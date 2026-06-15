import os
import uuid
from io import BytesIO

import boto3
from PIL import Image, ImageOps
from starlette.concurrency import run_in_threadpool
from fastapi import UploadFile, HTTPException, status

from config import settings

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB Limit


def _get_s3_client():
    """
    Initializes a boto3 S3 client using configuration settings.
    Handles Pydantic SecretStr evaluation cleanly.
    """
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
        endpoint_url=settings.s3_endpoint_url,
    )


def validate_and_read_image(file: UploadFile) -> str:
    """
    Validates file extension type limits before proceeding.
    Returns the clean lowercase extension string if valid.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    """
    Applies production optimization filters to raw image bytes:
    1. Corrects mobile camera orientation rotations (exif_transpose).
    2. Dynamically center-crops into a 300x300 square canvas (LANCZOS).
    3. Flattens transparency alpha-channels into clean RGB vectors.
    4. Compresses output into highly optimized 85% quality progressive JPEGs.
    """
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"

        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)

    return output.read(), filename


def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    """
    Synchronous boto3 file upload engine.
    """
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )


def _delete_from_s3(key: str) -> None:
    """
    Synchronous boto3 object removal engine.
    """
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)


async def save_profile_picture(file: UploadFile) -> str:
    """
    FastAPI high-level endpoint handler wrapper:
    Reads incoming stream, validates, runs PIL optimizations in a separate 
    threadpool worker, and ships the resulting bytes directly to S3.
    """
    validate_and_read_image(file)
    
    # Read raw bytes up to limit boundaries
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum limit of 5 Megabytes."
        )

    # Process image processing inside threadpool to prevent main loop blocking
    try:
        file_bytes, filename = await run_in_threadpool(process_profile_image, content)
        
        # Ship to Amazon S3 bucket instance
        key = f"profile_pics/{filename}"
        await run_in_threadpool(_upload_to_s3, file_bytes, key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing or storing the image cloud asset."
        )

    return filename


async def delete_old_profile_picture(filename: str | None) -> None:
    """
    Asynchronously deletes a cloud object from the bucket destination space.
    """
    if filename is None or not filename.strip():
        return
    key = f"profile_pics/{filename}"
    try:
        await run_in_threadpool(_delete_from_s3, key)
    except Exception:
        # Pass silently to ensure backend logic doesn't interrupt core transactions
        pass