import logging
from passlib.context import CryptContext
from storeapi.database import database, user_table
from storeapi import config
import datetime
from jose import jwt
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)
# when you work on a backend api you look at 3 main things a.data to be stored b. data the api is going to recieve and c.return and implement the endpoint to the user.

SECRET_KEY="9d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate Credentials",
    
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