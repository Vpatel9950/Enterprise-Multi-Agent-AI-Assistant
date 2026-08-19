import os

class Settings:
    PROJECT_NAME: str = "Enterprise Multi-Agent AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "enterprise-super-secret-jwt-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./enterprise_ai.db")
    
    # Optional LLM API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

settings = Settings()
