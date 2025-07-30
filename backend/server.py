from fastapi import FastAPI, APIRouter, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import time
import asyncio
from pathlib import Path

# Import routes
from routes.patients import router as patients_router
from routes.services import router as services_router
from database import close_database, init_database

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Global variables for database
client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events"""
    # Startup
    logger.info("🚀 Starting Hospital Totem API...")
    
    # Initialize database with indexes
    await init_database()
    
    logger.info("✅ Hospital Totem API started successfully")
    
    yield
    
    # Shutdown
    logger.info("📴 Shutting down Hospital Totem API...")
    await close_database()
    logger.info("✅ Hospital Totem API shutdown complete")

# Create the main app with lifespan manager
app = FastAPI(
    title="Hospital Totem API", 
    version="1.0.0",
    description="Optimized API for Hospital Totem System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # In production, specify actual hosts
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    return response

# Rate limiting middleware (simple implementation)
request_counts = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries (older than 1 minute)
    request_counts[client_ip] = [
        req_time for req_time in request_counts.get(client_ip, [])
        if current_time - req_time < 60
    ]
    
    # Check rate limit (max 100 requests per minute)
    if len(request_counts.get(client_ip, [])) >= 100:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add current request
    request_counts.setdefault(client_ip, []).append(current_time)
    
    response = await call_next(request)
    return response

# Create a router with the /api prefix for health checks
api_router = APIRouter(prefix="/api")

# Enhanced health check endpoints
@api_router.get("/")
async def root():
    """Root endpoint with basic API info"""
    return {
        "message": "Hospital Totem API is running", 
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@api_router.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Test database connection
        from database import get_database
        db = await get_database()
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "Hospital Totem API",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": time.time(),
        "uptime": time.time()
    }

@api_router.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint"""
    return {
        "requests_per_minute": {ip: len(times) for ip, times in request_counts.items()},
        "active_connections": len(request_counts),
        "timestamp": time.time()
    }

# Include routers - patients and services already have /api prefix
app.include_router(patients_router)
app.include_router(services_router)
app.include_router(api_router)

# CORS configuration - more restrictive in production
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # In production: specify actual origins
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # Cache CORS preflight for 1 hour
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error logging"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred",
        "timestamp": time.time()
    }