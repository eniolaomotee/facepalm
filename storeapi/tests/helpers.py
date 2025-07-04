from httpx import AsyncClient


async def create_post(body:str, async_client: AsyncClient, logged_in_token:str):
    response = await async_client.post("/post", json={"body":body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

async def create_comment(body:str, post_id:int, async_client: AsyncClient, logged_in_token:str):
    response = await async_client.post("/comment", json={"body":body, "post_id":post_id}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

async def like_post(async_client:AsyncClient, post_id:int, logged_in_token:str) ->dict:
    response = await async_client.post("/like", json={"post_id": post_id}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()
