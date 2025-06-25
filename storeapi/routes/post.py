from fastapi import APIRouter, HTTPException, status, Depends
from storeapi.models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments, PostLike, PostLikeIn, UserPostWithLikes
from storeapi.database import database, post_table, comment_table, like_table
import logging
from storeapi.models.user import User
from storeapi.security import get_current_user, oauth2_scheme
from typing import Annotated
import sqlalchemy
from enum import Enum


router = APIRouter()


logger = logging.getLogger(__name__)

select_post_and_likes = sqlalchemy.select(
    post_table, sqlalchemy.func.count(like_table.c.id).label("likes")
).select_from(post_table.outerjoin(like_table)).group_by(post_table.c.id)


async def find_post(post_id: int):
    logger.info(f"Finding post with ID: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)

@router.post("/post", response_model=UserPost, status_code=status.HTTP_201_CREATED)
async def create_post(post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]):
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"
    

@router.get("/post", response_model=list[UserPostWithLikes])
async def get_posts(sorting: PostSorting = PostSorting.new):
    logger.info("Getting all posts")
    
    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
        
    logger.debug(query)
    
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(comment:CommentIn,current_user: Annotated[User, Depends(get_current_user)]):

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    data = {**comment.model_dump(), "user_id": current_user.id}
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
    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post = await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id)
    }
    
@router.post("/like", status_code=status.HTTP_201_CREATED, response_model=PostLike)
async def get_likes_on_post(like:PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Liking post")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = {**like.model_dump(), "user_id": current_user.id}
    query = like_table.insert().values(data)
    logger.debug(query)
    
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}