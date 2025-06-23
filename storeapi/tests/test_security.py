
import pytest
from storeapi import security
from jose import jwt

def test_access_token_expired_minutes():
    assert security.access_token_expired_minutes() == 30
    
def test_create_access_token():
    token = security.create_access_token("123")
    
    assert {"sub":"123"}.items() <= jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM]).items()


def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))

@pytest.mark.anyio
async def test_get_user(registered_user:dict):
    user = await security.get_user(registered_user["email"])
    
    assert user.email == registered_user["email"]
   
@pytest.mark.anyio
async def test_user_not_found():
    user = await security.get_user("test@example.com")
    
    assert user is None
    
@pytest.mark.anyio
async def test_authenticate_user(registered_user:dict):
    user = await security.authenticate_user(registered_user["email"], registered_user["password"])
    
    assert user.email == registered_user["email"]
    
    
@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net", "test1234")
        
@pytest.mark.anyio
async def test_authenticate_wrong_password(registered_user:dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrong password")
    
@pytest.mark.anyio
async def test_authenticate_wrong_email(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("wrong email", registered_user["password"])