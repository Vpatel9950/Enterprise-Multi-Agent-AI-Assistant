import uvicorn
import logging
import sys
import os

# Ensure project root is in sys.path so scripts can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.mongo import MongoDBManager
from app.routers import chat_router, rag_router, approval_router, agents_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("enterprise.ai.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Agent AI Service powered by LangGraph, MongoDB, and Qdrant RAG Engine.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router.router, prefix=settings.API_V1_STR)
app.include_router(rag_router.router, prefix=settings.API_V1_STR)
app.include_router(approval_router.router, prefix=settings.API_V1_STR)
app.include_router(agents_router.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing Enterprise AI Microservice...")
    try:
        is_alive = MongoDBManager.ping()
        if is_alive:
            logger.info("MongoDB primary connection verified successfully.")
            # Trigger setup script if empty
            from scripts.init_mongo import setup_indexes, seed_data
            db = MongoDBManager.get_database()
            setup_indexes(db)
            seed_data(db)
        else:
            logger.warning("MongoDB ping failed. Check MONGODB_URI in .env configuration.")
    except Exception as e:
        logger.warning(f"Startup MongoDB setup note: {e}")

@app.on_event("shutdown")
def on_shutdown():
    MongoDBManager.close()

@app.get("/health")
def health():
    mongo_ok = MongoDBManager.ping()
    from app.llm.gemini_client import is_gemini_available
    gemini_ok = is_gemini_available()
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "MongoDB 7.0 (Connected)" if mongo_ok else "MongoDB (Offline)",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.GEMINI_MODEL_NAME if settings.LLM_PROVIDER == "gemini" else "openai",
        "gemini_connected": gemini_ok
    }

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.AI_SERVICE_PORT, reload=True)
