import os
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas import UserCreate, UserPublic, UserPrivate, UserUpdate, Token, UpdatePasswordSchema
from auth import creat_acces_token, hash_password, oauth2_scheme, verify_password, verify_acces_token

router = APIRouter()

UPLOAD_DIR = "media/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def get_user_or_404(
    user_id: int,
    db: AsyncSession,
) -> models.User:
    user = (
        await db.execute(
            select(models.User).where(
                models.User.id == user_id
            )
        )
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> models.User:
    email = verify_acces_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = (
        await db.execute(
            select(models.User).where(func.lower(models.User.email) == email.lower())
        )
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found"
        )
    return user


@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing_user = (
        await db.execute(
            select(models.User).where(
                func.lower(models.User.username) == user.username.lower()
            )
        )
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = (
        await db.execute(
            select(models.User).where(
                func.lower(models.User.email) == user.email.lower()
            )
        )
    ).scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.User).where(func.lower(models.User.email) == form_data.username.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = creat_acces_token(data={"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def update_password(
    data: UpdatePasswordSchema,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password verification context."
        )
    current_user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"detail": "Password modified successfully."}


@router.patch("/{user_id}/picture", response_model=UserPrivate)
async def update_profile_picture(
    user_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action context.")
    
    ext = os.path.splitext(file.filename)[1]
    if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format asset pattern.")

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    current_user.image_file = unique_filename
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await get_user_or_404(user_id, db)


@router.patch(
    "/{user_id}",
    response_model=UserPrivate,
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Forbidden.")

    user = current_user

    if (
        user_update.username is not None
        and user_update.username != user.username
    ):
        existing_user = (
            await db.execute(
                select(models.User).where(
                    models.User.username == user_update.username
                )
            )
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        user.username = user_update.username

    if (
        user_update.email is not None
        and user_update.email != user.email
    ):
        existing_email = (
            await db.execute(
                select(models.User).where(
                    models.User.email == user_update.email
                )
            )
        ).scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        user.email = user_update.email

    await db.commit()
    await db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Forbidden.")

    await db.delete(current_user)
    await db.commit()
    return None