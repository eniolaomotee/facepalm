from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport
from storeapi.main import app
from storeapi.routes.post import comment_table, post_table


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app=app)
    
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    comment_table.clear()
    post_table.clear()
    yield
    
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac