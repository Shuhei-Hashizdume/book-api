from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from security import decode_access_token

SessionDep = Annotated[Session, Depends(get_db)]
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: SessionDep,
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
        statement = select(User).where(User.id == user_id)
        user = db.scalar(statement)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証情報を確認できませんでした。",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報を確認できませんでした。",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUserDep) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作を行う権限がありません。",
        )
    return current_user


AdminUserDep = Annotated[User, Depends(get_current_admin)]
