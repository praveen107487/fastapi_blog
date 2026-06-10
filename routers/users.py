from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()


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


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing_user = (
        await db.execute(
            select(models.User).where(
                models.User.username == user.username
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
                models.User.email == user.email
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
        email=user.email,
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await get_user_or_404(user_id, db)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await get_user_or_404(user_id, db)

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

    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await get_user_or_404(user_id, db)

    await db.delete(user)

    await db.commit()

    return None