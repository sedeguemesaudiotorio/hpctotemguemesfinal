from motor.motor_asyncio import AsyncIOMotorDatabase
from models.patient import Patient, PatientResponse, AppointmentConfirmation
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.patients

    async def find_by_document(self, documento: str) -> Optional[PatientResponse]:
        """Buscar paciente por número de documento"""
        try:
            patient_data = await self.collection.find_one({"documento": documento})
            if patient_data:
                # Convertir ObjectId a string si existe
                if "_id" in patient_data:
                    del patient_data["_id"]
                return PatientResponse(**patient_data)
            return None
        except Exception as e:
            logger.error(f"Error finding patient by document {documento}: {str(e)}")
            return None

    async def confirm_appointment(self, documento: str) -> bool:
        """Confirmar turno de un paciente"""
        try:
            result = await self.collection.update_one(
                {"documento": documento},
                {
                    "$set": {
                        "turno.confirmado": True,
                        "turno.fecha_confirmacion": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error confirming appointment for document {documento}: {str(e)}")
            return False

    async def create_patient(self, patient_data: dict) -> Optional[Patient]:
        """Crear un nuevo paciente"""
        try:
            patient = Patient(**patient_data)
            await self.collection.insert_one(patient.dict())
            return patient
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return None

    async def get_all_patients(self) -> list:
        """Obtener todos los pacientes (para admin)"""
        try:
            patients = await self.collection.find().to_list(1000)
            for patient in patients:
                if "_id" in patient:
                    del patient["_id"]
            return patients
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return []

    async def get_confirmed_appointments(self) -> list:
        """Obtener turnos confirmados"""
        try:
            confirmed = await self.collection.find({"turno.confirmado": True}).to_list(1000)
            for appointment in confirmed:
                if "_id" in appointment:
                    del appointment["_id"]
            return confirmed
        except Exception as e:
            logger.error(f"Error getting confirmed appointments: {str(e)}")
            return []