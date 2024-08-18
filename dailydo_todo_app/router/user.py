from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlmodel import Session
from dailydo_todo_app.models import Register_User, User
from dailydo_todo_app.auth import get_user_from_db, hash_password, oauth_scheme, current_user
from dailydo_todo_app.db import get_session

user_router = APIRouter(
    prefix="/user", tags=["user"], responses={404: {"description": "Not Found"}}
)


@user_router.get("/")
async def read_user():
    return {"message": "Welcome to dailyDo todo app user's page"}


@user_router.post("/register")
async def register_user(
    new_user: Annotated[Register_User, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        HTTPException(
            status_code=409, detail="User with these credientials already exist"
        )
    user = User(
        username=new_user.username,
        email=new_user.email,
        password=hash_password(new_user.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f"User with {user.username} successfully registered"}


@user_router.get("/me")
async def user_profile(current_user: Annotated[User, Depends(current_user)]):
    return current_user
