from fastapi import FastAPI
from contextlib import asynccontextmanager

from configs.logger import get_custom_logger

from db.get_mongo_client import get_mongo_client

from routes.endpoints import router as EndpointsRouter
from routes.test_generation import router as TestEndpointRouter
from routes.api_doc_generation import router as APIDocsRouter

logger = get_custom_logger(__name__)

mongo_client = get_mongo_client()
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI backend started successfully!")
    try:
        mongo_client.ping()
    except Exception as e:
        logger.error(f"❌ MongoDB ping failed at startup: {e}")
    yield
    mongo_client.close()
    logger.error("FastAPI backend shutting down...")

app = FastAPI(title="APIDoc", lifespan=lifespan)

@app.get("/")
async def root():
    logger.info("/ accessed")
    return {"message": "Welcome to the API documentation!"}

app.include_router(EndpointsRouter, prefix="/api", tags=["GET API Endpoints"])
app.include_router(TestEndpointRouter, prefix="/api/test")
app.include_router(APIDocsRouter, prefix="/api/docs", tags=["API Documentation"])