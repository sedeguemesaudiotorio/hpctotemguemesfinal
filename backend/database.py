from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db

async def init_database():
    """Initialize database with indexes for optimal performance"""
    try:
        logger.info("🔧 Initializing database indexes...")
        
        # Create indexes for patients collection
        patients_collection = db.patients
        await patients_collection.create_index("documento", unique=True)
        await patients_collection.create_index("turno.confirmado")
        await patients_collection.create_index("created_at")
        await patients_collection.create_index([("documento", 1), ("turno.confirmado", 1)])
        
        # Create indexes for service_logs collection
        service_logs_collection = db.service_logs
        await service_logs_collection.create_index("documento")
        await service_logs_collection.create_index("secretaria")
        await service_logs_collection.create_index("timestamp")
        await service_logs_collection.create_index("estado")
        await service_logs_collection.create_index([("documento", 1), ("timestamp", -1)])
        await service_logs_collection.create_index([("secretaria", 1), ("timestamp", -1)])
        
        # Create TTL index for old service logs (auto-delete after 90 days)
        await service_logs_collection.create_index(
            "timestamp", 
            expireAfterSeconds=7776000  # 90 days
        )
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating database indexes: {e}")

async def close_database():
    """Close database connection"""
    try:
        client.close()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")

# Connection pooling configuration
async def configure_connection_pool():
    """Configure MongoDB connection pool for optimal performance"""
    # Motor automatically handles connection pooling
    # These settings are configured via the connection string
    pass