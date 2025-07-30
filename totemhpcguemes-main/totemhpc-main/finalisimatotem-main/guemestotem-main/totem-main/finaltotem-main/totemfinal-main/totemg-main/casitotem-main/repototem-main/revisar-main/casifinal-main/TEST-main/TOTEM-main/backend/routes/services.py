from fastapi import APIRouter, HTTPException, Depends
from services.service_log_service import ServiceLogService
from models.service import ServiceLogCreate, ServiceStats
from database import get_database

router = APIRouter(prefix="/api/services", tags=["services"])

async def get_service_log_service():
    db = await get_database()
    return ServiceLogService(db)

@router.post("/log")
async def log_service_request(
    log_data: ServiceLogCreate,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """Registrar una solicitud de servicio a secretaría"""
    if not log_data.documento or len(log_data.documento) < 7:
        raise HTTPException(status_code=400, detail="Número de documento inválido")
    
    if log_data.secretaria not in ['pb', 'pp', '2p', '3p']:
        raise HTTPException(status_code=400, detail="Secretaría inválida")
    
    service_log = await service_log_service.log_service_request(log_data)
    if not service_log:
        raise HTTPException(status_code=400, detail="Error al registrar solicitud")
    
    return {
        "message": "Solicitud registrada exitosamente",
        "id": service_log.id,
        "piso": service_log.piso,
        "timestamp": service_log.timestamp
    }

@router.get("/stats", response_model=ServiceStats)
async def get_service_stats(
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """Obtener estadísticas de servicios"""
    stats = await service_log_service.get_service_stats()
    return stats

@router.get("/recent")
async def get_recent_services(
    limit: int = 50,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """Obtener servicios recientes"""
    services = await service_log_service.get_recent_services(limit)
    return {"services": services}

@router.put("/{service_id}/status")
async def update_service_status(
    service_id: str,
    estado: str,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """Actualizar el estado de un servicio"""
    if estado not in ['pendiente', 'atendido', 'cancelado']:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    success = await service_log_service.update_service_status(service_id, estado)
    if not success:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    return {"message": "Estado actualizado exitosamente"}