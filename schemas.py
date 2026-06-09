from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ---------------- USERS ---------------- #


class UserBase(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    email: EmailStr | None = None

    image_file: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None = None
    image_path: str | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_path: str | None = None


# ---------------- POSTS ---------------- #


class PostBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
    )

    content: str = Field(
        min_length=1,
    )


class PostCreate(PostBase):
    user_id: int


class PostUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    content: str | None = Field(
        default=None,
        min_length=1,
    )


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic