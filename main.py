from datetime import datetime, UTC
from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from schemas import (
    PostResponse,
    PostCreate,
    UserResponse,
    UserCreate,
    UserPublic,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts_db = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"posts": posts_db, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False, name="post_page")
def post_page(
    request: Request,
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="post.html",
        context={
            "post": post,
            "title": post.title[:50],
        },
    )


@app.get(
    "/users/{user_id}/posts",
    include_in_schema=False,
    name="user_posts",
)
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    posts_db = db.execute(
        select(models.Post)
        .options(joinedload(models.Post.author))
        .where(models.Post.user_id == user_id)
    ).scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="user_posts.html",
        context={
            "user": user,
            "posts": posts_db,
            "title": f"{user.username}'s Posts",
        },
    )


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.execute(
        select(models.User).where(
            models.User.username == user.username
        )
    ).scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = db.execute(
        select(models.User).where(
            models.User.email == user.email
        )
    ).scalars().first()

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
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/api/user/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: PostCreate,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(models.User).where(models.User.id == post.user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    post = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    ).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@app.get(
    "/api/users/{user_id}/posts",
    response_model=list[PostResponse],
)
def get_user_posts(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    posts = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    ).scalars().all()

    return posts


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )