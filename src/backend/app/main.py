from fastapi import FastAPI
from app.api.main import router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(router, prefix=settings.API_V1_STR)


# app.get("/health", tags=["Health"])(lambda: {"status": "ok"})
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}