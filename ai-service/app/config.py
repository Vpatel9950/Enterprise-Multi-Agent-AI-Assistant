import os
from typing import List

# Load .env file manually (most reliable across environments)
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    env_path = os.path.abspath(env_path)
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    key = key.strip()
                    val = val.strip()
                    if key:
                        os.environ[key] = val

_load_env()

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Multi-Agent AI Service"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/ai/v1"
    
    # 1. MongoDB Configuration (Primary & Exclusive Application DB)
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/enterprise_ai")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "enterprise_ai")
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    
    # 2. Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DEFAULT_TTL: int = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", "86400"))
    
    # 3. Qdrant Vector Database
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION_NAME", "enterprise_knowledge_base")
    
    # 4. Security & Inter-Service Tokens
    JWT_SECRET: str = os.getenv("JWT_SECRET", "4c65637572655f456e74657270726973655f4a57545f53757065725f5365637265745f4b65795f3230323621")
    JWT_ALGORITHM: str = "HS256"
    INTERNAL_SERVICE_API_KEY: str = os.getenv("INTERNAL_SERVICE_API_KEY", "enterprise-internal-m2m-token-84920482049284092")
    
    # 5. LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    OPENAI_MINI_MODEL_NAME: str = os.getenv("OPENAI_MINI_MODEL_NAME", "gpt-4o-mini")

    # Google Gemini (Free tier available at aistudio.google.com)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL_NAME: str = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-20240620")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "llama3.1")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
