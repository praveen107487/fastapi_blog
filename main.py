from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
app=FastAPI()

templates=Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "Fastapi is Awesome",
        "content": "This is the framework that is really easy to use and super fast",
        "date_posted": "April 20,2025"
    },
    {
        "id": 2,
        "author": "Jane",
        "title": "Python is Awesome",
        "content": "Python for Fastapi",
        "date_posted": "April 20,2025"
    },
]
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request,"home.html",{"posts":posts,"title":"Home"})


@app.get("/posts")
def get_posts():
    return posts