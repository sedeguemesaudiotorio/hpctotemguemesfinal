from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from services.patient_service import PatientService
from models.patient import PatientResponse, AppointmentConfirmation, PatientCreate
from database import get_database
from typing import List, Optional
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/patients", tags=["patients"])

async def get_patient_service():
    """Dependency to get patient service instance"""
    db = await get_database()
    return PatientService(db)

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

@router.get("/{documento}", response_model=dict)
async def get_patient_by_document(
    documento: str,
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Buscar paciente por número de documento
    
    - **documento**: Número de documento del paciente (7-10 dígitos)
    """
    # Enhanced validation
    if not validate_documento(documento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_document",
                "message": "Número de documento inválido. Debe contener entre 7 y 10 dígitos.",
                "code": "INVALID_DOCUMENT_FORMAT"
            }
        )
    
    # Clean document number
    clean_documento = re.sub(r'\D', '', documento)
    
    try:
        patient = await patient_service.find_by_document(clean_documento)
        
        if not patient:
            # Caso 1: Paciente sin historia clínica - redirigir a otras gestiones
            logger.info(f"Patient not found in system: {clean_documento}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "no_patient_record",
                    "message": "Paciente no encontrado en el sistema",
                    "redirect": "other_services",
                    "code": "PATIENT_NOT_FOUND"
                }
            )
        
        # Verificar si el paciente tiene turno programado
        if not patient.turno or not patient.turno.medico:
            # Caso 2: Paciente sin turno programado - redirigir a otras gestiones
            logger.info(f"Patient found but no appointment: {clean_documento}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "no_appointment",
                    "message": "Usted no cuenta con turno programado",
                    "redirect": "other_services",
                    "code": "NO_APPOINTMENT_SCHEDULED"
                }
            )
        
        # Paciente con turno válido
        logger.info(f"Patient found with valid appointment: {clean_documento}")
        return {
            "status": "success",
            "data": {
                "documento": patient.documento,
                "nombre": patient.nombre,
                "apellido": patient.apellido,
                "turno": patient.turno
            },
            "timestamp": patient.updated_at
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error finding patient {clean_documento}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno del sistema",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.post("/confirm", response_model=dict)
async def confirm_appointment(
    confirmation: AppointmentConfirmation,
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Confirmar turno de un paciente
    
    - **documento**: Número de documento del paciente
    """
    if not validate_documento(confirmation.documento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_document", 
                "message": "Número de documento inválido",
                "code": "INVALID_DOCUMENT_FORMAT"
            }
        )
    
    clean_documento = re.sub(r'\D', '', confirmation.documento)
    
    try:
        success = await patient_service.confirm_appointment(clean_documento)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "confirmation_failed",
                    "message": "No se pudo confirmar el turno",
                    "code": "APPOINTMENT_CONFIRMATION_FAILED"
                }
            )
        
        logger.info(f"Appointment confirmed successfully: {clean_documento}")
        return {
            "status": "success",
            "message": "Turno confirmado exitosamente", 
            "documento": clean_documento,
            "confirmed_at": confirmation.fecha_confirmacion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming appointment for {clean_documento}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al confirmar turno",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/", response_model=dict)
async def get_all_patients(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados por página"),
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Obtener todos los pacientes con paginación (para administración)
    
    - **page**: Número de página (inicio en 1)
    - **limit**: Cantidad de resultados por página (máximo 100)
    """
    try:
        skip = (page - 1) * limit
        patients, total = await patient_service.get_all_patients_paginated(skip, limit)
        
        return {
            "status": "success",
            "data": patients,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al obtener pacientes",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/confirmed/appointments", response_model=dict)
async def get_confirmed_appointments(
    patient_service: PatientService = Depends(get_patient_service)
):
    """Obtener turnos confirmados"""
    try:
        appointments = await patient_service.get_confirmed_appointments()
        return {
            "status": "success",
            "data": appointments,
            "count": len(appointments)
        }
        
    except Exception as e:
        logger.error(f"Error getting confirmed appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al obtener turnos confirmados",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.post("/", response_model=dict)
async def create_patient(
    patient_data: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Crear un nuevo paciente
    
    - **documento**: Número de documento único
    - **nombre**: Nombre del paciente
    - **apellido**: Apellido del paciente
    - **turno**: Información del turno médico
    """
    if not validate_documento(patient_data.documento):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_document",
                "message": "Número de documento inválido",
                "code": "INVALID_DOCUMENT_FORMAT"
            }
        )
    
    # Clean and validate data
    clean_data = patient_data.dict()
    clean_data["documento"] = re.sub(r'\D', '', clean_data["documento"])
    
    try:
        patient = await patient_service.create_patient(clean_data)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "creation_failed",
                    "message": "Error al crear paciente",
                    "code": "PATIENT_CREATION_FAILED"
                }
            )
        
        logger.info(f"Patient created successfully: {clean_data['documento']}")
        return {
            "status": "success",
            "message": "Paciente creado exitosamente", 
            "id": patient.id,
            "documento": patient.documento
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Error interno al crear paciente",
                "code": "INTERNAL_SERVER_ERROR"
            }
        )