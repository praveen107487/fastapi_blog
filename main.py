from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from routers import post, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# ==========================================
#              STATIC FILES
# ==========================================

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# ==========================================
#             TEMPLATE ENGINE
# ==========================================

templates = Jinja2Templates(directory="templates")


def format_datetime(value, format_str="%b %d, %Y at %I:%M %p"):
    """
    Formatting filter for cleaner timestamps in HTML views.
    """
    if not value:
        return ""

    if isinstance(value, datetime):
        return value.strftime(format_str)

    try:
        if " " in str(value) or "T" in str(value):
            dt = datetime.fromisoformat(str(value))
        else:
            dt = datetime.strptime(str(value), "%H:%M:%S.%f")
            return dt.strftime("%I:%M %p")

        return dt.strftime(format_str)

    except ValueError:
        return str(value)


templates.env.filters["datetimeformat"] = format_datetime

# ==========================================
#                ROUTERS
# ==========================================

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"],
)

app.include_router(
    post.router,
    prefix="/api/posts",
    tags=["Posts"],
)

# ==========================================
#            HTML FRONTEND PAGES
# ==========================================


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post).options(
            selectinload(models.Post.author)
        )
    )

    posts_db = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "posts": posts_db,
            "title": "Home",
        },
    )

@app.get("/account", include_in_schema=False, name="account_page")
async def account_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"title": "Account Settings"}
    )

@app.get(
    "/posts/{post_id}",
    include_in_schema=False,
    name="post_page",
)
async def post_page(
    request: Request,
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(joinedload(models.Post.author))
        .where(models.Post.id == post_id)
    )

    post_data = result.scalars().first()

    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="post.html",
        context={
            "post": post_data,
            "title": post_data.title[:50],
        },
    )


@app.get(
    "/users/{user_id}/posts",
    include_in_schema=False,
    name="user_posts",
)
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = (
        await db.execute(
            select(models.User).where(
                models.User.id == user_id
            )
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    posts_db = (
        await db.execute(
            select(models.Post)
            .options(joinedload(models.Post.author))
            .where(models.Post.user_id == user_id)
        )
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


@app.get("/login", include_in_schema=False, name="login_page")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Login"
        }
    )


@app.get("/register", include_in_schema=False, name="register_page")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "title": "Register"
        }
    )


# Added fallback named route to prevent template execution runtime errors
@app.get("/forgot-password", include_in_schema=False, name="forgot_password_page")
async def forgot_password_page(request: Request):
    return JSONResponse(content={"detail": "Password reset page coming soon."})


# ==========================================
#         GLOBAL EXCEPTION HANDLERS
# ==========================================


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
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
async def validation_exception_handler(
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