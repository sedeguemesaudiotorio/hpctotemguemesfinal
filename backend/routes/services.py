from fastapi import APIRouter, HTTPException, Depends, Query, status
from services.service_log_service import ServiceLogService
from models.service import ServiceLogCreate, ServiceStats
from database import get_database
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/services", tags=["services"])

async def get_service_log_service():
    """Dependency to get service log service instance"""
    db = await get_database()
    return ServiceLogService(db)

def validate_documento(documento: str) -> bool:
    """Validate document number format"""
    if not documento:
        return False
    
    # Remove any non-digit characters
    clean_doc = re.sub(r'\D', '', documento)
    
    # Check length (between 7 and 10 digits)
    if len(clean_doc) < 7 or len(clean_doc) > 10:
        return False
    
    return True

def validate_secretaria(secretaria: str) -> bool:
    """Validate secretaria value"""
    valid_secretarias = ['pb', 'pp', '2p', '3p']
    return secretaria.lower() in valid_secretarias

@router.post("/log", response_model=dict)
async def log_service_request(
    log_data: ServiceLogCreate,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """
    Registrar una solicitud de servicio a secretaría
    
    - **documento**: Número de documento del paciente
    - **secretaria**: Código de secretaría (pb, pp, 2p, 3p)
    - **piso**: Piso donde se encuentra la secretaría
    """
    # Enhanced validation
    if not validate_documento(log_data.documento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_document",
                "message": "Número de documento inválido. Debe contener entre 7 y 10 dígitos.",
                "code": "INVALID_DOCUMENT_FORMAT"
            }
        )
    
    if not validate_secretaria(log_data.secretaria):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_secretaria",
                "message": "Secretaría inválida. Valores permitidos: pb, pp, 2p, 3p",
                "code": "INVALID_SECRETARIA"
            }
        )
    
    # Clean and normalize data
    clean_data = log_data.dict()
    clean_data["documento"] = re.sub(r'\D', '', clean_data["documento"])
    clean_data["secretaria"] = clean_data["secretaria"].lower()
    
    try:
        service_log = await service_log_service.log_service_request(ServiceLogCreate(**clean_data))
        if not service_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "registration_failed",
                    "message": "Error al registrar solicitud",
                    "code": "SERVICE_REGISTRATION_FAILED"
                }
            )
        
        logger.info(f"Service request logged: {clean_data['documento']} -> {clean_data['secretaria']}")
        return {
            "status": "success",
            "message": "Solicitud registrada exitosamente",
            "data": {
                "id": service_log.id,
                "documento": service_log.documento,
                "secretaria": service_log.secretaria,
                "piso": service_log.piso,
                "timestamp": service_log.timestamp,
                "estado": service_log.estado
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging service request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al registrar solicitud",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/stats", response_model=dict)
async def get_service_stats(
    days: int = Query(7, ge=1, le=90, description="Días para estadísticas"),
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """
    Obtener estadísticas de servicios
    
    - **days**: Número de días para el análisis (1-90)
    """
    try:
        stats = await service_log_service.get_service_stats(days)
        return {
            "status": "success",
            "data": stats,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al obtener estadísticas",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/recent", response_model=dict)
async def get_recent_services(
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    secretaria: Optional[str] = Query(None, description="Filtrar por secretaría"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """
    Obtener servicios recientes con filtros opcionales
    
    - **limit**: Número máximo de resultados (1-200)
    - **secretaria**: Filtrar por secretaría específica
    - **estado**: Filtrar por estado específico
    """
    try:
        # Validate filters
        if secretaria and not validate_secretaria(secretaria):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_secretaria",
                    "message": "Secretaría inválida para filtro",
                    "code": "INVALID_FILTER_SECRETARIA"
                }
            )
        
        if estado and estado not in ['pendiente', 'atendido', 'cancelado']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_estado",
                    "message": "Estado inválido para filtro",
                    "code": "INVALID_FILTER_ESTADO"
                }
            )
        
        services = await service_log_service.get_recent_services(
            limit=limit,
            secretaria=secretaria.lower() if secretaria else None,
            estado=estado
        )
        
        return {
            "status": "success",
            "data": services,
            "count": len(services),
            "filters": {
                "secretaria": secretaria,
                "estado": estado,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al obtener servicios recientes",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.put("/{service_id}/status", response_model=dict)
async def update_service_status(
    service_id: str,
    request_data: dict,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """
    Actualizar el estado de un servicio
    
    - **service_id**: ID único del servicio
    - **estado**: Nuevo estado (pendiente, atendido, cancelado)
    """
    estado = request_data.get("estado")
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "missing_estado",
                "message": "Estado es requerido",
                "code": "MISSING_ESTADO_FIELD"
            }
        )
    
    valid_estados = ['pendiente', 'atendido', 'cancelado']
    if estado not in valid_estados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_estado",
                "message": f"Estado inválido. Valores permitidos: {', '.join(valid_estados)}",
                "code": "INVALID_ESTADO_VALUE"
            }
        )
    
    try:
        success = await service_log_service.update_service_status(service_id, estado)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "service_not_found",
                    "message": "Servicio no encontrado",
                    "code": "SERVICE_NOT_FOUND"
                }
            )
        
        logger.info(f"Service status updated: {service_id} -> {estado}")
        return {
            "status": "success",
            "message": "Estado actualizado exitosamente",
            "service_id": service_id,
            "new_estado": estado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al actualizar estado",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.delete("/{service_id}", response_model=dict)
async def delete_service(
    service_id: str,
    service_log_service: ServiceLogService = Depends(get_service_log_service)
):
    """
    Eliminar un registro de servicio (soft delete)
    
    - **service_id**: ID único del servicio a eliminar
    """
    try:
        success = await service_log_service.delete_service(service_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "service_not_found",
                    "message": "Servicio no encontrado",
                    "code": "SERVICE_NOT_FOUND"
                }
            )
        
        logger.info(f"Service deleted: {service_id}")
        return {
            "status": "success",
            "message": "Servicio eliminado exitosamente",
            "service_id": service_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al eliminar servicio",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )