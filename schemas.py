from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from config import settings

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

    image_file: str | None = Field(default=None, exclude=True)
    
    @computed_field
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

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


# ---------------- PASSWORD RECOVERY SCHEMAS ---------------- #

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# ---------------- PAGINATION SCHEMAS ---------------- #
    
class PaginatedPostResponse(BaseModel):
    items: list[PostResponse]
    total: int
    limit: int
    offset: int