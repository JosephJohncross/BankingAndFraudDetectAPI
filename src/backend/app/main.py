from fastapi import FastAPI
from app.api.main import router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # Cleanup actions can be added here if necessary

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(router, prefix=settings.API_V1_STR)


# app.get("/health", tags=["Health"])(lambda: {"status": "ok"})
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}