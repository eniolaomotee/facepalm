import logging
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from storeapi.database import database, user_table
import datetime
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, status, Depends
from typing import Annotated,Literal

logger = logging.getLogger(__name__)
# when you work on a backend api you look at 3 main things a.data to be stored b. data the api is going to recieve and c.return and implement the endpoint to the user.

SECRET_KEY="9d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7"
ALGORITHM="HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_credentials_exception(detail:str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )



def access_token_expired_minutes() ->int:
    return 30


def confirm_token_expired_minutes() ->int:
    return 1440



def create_access_token(email:str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expired_minutes())
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_confirmation_token(email:str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=confirm_token_expired_minutes())
    jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_subject_from_token(token: str, type:Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        raise create_credentials_exception("Invalid token") from e
    
    email = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing in sub field")
    token_type = payload.get("type")
    if token_type is None or token_type != "access":
        raise create_credentials_exception("Token has incorrect type")
    return email
    

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
        raise create_credentials_exception("Invalid email or password")
    if not verify_password(password, user.password):
        raise create_credentials_exception("Invalid email or password")
    if not user.confirmed:
        raise create_credentials_exception("User is not confirmed")
    return user

async def get_current_user(token:Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_from_token(token, "access")
    user = await get_user(email)
    if user is None:
        raise create_credentials_exception("Could not find user for this token")
    return user