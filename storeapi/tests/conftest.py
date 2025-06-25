import os
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport
os.environ["ENV_STATE"] = "test"
from storeapi.database import database, user_table #noqa: E402
from storeapi.main import app #noqa: E402 



@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app=app)
# fixed the issue of the test for registering a user failing due to the database not being cleared before each test run.
@pytest_asyncio.fixture(autouse=True)
async def clear_users():
    await database.execute(user_table.delete())
    
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()
    
@pytest_asyncio.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac
        
# Fixture for user that's not confirmed
@pytest_asyncio.fixture()
async def registered_user(async_client:AsyncClient) -> dict:
    user_details = {"email":"test@example.net", "password":"test1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details

# Fixture for user that's confirmed
@pytest_asyncio.fixture()
async def confirmed_user(registered_user:dict) -> dict:
    query = (user_table.update().where(user_table.c.email == registered_user["email"]).values(confirmed=True))
    await database.execute(query)
    return registered_user
    


@pytest.fixture()
async def logged_in_token(async_client:AsyncClient, confirmed_user:dict) -> str:
    response = await async_client.post("/token", data={"username": confirmed_user["email"], "password": confirmed_user["password"]})
    assert response.status_code == 200, f"Failed to log in: {response.text}"
    return response.json()["access_token"]