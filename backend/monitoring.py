"""
Monitoring and health check utilities for Hospital Totem API
"""
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import settings, PERFORMANCE_THRESHOLDS
from database import get_database

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Health monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.db_query_times = []
        
    def record_request(self, response_time: float, is_error: bool = False):
        """Record request metrics"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        
        # Keep only last 1000 response times for memory efficiency
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def record_db_query(self, query_time: float):
        """Record database query time"""
        self.db_query_times.append(query_time)
        if len(self.db_query_times) > 1000:
            self.db_query_times = self.db_query_times[-1000:]
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024 ** 3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024 ** 3)  # GB
            
            # Network stats
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "usage_percent": memory_percent,
                    "available_gb": round(memory_available, 2),
                    "status": "healthy" if memory_percent < 80 else "warning" if memory_percent < 90 else "critical"
                },
                "disk": {
                    "usage_percent": disk_percent,
                    "free_gb": round(disk_free, 2),
                    "status": "healthy" if disk_percent < 80 else "warning" if disk_percent < 90 else "critical"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    async def get_database_health(self) -> Dict[str, Any]:
        """Check database health and performance"""
        try:
            db = await get_database()
            start_time = time.time()
            
            # Test basic connectivity
            await db.command("ping")
            ping_time = time.time() - start_time
            
            # Get database stats
            start_time = time.time()
            db_stats = await db.command("dbStats")
            stats_time = time.time() - start_time
            
            # Get collection counts
            patients_count = await db.patients.estimated_document_count()
            services_count = await db.service_logs.estimated_document_count()
            
            return {
                "status": "healthy",
                "ping_time_ms": round(ping_time * 1000, 2),
                "stats_query_time_ms": round(stats_time * 1000, 2),
                "collections": {
                    "patients": patients_count,
                    "service_logs": services_count
                },
                "storage": {
                    "data_size_mb": round(db_stats.get("dataSize", 0) / (1024 ** 2), 2),
                    "index_size_mb": round(db_stats.get("indexSize", 0) / (1024 ** 2), 2),
                    "total_size_mb": round(db_stats.get("storageSize", 0) / (1024 ** 2), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "ping_time_ms": None
            }
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        uptime = time.time() - self.start_time
        
        # Calculate response time statistics
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)
            min_response_time = min(self.response_times)
            
            # Calculate percentiles
            sorted_times = sorted(self.response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
            p95_response_time = 0
            p99_response_time = 0
        
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        requests_per_second = self.request_count / uptime if uptime > 0 else 0
        
        return {
            "uptime_seconds": round(uptime, 2),
            "uptime_human": str(timedelta(seconds=int(uptime))),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "requests_per_second": round(requests_per_second, 2),
            "response_times": {
                "average_ms": round(avg_response_time * 1000, 2),
                "min_ms": round(min_response_time * 1000, 2),
                "max_ms": round(max_response_time * 1000, 2),
                "p95_ms": round(p95_response_time * 1000, 2),
                "p99_ms": round(p99_response_time * 1000, 2)
            },
            "status": self._get_api_status(avg_response_time, error_rate)
        }
    
    def _get_api_status(self, avg_response_time: float, error_rate: float) -> str:
        """Determine API health status"""
        if error_rate > 10:  # More than 10% error rate
            return "critical"
        elif error_rate > 5:  # More than 5% error rate
            return "warning"
        elif avg_response_time > PERFORMANCE_THRESHOLDS["response_time_critical"]:
            return "critical"
        elif avg_response_time > PERFORMANCE_THRESHOLDS["response_time_warning"]:
            return "warning"
        else:
            return "healthy"
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health check results"""
        try:
            # Gather all metrics concurrently
            system_metrics, db_health, api_metrics = await asyncio.gather(
                self.get_system_metrics(),
                self.get_database_health(),
                asyncio.to_thread(self.get_api_metrics)
            )
            
            # Determine overall status
            statuses = [
                system_metrics.get("cpu", {}).get("status", "unknown"),
                system_metrics.get("memory", {}).get("status", "unknown"),
                system_metrics.get("disk", {}).get("status", "unknown"),
                db_health.get("status", "unknown"),
                api_metrics.get("status", "unknown")
            ]
            
            # Overall status logic
            if "critical" in statuses:
                overall_status = "critical"
            elif "warning" in statuses:
                overall_status = "warning"
            elif "unhealthy" in statuses:
                overall_status = "unhealthy"
            elif all(s == "healthy" for s in statuses if s != "unknown"):
                overall_status = "healthy"
            else:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "system": system_metrics,
                "database": db_health,
                "api": api_metrics,
                "environment": {
                    "environment": settings.environment,
                    "version": settings.app_version,
                    "debug": settings.debug
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive health check failed: {e}")
            return {
                "status": "critical",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def reset_metrics(self):
        """Reset collected metrics"""
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.db_query_times = []
        logger.info("Metrics reset completed")

# Global health monitor instance
health_monitor = HealthMonitor()

async def run_health_checks():
    """Run periodic health checks"""
    while True:
        try:
            health_data = await health_monitor.get_comprehensive_health()
            
            # Log warnings or critical issues
            if health_data["status"] in ["warning", "critical"]:
                logger.warning(f"Health check alert: {health_data['status']} - {health_data}")
            
            # Sleep for the configured interval
            await asyncio.sleep(settings.health_check_interval)
            
        except Exception as e:
            logger.error(f"Health check loop error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

def start_health_monitoring():
    """Start background health monitoring"""
    if settings.enable_metrics:
        asyncio.create_task(run_health_checks())
        logger.info("Health monitoring started")