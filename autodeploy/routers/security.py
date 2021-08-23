
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from security.scheme import oauth2_scheme, fake_users_db, get_user, fake_decode_token, fake_hash_password
from schema.security import User, UserInDB

router = APIRouter(
    prefix="/token",
    tags=["security"],
    responses={}
)

@router.post("/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  user_dict = fake_users_db.get(form_data.username)
  if not user_dict:
    raise HTTPException(status_code=400, detail="Incorrect username or password")
  user = UserInDB(**user_dict)
  hashed_password = fake_hash_password(form_data.password)
  if not hashed_password == user.hashed_password:
    raise HTTPException(status_code=400, detail="Incorrect username or password")

  return {"access_token": user.username, "token_type": "bearer"}
