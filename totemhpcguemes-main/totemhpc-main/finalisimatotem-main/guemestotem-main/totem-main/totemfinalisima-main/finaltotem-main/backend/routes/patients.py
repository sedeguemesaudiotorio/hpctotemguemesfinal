from fastapi import APIRouter, HTTPException, Depends
from services.patient_service import PatientService
from models.patient import PatientResponse, AppointmentConfirmation, PatientCreate
from database import get_database
from typing import List

router = APIRouter(prefix="/api/patients", tags=["patients"])

async def get_patient_service():
    db = await get_database()
    return PatientService(db)

@router.get("/{documento}")
async def get_patient_by_document(
    documento: str,
    patient_service: PatientService = Depends(get_patient_service)
):
    """Buscar paciente por número de documento"""
    if not documento or len(documento) < 7:
        raise HTTPException(status_code=400, detail="Número de documento inválido")
    
    patient = await patient_service.find_by_document(documento)
    
    if not patient:
        # Caso 1: Paciente sin historia clínica - redirigir a otras gestiones
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "no_patient_record",
                "message": "Paciente no encontrado en el sistema",
                "redirect": "other_services"
            }
        )
    
    # Verificar si el paciente tiene turno programado
    if not patient.turno or not patient.turno.medico:
        # Caso 2: Paciente sin turno programado - redirigir a otras gestiones
        raise HTTPException(
            status_code=404,
            detail={
                "error": "no_appointment",
                "message": "Usted no cuenta con turno programado",
                "redirect": "other_services"
            }
        )
    
    # Paciente con turno válido
    return {
        "status": "success",
        "data": {
            "documento": patient.documento,
            "nombre": patient.nombre,
            "apellido": patient.apellido,
            "turno": patient.turno
        }
    }

@router.post("/confirm")
async def confirm_appointment(
    confirmation: AppointmentConfirmation,
    patient_service: PatientService = Depends(get_patient_service)
):
    """Confirmar turno de un paciente"""
    success = await patient_service.confirm_appointment(confirmation.documento)
    if not success:
        raise HTTPException(status_code=404, detail="No se pudo confirmar el turno")
    
    return {"message": "Turno confirmado exitosamente", "documento": confirmation.documento}

@router.get("/", response_model=List[dict])
async def get_all_patients(
    patient_service: PatientService = Depends(get_patient_service)
):
    """Obtener todos los pacientes (para administración)"""
    patients = await patient_service.get_all_patients()
    return patients

@router.get("/confirmed/appointments", response_model=List[dict])
async def get_confirmed_appointments(
    patient_service: PatientService = Depends(get_patient_service)
):
    """Obtener turnos confirmados"""
    appointments = await patient_service.get_confirmed_appointments()
    return appointments

@router.post("/", response_model=dict)
async def create_patient(
    patient_data: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service)
):
    """Crear un nuevo paciente"""
    patient = await patient_service.create_patient(patient_data.dict())
    if not patient:
        raise HTTPException(status_code=400, detail="Error al crear paciente")
    
    return {"message": "Paciente creado exitosamente", "id": patient.id}