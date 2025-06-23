import logging
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from storeapi.database import database, user_table
import datetime
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, status, Depends
from typing import Annotated

logger = logging.getLogger(__name__)
# when you work on a backend api you look at 3 main things a.data to be stored b. data the api is going to recieve and c.return and implement the endpoint to the user.

SECRET_KEY="9d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7"
ALGORITHM="HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate Credentials",
    headers={"WWW-Authenticate": "Bearer"},
    
)

def access_token_expired_minutes() ->int:
    return 30

def create_access_token(email:str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expired_minutes())
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(email:str):
    logger.debug("Fetching user from db", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result
    
    
async def authenticate_user(email:str,password:str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user.password):
        raise credentials_exception
    return user

async def get_current_user(token:Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e
    
    user = await get_user(email)
    if user is None:
        raise credentials_exception
    return user