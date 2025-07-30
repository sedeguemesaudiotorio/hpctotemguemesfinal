from typing import Any, Optional, Dict
import json
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl

    def _is_expired(self, cache_entry: Dict) -> bool:
        """Check if cache entry is expired"""
        return time.time() > cache_entry["expires_at"]

    def _clean_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time > value["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key not in self.cache:
                return None
            
            cache_entry = self.cache[key]
            
            if self._is_expired(cache_entry):
                del self.cache[key]
                return None
            
            logger.debug(f"Cache hit: {key}")
            return cache_entry["value"]
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            self.cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }
            
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            
            # Periodically clean expired entries
            if len(self.cache) % 100 == 0:
                self._clean_expired()
                
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache delete: {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def stats(self) -> Dict:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache)
            current_time = time.time()
            
            expired_count = sum(
                1 for entry in self.cache.values()
                if current_time > entry["expires_at"]
            )
            
            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_count,
                "expired_entries": expired_count,
                "cache_size_mb": len(str(self.cache)) / 1024 / 1024
            }
            
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}

# Global cache instance
cache = SimpleCache(default_ttl=300)  # 5 minutes default TTL

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    try:
        key_parts = [str(arg) for arg in args]
        if kwargs:
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return ":".join(key_parts)
    except Exception:
        return str(hash(str(args) + str(sorted(kwargs.items()))))

def cached(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"func:{func.__name__}:" + cache_key(*args, **kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator