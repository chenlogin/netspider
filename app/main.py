import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.database import engine
from app.models.company import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nothing special


app = FastAPI(title="NetSpider", version="1.0.0", lifespan=lifespan)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Mount API routes
from app.routers.companies import router as companies_router
app.include_router(companies_router)


@app.get("/")
async def index():
    from fastapi.responses import FileResponse
    return FileResponse(str(BASE_DIR / "static" / "index.html"))
