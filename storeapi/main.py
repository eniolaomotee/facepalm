import logging
from fastapi import  FastAPI,HTTPException
from storeapi.routes.post import router as post_router
from storeapi.routes.user import router as user_router
from storeapi.routes.upload import router as upload_router
from contextlib import asynccontextmanager
from storeapi.database import database
from storeapi.logging_conf import configure_logging
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware
from storeapi.config import config
import sentry_sdk


sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)

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
app.include_router(upload_router, tags=["File Upload"])



@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTPException:{exc.status_code} {exc.detail}")
    return await http_exception_handler(request=request, exc=exc) 