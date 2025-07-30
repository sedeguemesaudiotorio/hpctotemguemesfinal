"""
Configuration module for Hospital Totem API
Optimized settings for production and development environments
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Hospital Totem API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database
    mongo_url: str = Field(..., env="MONGO_URL")
    db_name: str = Field(..., env="DB_NAME")
    db_max_connections: int = Field(default=100, env="DB_MAX_CONNECTIONS")
    db_min_connections: int = Field(default=10, env="DB_MIN_CONNECTIONS")
    
    # Security
    allowed_hosts: list = Field(default=["*"], env="ALLOWED_HOSTS")
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    burst_limit: int = Field(default=20, env="BURST_LIMIT")
    
    # Caching
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Performance
    worker_connections: int = Field(default=1000, env="WORKER_CONNECTIONS")
    max_requests: int = Field(default=10000, env="MAX_REQUESTS")
    timeout_keep_alive: int = Field(default=5, env="TIMEOUT_KEEP_ALIVE")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # API Keys (for admin endpoints)
    admin_api_keys: Optional[str] = Field(default=None, env="ADMIN_API_KEYS")
    
    # Data retention
    service_logs_retention_days: int = Field(default=90, env="SERVICE_LOGS_RETENTION_DAYS")
    auto_cleanup_enabled: bool = Field(default=True, env="AUTO_CLEANUP_ENABLED")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Helper functions
def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() in ["development", "dev"]

def get_cors_origins() -> list:
    """Get CORS origins based on environment"""
    if is_production():
        # In production, return specific origins from env var
        if isinstance(settings.cors_origins, str):
            return [origin.strip() for origin in settings.cors_origins.split(",")]
        return settings.cors_origins
    return ["*"]  # Allow all in development

def get_allowed_hosts() -> list:
    """Get allowed hosts based on environment"""
    if is_production():
        if isinstance(settings.allowed_hosts, str):
            return [host.strip() for host in settings.allowed_hosts.split(",")]
        return settings.allowed_hosts
    return ["*"]  # Allow all in development

def get_admin_api_keys() -> list:
    """Get admin API keys"""
    if not settings.admin_api_keys:
        return []
    
    if isinstance(settings.admin_api_keys, str):
        return [key.strip() for key in settings.admin_api_keys.split(",")]
    return settings.admin_api_keys

# Database configuration
def get_mongo_connection_params() -> dict:
    """Get MongoDB connection parameters"""
    return {
        "maxPoolSize": settings.db_max_connections,
        "minPoolSize": settings.db_min_connections,
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 30000,
        "retryWrites": True,
        "retryReads": True
    }

# Logging configuration
def get_logging_config() -> dict:
    """Get logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.log_format
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "detailed",
                "filename": "logs/api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": settings.log_level,
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        }
    }

# FastAPI app configuration
def get_app_config() -> dict:
    """Get FastAPI application configuration"""
    config = {
        "title": settings.app_name,
        "version": settings.app_version,
        "description": "Optimized API for Hospital Totem System with enhanced performance and monitoring",
        "docs_url": "/docs" if not is_production() else None,  # Disable docs in production
        "redoc_url": "/redoc" if not is_production() else None,
        "openapi_url": "/openapi.json" if not is_production() else None,
    }
    
    if is_production():
        # Production-specific settings
        config.update({
            "docs_url": None,
            "redoc_url": None,
            "openapi_url": None
        })
    
    return config

# Performance monitoring
PERFORMANCE_THRESHOLDS = {
    "response_time_warning": 1.0,  # seconds
    "response_time_critical": 3.0,  # seconds
    "memory_usage_warning": 0.8,   # 80%
    "memory_usage_critical": 0.9,  # 90%
    "db_connection_warning": 0.8,  # 80% of max connections
    "db_connection_critical": 0.95  # 95% of max connections
}

# API Rate limits by endpoint
ENDPOINT_RATE_LIMITS = {
    "/api/patients/": {"per_minute": 60, "burst": 10},
    "/api/services/log": {"per_minute": 120, "burst": 20},
    "/api/services/stats": {"per_minute": 30, "burst": 5},
    "/api/health": {"per_minute": 200, "burst": 50}
}