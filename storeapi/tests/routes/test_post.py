import pytest
from httpx import AsyncClient
from fastapi import status
from storeapi import security
from storeapi.tests.helpers import create_comment,create_post,like_post


@pytest.fixture()
def mock_generate_cute_creature_api(mocker):
    return mocker.patch(
        "storeapi.tasks._generate_cute_creature_api",
        return_value={"output_url":"http://example.net/image.jpeg"}
    )
    


@pytest.fixture()
async def created_comment(async_client:AsyncClient, created_post:dict, logged_in_token: str):
    return await create_comment("Test Comment", created_post.get("id"), async_client, logged_in_token)

# We don;t want to use our fixture when we're creating a post, we only want to use it when we're testing that requires a post to already exist

@pytest.mark.anyio
async def test_create_post(async_client:AsyncClient,confirmed_user:dict, logged_in_token: str):
    body = "Test Post"
    response = await async_client.post("/post", json={"body":body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == status.HTTP_201_CREATED
    assert {"id":1, "body":body, "user_id": confirmed_user["id"], "image_url":None}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_with_prompt(async_client:AsyncClient,logged_in_token:str, mock_generate_cute_creature_api):
    body = "Test Post"
    response = await async_client.post("/post?prompt=A cat", json={"body":body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == 201
    assert {"id": 1, "body": body,"image_url":None}.items() <= response.json().items()
    
    mock_generate_cute_creature_api.assert_called()



@pytest.mark.anyio
async def test_create_post_missing_dat(async_client:AsyncClient, logged_in_token: str):
    response = await async_client.post("/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
 
@pytest.mark.anyio
async def test_create_post_expired_token(async_client:AsyncClient, confirmed_user:dict,mocker):
    mocker.patch("storeapi.security.access_token_expired_minutes", return_value=-1) # Mocking the token to be expired
    token = security.create_access_token(confirmed_user["email"])
    response = await async_client.post("/post", json={"body":"Test Post"}, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token has expired"}
    
@pytest.mark.anyio
async def test_create_post_without_body(async_client:AsyncClient, logged_in_token: str):
    response = await async_client.post("/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.anyio
async def test_like_post(async_client:AsyncClient, created_post:dict, logged_in_token: str):
    response = await async_client.post("/like", json={"post_id":created_post.get("id")}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.anyio
async def test_get_all_post(async_client:AsyncClient, created_post:dict):
    response = await async_client.get("/post")
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    
    
@pytest.mark.anyio
# @pytest.mark.parametrize(
#     "sorting", "expected_order",
#     [
#         ("new", [2,1]),
#         ("old", [1,2])
#     ])
async def test_get_all_post_sorting(async_client:AsyncClient, logged_in_token:str):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    
    response = await async_client.get("/post", params={"sorting":"new"})
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    print("Data:", data)
    expected_order = [2,1]
    post_ids = [post["id"] for post in data]
    assert post_ids == expected_order
    
    
@pytest.mark.anyio
async def test_get_all_post_sort_likes(async_client:AsyncClient, logged_in_token:str):   
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    await like_post(async_client, 2, logged_in_token) 
    response = await async_client.get("/post", params={"sorting":"most_likes"})
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    post_ids = [post["id"] for post in data]
    expected_order = [2,1]
    assert post_ids == expected_order
    
    
@pytest.mark.anyio
async def test_get_all_post_wrong_sorting(async_client:AsyncClient, logged_in_token:str):
    response = await async_client.get("/post", params={"sorting":"wrong_sorting"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
@pytest.mark.anyio
async def test_create_comment(async_client:AsyncClient, created_post:dict, logged_in_token: str, confirmed_user:dict):
    body = "Test Comment"
    response = await async_client.post("/comment", json={"body":body,"post_id":created_post.get("id")}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
    assert response.status_code == status.HTTP_201_CREATED
    assert {"id":1, "body":body,"user_id": confirmed_user["id"] ,"post_id":created_post.get("id")}.items() <= response.json().items()
    
    
@pytest.mark.anyio
async def test_create_comment_without_post_id(async_client:AsyncClient, logged_in_token: str):
    body = "Test Comment"
    response = await async_client.post("/comment", json={"body":body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    
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
    assert response.json() == {"post": {**created_post, "likes":0}, "comments":[created_comment]}
    
    
@pytest.mark.anyio
async def test_get_missing_post_with_comments(async_client: AsyncClient, created_comment:dict, created_post:dict):
    response = await async_client.get("/post/9999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}