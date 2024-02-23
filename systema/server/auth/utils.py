from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from systema.management import settings

from ..db import engine
from .models import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_superuser(username: str, password: str):
    with Session(engine) as session:
        user = User(
            username=username,
            hashed_password=get_hash(password),
            superuser=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        password=plain_password.encode(),
        hashed_password=hashed_password.encode(),
    )


def get_hash(password: str):
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    ).decode()


def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub", "")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username or "")
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.active:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a superuser")
