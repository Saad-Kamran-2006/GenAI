from sqlmodel import SQLModel, Field
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from pydantic import BaseModel


# ? Step-4: Create Model
# * Data Model:
# * Table Model:
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True, min_length=3, max_length=54)
    is_completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")


class Todo_Create(BaseModel):
    content: str


class Todo_Edit(BaseModel):
    content: str
    is_completed: bool


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str


class Register_User(BaseModel):
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str


class RefreshTokenData(BaseModel):
    email: str
