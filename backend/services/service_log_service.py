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
        """
        Registrar una solicitud de servicio con validación mejorada
        """
        try:
            service_log = ServiceLog(**log_data.dict())
            
            # Insert with duplicate detection (if needed)
            await self.collection.insert_one(service_log.dict())
            logger.info(f"Service request logged: {service_log.documento} -> {service_log.secretaria}")
            return service_log
            
        except Exception as e:
            logger.error(f"Error logging service request: {str(e)}")
            return None

    async def get_service_stats(self, days: int = 7) -> ServiceStats:
        """
        Obtener estadísticas de servicios optimizadas con agregaciones
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get total count efficiently
            total_gestiones = await self.collection.count_documents({
                "timestamp": {"$gte": start_date},
                "deleted": {"$ne": True}  # Exclude soft deleted
            })
            
            # Aggregation pipeline for statistics
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start_date},
                        "deleted": {"$ne": True}
                    }
                },
                {
                    "$facet": {
                        # Group by secretaria
                        "por_secretaria": [
                            {"$group": {"_id": "$secretaria", "count": {"$sum": 1}}}
                        ],
                        # Group by day
                        "por_dia": [
                            {
                                "$group": {
                                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                                    "count": {"$sum": 1}
                                }
                            },
                            {"$sort": {"_id": 1}}
                        ],
                        # Get recent services
                        "gestiones_recientes": [
                            {"$sort": {"timestamp": -1}},
                            {"$limit": 10},
                            {
                                "$project": {
                                    "_id": 0,
                                    "documento": 1,
                                    "secretaria": 1,
                                    "piso": 1,
                                    "timestamp": 1,
                                    "estado": 1
                                }
                            }
                        ]
                    }
                }
            ]
            
            # Execute aggregation
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats_data = result[0]
                por_secretaria = {item["_id"]: item["count"] for item in stats_data["por_secretaria"]}
                por_dia = {item["_id"]: item["count"] for item in stats_data["por_dia"]}
                gestiones_recientes = stats_data["gestiones_recientes"]
            else:
                por_secretaria = {}
                por_dia = {}
                gestiones_recientes = []
            
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
        """
        Actualizar el estado de un servicio con validación
        """
        try:
            # Validate that the service exists first
            existing_service = await self.collection.find_one({"id": service_id, "deleted": {"$ne": True}})
            if not existing_service:
                logger.warning(f"Service not found for status update: {service_id}")
                return False
            
            result = await self.collection.update_one(
                {"id": service_id, "deleted": {"$ne": True}},
                {
                    "$set": {
                        "estado": estado,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Service status updated: {service_id} -> {estado}")
            else:
                logger.warning(f"No service status was updated: {service_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error updating service status: {str(e)}")
            return False

    async def get_recent_services(self, limit: int = 50, secretaria: Optional[str] = None, estado: Optional[str] = None) -> List[Dict]:
        """
        Obtener servicios recientes con filtros opcionales
        """
        try:
            # Build query filters
            query_filter = {"deleted": {"$ne": True}}
            
            if secretaria:
                query_filter["secretaria"] = secretaria
            if estado:
                query_filter["estado"] = estado
            
            # Get services with pagination and sorting
            services = await self.collection.find(
                query_filter,
                {"_id": 0}  # Exclude MongoDB _id
            ).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            return services
            
        except Exception as e:
            logger.error(f"Error getting recent services: {str(e)}")
            return []

    async def delete_service(self, service_id: str) -> bool:
        """
        Eliminar un servicio (soft delete)
        """
        try:
            result = await self.collection.update_one(
                {"id": service_id, "deleted": {"$ne": True}},
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Service soft deleted: {service_id}")
            else:
                logger.warning(f"No service was deleted: {service_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {str(e)}")
            return False

    async def get_service_by_id(self, service_id: str) -> Optional[Dict]:
        """
        Obtener un servicio por su ID
        """
        try:
            service = await self.collection.find_one(
                {"id": service_id, "deleted": {"$ne": True}},
                {"_id": 0}
            )
            return service
            
        except Exception as e:
            logger.error(f"Error getting service by ID {service_id}: {str(e)}")
            return None

    async def get_services_by_document(self, documento: str) -> List[Dict]:
        """
        Obtener todos los servicios de un paciente específico
        """
        try:
            services = await self.collection.find(
                {
                    "documento": documento,
                    "deleted": {"$ne": True}
                },
                {"_id": 0}
            ).sort("timestamp", -1).to_list(length=100)
            
            return services
            
        except Exception as e:
            logger.error(f"Error getting services by document {documento}: {str(e)}")
            return []

    async def get_services_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtener servicios en un rango de fechas
        """
        try:
            services = await self.collection.find(
                {
                    "timestamp": {
                        "$gte": start_date,
                        "$lte": end_date
                    },
                    "deleted": {"$ne": True}
                },
                {"_id": 0}
            ).sort("timestamp", -1).to_list(length=1000)
            
            return services
            
        except Exception as e:
            logger.error(f"Error getting services by date range: {str(e)}")
            return []

    async def get_pending_services_count(self) -> int:
        """
        Obtener cantidad de servicios pendientes
        """
        try:
            count = await self.collection.count_documents({
                "estado": "pendiente",
                "deleted": {"$ne": True}
            })
            return count
            
        except Exception as e:
            logger.error(f"Error getting pending services count: {str(e)}")
            return 0

    async def bulk_update_status(self, service_ids: List[str], new_estado: str) -> int:
        """
        Actualizar el estado de múltiples servicios
        """
        try:
            result = await self.collection.update_many(
                {
                    "id": {"$in": service_ids},
                    "deleted": {"$ne": True}
                },
                {
                    "$set": {
                        "estado": new_estado,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            updated_count = result.modified_count
            logger.info(f"Bulk status update: {updated_count} services updated to {new_estado}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error in bulk status update: {str(e)}")
            return 0