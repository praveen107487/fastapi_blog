from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostResponse, PostCreate

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(url_for=templates.env.globals.get("url_for"))

posts = [
    {
        "id": 1,
        "author": {
            "id": 1,
            "username": "Corey Schafer",
            "image_path": "/static/profile_pics/default.jpg"
        },
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
        "user_id": 1
    },
    {
        "id": 2,
        "author": {
            "id": 2,
            "username": "Jane",
            "image_path": "/static/profile_pics/default.jpg"
        },
        "title": "Python is Awesome",
        "content": "Python works great with FastAPI.",
        "date_posted": "April 21, 2025",
        "user_id": 2
    },
]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "posts": posts,
            "title": "Home",
        }
    )


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate):

    new_id = max(p["id"] for p in posts) + 1 if posts else 1

    new_post = {
        "id": new_id,
        "author": post.author.model_dump(),
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
        "user_id": post.author.id
    }

    posts.append(new_post)

    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):

    for post in posts:
        if post["id"] == post_id:
            return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):

    for post in posts:
        if post["id"] == post_id:

            title = post["title"][:50]

            return templates.TemplateResponse(
                request=request,
                name="post.html",
                context={
                    "post": post,
                    "title": title
                }
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException
):

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please try again."
    )

    if request.url.path.startswith("/api"):

        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message
        },
        status_code=exception.status_code
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request,
    exception: RequestValidationError
):

    if request.url.path.startswith("/api"):

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()}
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )