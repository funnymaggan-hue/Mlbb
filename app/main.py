from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database.base import Base
from app.database.session import engine
from app.routers.api import router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Local SQLite convenience; Railway runs Alembic before server startup.
    if "sqlite" in str(engine.url):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(title="MLBB Tournament Pro", version="1.0.0", lifespan=lifespan)
app.include_router(router)
@app.get("/health")
async def health(): return {"status":"ok"}
@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")
app.mount("/static", StaticFiles(directory="static"), name="static")
