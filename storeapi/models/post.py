from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserPostIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    body: str
    
class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id:int
    user_id: int
    image_url : Optional[str] = None
    
class UserPostWithLikes(UserPost):
    model_config = ConfigDict(from_attributes=True)
    
    likes:int
    
class CommentIn(BaseModel):
    body: str
    post_id: int
    
class Comment(CommentIn):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    
class UserPostWithComments(BaseModel):
    post: UserPostWithLikes
    comments: list[Comment]
    
class PostLikeIn(BaseModel):
    post_id: int
    
class PostLike(PostLikeIn):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int