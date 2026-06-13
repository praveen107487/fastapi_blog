from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------- USERS ---------------- #

class UserBase(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=16)

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

class Token(BaseModel):
    access_token: str
    token_type: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_path: str | None = None

class UserPrivate(UserPublic):
    email: EmailStr


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
class UpdatePasswordSchema(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=16)
    
class PaginatedPostResponse(BaseModel):
    items: list[PostResponse]
    total: int
    limit: int
    offset: int