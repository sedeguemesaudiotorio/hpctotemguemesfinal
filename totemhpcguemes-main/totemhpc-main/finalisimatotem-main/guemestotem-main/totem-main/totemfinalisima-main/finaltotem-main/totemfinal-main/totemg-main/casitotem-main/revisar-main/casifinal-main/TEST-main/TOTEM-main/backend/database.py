from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db

async def close_database():
    """Close database connection"""
    client.close()