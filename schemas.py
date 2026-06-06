from pydantic import BaseModel, ConfigDict, Field


class Author(BaseModel):
    id: int
    username: str
    image_path: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: Author


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str