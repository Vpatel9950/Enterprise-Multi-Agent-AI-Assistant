import logging
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from app.config import settings

logger = logging.getLogger("enterprise.ai.mongo")

class MongoDBManager:
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            logger.info("Initializing MongoDB Client connection pool...")
            cls._client = MongoClient(
                settings.MONGODB_URI,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
        return cls._client

    @classmethod
    def get_database(cls) -> Database:
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_DB_NAME]
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB client connections closed.")

    @classmethod
    def ping(cls) -> bool:
        try:
            client = cls.get_client()
            client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB Ping Error: {e}")
            return False

    # Specific Collections Accessors
    @classmethod
    def users(cls) -> Collection:
        return cls.get_database()["users"]

    @classmethod
    def organizations(cls) -> Collection:
        return cls.get_database()["organizations"]

    @classmethod
    def departments(cls) -> Collection:
        return cls.get_database()["departments"]

    @classmethod
    def roles(cls) -> Collection:
        return cls.get_database()["roles"]

    @classmethod
    def ai_agents(cls) -> Collection:
        return cls.get_database()["ai_agents"]

    @classmethod
    def conversations(cls) -> Collection:
        return cls.get_database()["conversations"]

    @classmethod
    def messages(cls) -> Collection:
        return cls.get_database()["messages"]

    @classmethod
    def agent_execution_logs(cls) -> Collection:
        return cls.get_database()["agent_execution_logs"]

    @classmethod
    def uploaded_documents(cls) -> Collection:
        return cls.get_database()["uploaded_documents"]

    @classmethod
    def workflows(cls) -> Collection:
        return cls.get_database()["workflows"]

    @classmethod
    def approval_requests(cls) -> Collection:
        return cls.get_database()["approval_requests"]

    @classmethod
    def audit_logs(cls) -> Collection:
        return cls.get_database()["audit_logs"]

def to_object_id(oid: Any) -> Optional[ObjectId]:
    if not oid:
        return None
    if isinstance(oid, ObjectId):
        return oid
    try:
        return ObjectId(str(oid))
    except Exception:
        return None

def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    result = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, list):
            result[k] = [str(item) if isinstance(item, ObjectId) else item for item in v]
        elif isinstance(v, dict):
            result[k] = serialize_doc(v)
        else:
            result[k] = v
    if "_id" in result:
        result["id"] = result["_id"]
    return result
