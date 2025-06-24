from fastapi import APIRouter, HTTPException, status, Form, Depends
from typing import Annotated
from storeapi.models.user import  UserIn
from storeapi.security import get_user, get_password_hash,authenticate_user, create_access_token
from storeapi.database import database, user_table
import logging
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this email")
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {"message": "User registered successfully"}

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}