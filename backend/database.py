"""
MongoDB database connection and utilities.
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
    
    def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(settings.mongodb_connection_url)
            self.db = self.client[settings.mongodb_database]
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, name: str) -> Collection:
        """Get a collection by name."""
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db[name]


# Global MongoDB instance
mongodb = MongoDB()


def get_db() -> Database:
    """Dependency for getting database instance."""
    return mongodb.db
