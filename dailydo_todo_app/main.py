from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated
from contextlib import asynccontextmanager
from dailydo_todo_app.models import Todo, Token, User, Todo_Create, Todo_Edit
from dailydo_todo_app.auth import (
    authenticate_user,
    create_access_token,
    EXPIRY_TIME,
    current_user,
    validate_refresh_token,
    create_refresh_token,
)
from dailydo_todo_app.db import create_tables, get_session
from dailydo_todo_app.router.user import user_router
from datetime import timedelta


# ? Step-1: Create Database on Neon
# ? Step-2: Create .env file for environment variables
# ? Step-3: Create setting.py file for encrypting DatabaseURL
# ? Step-4: Create Model
# ? Step-5: Create connection string
# ? Step-6: Create Engine
# ? Step-7: Create function for table creation
# ? Step-8: Create function for session management
# ? Step-9: Create contex manager for app lifespan
# ? Step-10: Create all endpoints for todo app


# ? Step-9: Create contex manager for app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating Tables")
    create_tables()
    print("Tables Created")
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="dailyDo-Todo-App",
    version="1.0.0",
    servers=[
        {
            "url": "https://immensely-innocent-warthog.ngrok-free.app",
            "description": "Development Server",
        }
    ],
)

app.include_router(router=user_router)


# ? Step-10: Create all endpoints for todo app
@app.get("/")
async def root():
    return {"message": "Welcome to dailyDo todo app"}


# * Login: - username, password
@app.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub": form_data.username}, expire_time)
    refresh_expire_time = timedelta(days=7)
    refresh_token = create_refresh_token({"sub": user.email}, refresh_expire_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@app.post("/token/refresh")
def refresh_token(
    old_refresh_token: str,
    session: Annotated[Session, Depends(get_session)],
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, please login again",
        headers={"www-Authenticate": "Bearer"},
    )
    user = validate_refresh_token(old_refresh_token, session)
    if not user:
        raise credential_exception

    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub": user.username}, expire_time)
    refresh_expire_time = timedelta(days=7)
    refresh_token = create_refresh_token({"sub": user.email}, refresh_expire_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@app.post("/todos/", response_model=Todo)
async def create_todo(
    current_user: Annotated[User, Depends(current_user)],
    todo: Todo_Create,
    session: Annotated[Session, Depends(get_session)],
):
    new_todo = Todo(content=todo.content, user_id=current_user.id)

    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    return new_todo


@app.get("/todos/", response_model=list[Todo])
async def get_all(
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No task found")


@app.get("/todos/{id}", response_model=Todo)
async def get_single_todo(
    id: int,
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    mached_todo = next((todo for todo in user_todo if todo.id == id), None)
    if mached_todo:
        return mached_todo
    else:
        raise HTTPException(status_code=404, detail="No Task found")


@app.put("/todos/{id}")
async def edit_todo(
    id: int,
    todo: Todo_Edit,
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    existing_todo = next((todo for todo in user_todo if todo.id == id), None)

    if existing_todo:
        existing_todo.content = todo.content
        existing_todo.is_completed = todo.is_completed
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        raise HTTPException(status_code=404, detail="No task found")


@app.delete("/todos/{id}")
async def delete_todo(
    id: int,
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    user_todo = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    todo = next((todo for todo in user_todo if todo.id == id), None)
    if todo:
        session.delete(todo)
        session.commit()
        return {"message": "Task successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="No task found")
