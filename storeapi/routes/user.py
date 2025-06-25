from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from typing import Annotated
from storeapi.models.user import  UserIn
from storeapi.security import get_user, get_password_hash,authenticate_user, create_access_token,get_subject_from_token, create_confirmation_token
from storeapi.database import database, user_table
import logging
from fastapi.security import OAuth2PasswordRequestForm
from storeapi import tasks

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this email")
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password, confirmed=False)
    logger.debug(query)
    await database.execute(query)
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_link= request.url_for(
                "confirm_email", token=create_confirmation_token(user.email)
            ),
    )
    return {"message": "User registered successfully. Please confirm your email"}
            

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_from_token(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )
    
    logger.debug(query)
    await database.execute(query)
    return {"detail":"User confirmed"}
    