import logging
from fastapi import  FastAPI
from storeapi.routes.post import router as post_router
from contextlib import asynccontextmanager
from storeapi.database import database
from storeapi.logging_conf import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    configure_logging()
    logger.info("Hello wolrd")
    await database.connect()
    yield
    await database.disconnect()




app = FastAPI(lifespan=lifespan)

app.include_router(post_router, tags=["Post"])