from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, List
import hashlib

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for API protection"""
    
    def __init__(self, app, max_requests_per_minute: int = 60):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.request_history: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware"""
    
    def __init__(self, app, max_requests_per_minute: int = 100, burst_limit: int = 20):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.burst_limit = burst_limit
        self.request_history: Dict[str, List[float]] = {}
        self.burst_history: Dict[str, List[float]] = {}

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP + User-Agent hash)"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Create a hash of IP + User-Agent for better tracking
        client_hash = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()
        return f"{client_ip}_{client_hash[:8]}"

    def _clean_old_requests(self, client_id: str, current_time: float):
        """Clean requests older than time windows"""
        # Clean minute window
        if client_id in self.request_history:
            self.request_history[client_id] = [
                req_time for req_time in self.request_history[client_id]
                if current_time - req_time < 60
            ]
        
        # Clean burst window (10 seconds)
        if client_id in self.burst_history:
            self.burst_history[client_id] = [
                req_time for req_time in self.burst_history[client_id]
                if current_time - req_time < 10
            ]

    async def dispatch(self, request: Request, call_next):
        current_time = time.time()
        client_id = self._get_client_id(request)
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Check burst limit (20 requests in 10 seconds)
        burst_count = len(self.burst_history.get(client_id, []))
        if burst_count >= self.burst_limit:
            logger.warning(f"Burst limit exceeded for client {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests in short time. Please wait.",
                    "code": "BURST_LIMIT_EXCEEDED"
                }
            )
        
        # Check minute limit
        minute_count = len(self.request_history.get(client_id, []))
        if minute_count >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Rate limit exceeded. Maximum requests per minute exceeded.",
                    "code": "MINUTE_LIMIT_EXCEEDED"
                }
            )
        
        # Add current request to history
        self.request_history.setdefault(client_id, []).append(current_time)
        self.burst_history.setdefault(client_id, []).append(current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests_per_minute - minute_count - 1))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response

def validate_api_key(api_key: str) -> bool:
    """Validate API key (if needed for admin endpoints)"""
    # In production, validate against database or environment variable
    valid_keys = ["admin-key-123", "totem-key-456"]  # Example keys
    return api_key in valid_keys

async def require_api_key(request: Request):
    """Dependency to require API key for protected endpoints"""
    api_key = request.headers.get("X-API-Key")
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_api_key",
                "message": "Valid API key required",
                "code": "INVALID_API_KEY"
            }
        )
    return api_key