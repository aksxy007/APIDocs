from db.db_connection import MongoDBClient
from dotenv import load_dotenv
import os 

load_dotenv()

# uri= str(os.getenv("MONGO_URI")),
# db_name=str(os.getenv("MONGO_DB_NAME"))

# print(f"URI: {uri}, DB: {db_name}")

mogno_client = MongoDBClient(
    uri= str(os.getenv("MONGO_URI")),
    db_name=str(os.getenv("MONGO_DB_NAME"))
)

def get_mongo_client() -> MongoDBClient:
    """
    Returns the MongoDB client instance.
    """
    return mogno_client