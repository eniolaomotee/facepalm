from fastapi import APIRouter, HTTPException, status
from storeapi.models.user import User, UserIn
from storeapi.security import get_user
from storeapi.database import database, user_table
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this email")
    query = user_table.insert().values(email=user.email, password=user.password)
    
    logger.debug(query)
    await database.execute(query)
    return {"message": "User registered successfully"}
