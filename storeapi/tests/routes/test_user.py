import pytest
from httpx import AsyncClient
from fastapi import status, Request
from storeapi import security

async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post("/register", json={"email":email, "password": password})

@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "password123")
    
    assert response.status_code == 201
    assert "User registered successfully" in response.text
    
    
@pytest.mark.anyio
async def test_register_user_already_exists(async_client:AsyncClient, registered_user:dict):
    response = await register_user(async_client, registered_user["email"], registered_user["password"])
    
    assert response.status_code == 400
    assert "User already exists" in response.text

@pytest.mark.anyio
async def test_confirm_user(async_client:AsyncClient, mocker):
    await register_user(async_client, "test@example.com", "password123")
    
    token = security.create_access_token("test@example.com")
    response = await async_client.get(f"/confirm/{token}")
    
    assert response.status_code == 200
    assert "User confirmed" in response.text
    
@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client:AsyncClient):
    response = await async_client.get("/confirm/invalid_token")
    
    assert response.status_code == 401
    assert "Invalid token" in response.text

@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client:AsyncClient, mocker):
    mocker.patch("storeapi.security.confirm_token_expired_minutes", return_value=-1)
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "test@example.com", "password123")
    
    confirmation_url = str(spy.spy_return)
    response = await async_client.get(confirmation_url)
    
    assert response.status_code == 401
    assert "Token has expired" in response.text


@pytest.mark.anyio
async def test_login_user_not_exists(async_client:AsyncClient):
    response = await async_client.post("/token", data={"username":"test@example.com", "password":"password123"})
    assert  response.status_code == status.HTTP_401_UNAUTHORIZED  
    
    
@pytest.mark.anyio
async def test_login_user_not_confirmed(async_client:AsyncClient, registered_user:dict):
    response = await async_client.post("/token", data={"username":registered_user["email"], "password": registered_user["password"]})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
@pytest.mark.anyio
async def test_login_user(async_client:AsyncClient, confirmed_user:dict):
    response = await async_client.post("/token", data={"username":confirmed_user["email"], "password": confirmed_user["password"]})

    assert  response.status_code == 200