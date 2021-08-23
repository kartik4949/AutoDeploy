
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from security.model import User, UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

'''
Some fake users. These should be in a database
'''
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def get_user(db, username: str):
  if username in db:
    user_dict = db[username]
    return UserInDB(**user_dict)


def fake_decode_token(token):
  # This doesn't provide any security at all
  # Check the next version
  user = get_user(fake_users_db, token)
  return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
  user = fake_decode_token(token)
  if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
  return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user

def fake_hash_password(password: str):
  return password


def get_user(db, username: str):
  if username in db:
    user_dict = db[username]
    return UserInDB(**user_dict)


def fake_decode_token(token):
  # This doesn't provide any security at all
  # Check the next version
  user = get_user(fake_users_db, token)
  return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
  user = fake_decode_token(token)
  if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
  return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user
