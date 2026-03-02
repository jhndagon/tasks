from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.config.env import get_settings
from app.infrastructure.http.rest.routes import router as api_router
from app.infrastructure.persistence.sqlalchemy.database import close_db, init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Tasks Microservice", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
