from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from backend.app.api.main import router
from backend.app.core.config import settings
from contextlib import asynccontextmanager
from backend.app.core.database import init_db, engine
from backend.app.core.logging import get_logger
from backend.app.core.health import health_checker, ServiceStatus
import asyncio
import time

logger = get_logger()

async def startup_health_check(timeout: float=90.0) -> bool:
    try:
        async with asyncio.timeout(timeout):
            retry_interval = [1,2,5,10,15]
            start_time = time.time()

            while True:
                is_healthy = await health_checker.wait_for_services()
                if is_healthy:
                    return True
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    logger.error("services failed health check duroing startup")
                    return False
                
                wait_time = retry_interval[min(len(retry_interval)-1, int(elapsed_time/10))]
                logger.warning(f"Services not healthy yet, retrying in {wait_time} seconds...")

                await asyncio.sleep(wait_time)

    except asyncio.TimeoutError:
        logger.error(f"Health check timed out after {timeout} during startup")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}")
        return False



@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Database initialized successfully.")

        await health_checker.add_service("database", health_checker.check_database)
        await health_checker.add_service("celery", health_checker.check_celery)
        await health_checker.add_service("redis", health_checker.check_redis)

        if not await startup_health_check():
            raise RuntimeError("One or more services failed health check during startup")
        logger.info("All services are healthy. Application startup complete.")
        yield
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        await engine.dispose()
        await health_checker.cleanup()
        raise
    finally:
        logger.info("Shutting down application...")
        await engine.dispose()
        await health_checker.cleanup()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.get("/health", response_model=dict, tags=["Health"])
async def health_check():
    try:
        statuses = await health_checker.check_all_services()

        if statuses["status"] == ServiceStatus.HEALTHY:
            status_code = status.HTTP_200_OK
        elif statuses["status"] == ServiceStatus.DEGRADED:
            status_code = status.HTTP_206_PARTIAL_CONTENT
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(status_code=status_code, content=statuses)   
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": ServiceStatus.UNHEALTHY, 
                "error": str(e)
            }
        )


app.include_router(router, prefix=settings.API_V1_STR)
