from motor.motor_asyncio import AsyncIOMotorDatabase
from models.service import ServiceLog, ServiceLogCreate, ServiceStats
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ServiceLogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.service_logs

    async def log_service_request(self, log_data: ServiceLogCreate) -> Optional[ServiceLog]:
        """Registrar una solicitud de servicio"""
        try:
            service_log = ServiceLog(**log_data.dict())
            await self.collection.insert_one(service_log.dict())
            return service_log
        except Exception as e:
            logger.error(f"Error logging service request: {str(e)}")
            return None

    async def get_service_stats(self) -> ServiceStats:
        """Obtener estadísticas de servicios"""
        try:
            # Total de gestiones
            total_gestiones = await self.collection.count_documents({})
            
            # Por secretaría
            pipeline_secretaria = [
                {"$group": {"_id": "$secretaria", "count": {"$sum": 1}}}
            ]
            secretaria_stats = await self.collection.aggregate(pipeline_secretaria).to_list(None)
            por_secretaria = {item["_id"]: item["count"] for item in secretaria_stats}
            
            # Por día (últimos 7 días)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            pipeline_dia = [
                {"$match": {"timestamp": {"$gte": seven_days_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1}
                }}
            ]
            dia_stats = await self.collection.aggregate(pipeline_dia).to_list(None)
            por_dia = {item["_id"]: item["count"] for item in dia_stats}
            
            # Gestiones recientes (últimas 10)
            gestiones_recientes = await self.collection.find().sort("timestamp", -1).limit(10).to_list(10)
            for gestion in gestiones_recientes:
                if "_id" in gestion:
                    del gestion["_id"]
            
            return ServiceStats(
                total_gestiones=total_gestiones,
                por_secretaria=por_secretaria,
                por_dia=por_dia,
                gestiones_recientes=gestiones_recientes
            )
        except Exception as e:
            logger.error(f"Error getting service stats: {str(e)}")
            return ServiceStats(
                total_gestiones=0,
                por_secretaria={},
                por_dia={},
                gestiones_recientes=[]
            )

    async def update_service_status(self, service_id: str, estado: str) -> bool:
        """Actualizar el estado de un servicio"""
        try:
            result = await self.collection.update_one(
                {"id": service_id},
                {"$set": {"estado": estado}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating service status: {str(e)}")
            return False

    async def get_recent_services(self, limit: int = 50) -> List[Dict]:
        """Obtener servicios recientes"""
        try:
            services = await self.collection.find().sort("timestamp", -1).limit(limit).to_list(limit)
            for service in services:
                if "_id" in service:
                    del service["_id"]
            return services
        except Exception as e:
            logger.error(f"Error getting recent services: {str(e)}")
            return []