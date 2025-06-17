from pydantic import BaseModel, ConfigDict



class UserPostIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    body: str
    
class UserPost(UserPostIn):
    id:int
    
class CommentIn(BaseModel):
    body: str
    post_id: int
    
class Comment(CommentIn):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    
class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]