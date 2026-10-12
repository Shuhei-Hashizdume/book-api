from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import CurrentUserDep, SessionDep
from models import User
from schemas.users import LoginResponse, UserCreate, UserLogin, UserResponse
from security import create_access_token, hash_password, verify_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user_data: UserCreate, db: SessionDep):
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hashed_password,
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="同じユーザー名またはメールアドレスが既に登録されています。",
        )

    db.refresh(new_user)
    return new_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(current_user: CurrentUserDep, db: SessionDep):

    db.delete(current_user)
    db.commit()


@router.post("/login", response_model=LoginResponse)
def login_user(user_login: UserLogin, db: SessionDep):
    statement = select(User).where(User.email == user_login.email)
    user = db.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスもしくは、パスワードが異なります。",
        )

    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスもしくは、パスワードが異なります。",
        )

    access_token = create_access_token(user.id)
    return LoginResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: CurrentUserDep):
    return current_user
