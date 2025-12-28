from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import router
from app.config import APP_NAME, VERSION
from app.database import engine
from app.db_models import Base
from app.logger import logger

app = FastAPI(title=APP_NAME, version=VERSION)

Base.metadata.create_all(bind=engine)

app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong. Please contact support."
        }
    )


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "CovenantGuard+ Backend",
        "version": VERSION
    }
