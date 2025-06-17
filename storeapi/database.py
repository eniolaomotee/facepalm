import databases
import sqlalchemy
from storeapi.config import config

metadata =sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("body", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("post_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"), nullable=False)
    
)


engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} 
)

metadata.create_all(engine)
database = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK)