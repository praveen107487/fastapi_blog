from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db
from schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
)

router = APIRouter()


async def get_post_or_404(
    post_id: int,
    db: AsyncSession,
) -> models.Post:
    post = (
        await db.execute(
            select(models.Post)
            .options(joinedload(models.Post.author))
            .where(models.Post.id == post_id)
        )
    ).scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


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
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await get_user_or_404(post.user_id, db)

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
        date_posted=datetime.now(UTC),
    )

    db.add(new_post)

    await db.commit()

    created_post = await get_post_or_404(new_post.id, db)

    return created_post


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await get_post_or_404(post_id, db)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post = await get_post_or_404(post_id, db)

    if post.user_id != post_data.user_id:
        await get_user_or_404(post_data.user_id, db)

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()

    updated_post = await get_post_or_404(post_id, db)

    return updated_post


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post = await get_post_or_404(post_id, db)

    update_data = post_data.model_dump(exclude_unset=True)

    if "user_id" in update_data:
        await get_user_or_404(update_data["user_id"], db)

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()

    updated_post = await get_post_or_404(post_id, db)

    return updated_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post = await get_post_or_404(post_id, db)

    await db.delete(post)

    await db.commit()

    return None


@router.get(
    "/user/{user_id}",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10,
    offset: int = 0,
):
    await get_user_or_404(user_id, db)

    posts = (
        await db.execute(
            select(models.Post)
            .options(joinedload(models.Post.author))
            .where(models.Post.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    return posts