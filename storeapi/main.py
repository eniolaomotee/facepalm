import logging
from fastapi import  FastAPI,HTTPException
from storeapi.routes.post import router as post_router
from storeapi.routes.user import router as user_router
from contextlib import asynccontextmanager
from storeapi.database import database
from storeapi.logging_conf import configure_logging
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    configure_logging()
    logger.info("Hello wolrd")
    await database.connect()
    yield
    await database.disconnect()




app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(post_router, tags=["Post"])
app.include_router(user_router, tags=["User"])




@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTPException:{exc.status_code} {exc.detail}")
    return await http_exception_handler(request=request, exc=exc) 