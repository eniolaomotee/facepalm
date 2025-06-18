from fastapi import APIRouter, HTTPException, status
from storeapi.models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments
from storeapi.database import database, post_table, comment_table
import logging
router = APIRouter()


logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding post with ID: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)

@router.post("/post", response_model=UserPost, status_code=status.HTTP_201_CREATED)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    
    logger.debug(query)
    
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(comment:CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with ID {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")
    
    data = comment.model_dump()
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comment(post_id: int):
    logger.info("Getting post with ID")
    post = await find_post(post_id)
    if not post:
        logger.error(f"Post with ID {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id)
    }