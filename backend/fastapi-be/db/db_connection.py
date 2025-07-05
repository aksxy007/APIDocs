from pymongo import MongoClient, errors
from typing import List, Dict, Any, Optional
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

class MongoDBClient:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connect()  # Auto-connect on init

    def _connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            logger.info("Connected to MongoDB.")
        except errors.ServerSelectionTimeoutError as err:
            logger.error(f"MongoDB connection failed: {err}")
            raise

    def ping(self) -> bool:
        try:
            self.client.admin.command("ping")
            logger.info("MongoDB ping successful.")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False

    def get_collection(self, collection_name: str):
        if self.db is None:
            raise RuntimeError("Not connected to MongoDB.")
        return self.db[collection_name]

    def insert_one(self, collection: str, document: Dict[str, Any]):
        return self.get_collection(collection).insert_one(document)

    def insert_many(self, collection: str, documents: List[Dict[str, Any]]):
        return self.get_collection(collection).insert_many(documents)

    def find(self, collection: str, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        return list(self.get_collection(collection).find(query))

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.get_collection(collection).find_one(query)

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        return self.get_collection(collection).update_one(query, {"$set": update}, upsert=upsert)

    def delete_one(self, collection: str, query: Dict[str, Any]):
        return self.get_collection(collection).delete_one(query)

    def delete_many(self, collection: str, query: Dict[str, Any]):
        return self.get_collection(collection).delete_many(query)

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
