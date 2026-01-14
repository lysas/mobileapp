from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import mcq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting up...")
    try:
        yield
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Server interrupt caught (CancelledError/KeyboardInterrupt).")
    finally:
        logger.info("Server shutting down...")

app = FastAPI(title="MCQ Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_interruptions(request: Request, call_next):
    try:
        return await call_next(request)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("Request interrupted (CancelledError/KeyboardInterrupt).")
        return JSONResponse(status_code=499, content={"detail": "Interrupted"})

app.include_router(mcq.router)

@app.get("/")
def root():
    return {"status": "online"}
