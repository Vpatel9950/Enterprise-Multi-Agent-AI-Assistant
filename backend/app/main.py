import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.seed import seed_database
from app.routers import (
    auth_router,
    agent_router,
    chat_router,
    rag_router,
    workflow_router,
    integration_router,
    admin_router,
    external_api_router
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Agent AI Assistant REST API Platform featuring RAG Knowledge Retrieval, Workflow Automations, and External Tool Integrations.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(agent_router.router, prefix=settings.API_V1_STR)
app.include_router(chat_router.router, prefix=settings.API_V1_STR)
app.include_router(rag_router.router, prefix=settings.API_V1_STR)
app.include_router(workflow_router.router, prefix=settings.API_V1_STR)
app.include_router(integration_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR)
app.include_router(external_api_router.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_database()

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "message": "Enterprise Multi-Agent AI Platform is running."
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
