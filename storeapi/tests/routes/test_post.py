import pytest
from httpx import AsyncClient
from fastapi import status

async def create_post(body:str, async_client: AsyncClient):
    response = await async_client.post("/post", json={"body":body})
    return response.json()

async def create_comment(body:str, post_id:int, async_client: AsyncClient):
    response = await async_client.post("/comment", json={"body":body, "post_id":post_id})
    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test Post", async_client)

@pytest.fixture()
async def created_comment(async_client:AsyncClient, created_post:dict):
    return await create_comment("Test Comment", created_post.get("id"), async_client)

# We don;t want to use our fixture when we're creating a post, we only want to use it when we're testing that requires a post to already exist

@pytest.mark.anyio
async def test_create_post(async_client:AsyncClient):
    body = "Test Post"
    response = await async_client.post("/post", json={"body":body})
    
    assert response.status_code == status.HTTP_201_CREATED
    # assert {"id":1, "body":body}.items() <= response.json().items()
    
@pytest.mark.anyio
async def test_create_post_without_body(async_client:AsyncClient):
    response = await async_client.post("/post", json={})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
@pytest.mark.anyio
async def test_get_all_post(async_client:AsyncClient, created_post:dict):
    response = await async_client.get("/post")
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    
@pytest.mark.anyio
async def test_create_comment(async_client:AsyncClient, created_post:dict):
    body = "Test Comment"
    response = await async_client.post("/comment", json={"body":body,"post_id":created_post.get("id")})
    
    assert response.status_code == status.HTTP_201_CREATED
    assert {"id":1, "body":body, "post_id":created_post.get("id")}.items() <= response.json().items()
    
    
@pytest.mark.anyio
async def test_create_comment_without_post_id(async_client:AsyncClient):
    body = "Test Comment"
    response = await async_client.post("/comment", json={"body":body})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
@pytest.mark.anyio
async def test_get_comments_on_post(async_client: AsyncClient, created_comment:dict, created_post:dict):
    response = await async_client.get(f"/post/{created_post.get('id')}/comment")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [created_comment]

@pytest.mark.anyio
async def test_get_comments_on_post_empty(async_client: AsyncClient, created_post:dict):
    response = await async_client.get(f"/post/{created_post.get('id')}/comment")
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient,created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post.get('id')}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"post": created_post, "comments":[created_comment]}
    
    
@pytest.mark.anyio
async def test_get_missing_post_with_comments(async_client: AsyncClient, created_comment:dict, created_post:dict):
    response = await async_client.get("/post/9999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}