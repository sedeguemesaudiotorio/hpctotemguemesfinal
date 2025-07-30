from motor.motor_asyncio import AsyncIOMotorDatabase
from models.patient import Patient, PatientResponse, AppointmentConfirmation
from typing import Optional, Tuple, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.patients

    async def find_by_document(self, documento: str) -> Optional[PatientResponse]:
        """
        Buscar paciente por número de documento con optimización de consulta
        """
        try:
            # Use index on documento field for faster lookup
            patient_data = await self.collection.find_one(
                {"documento": documento},
                {"_id": 0}  # Exclude MongoDB _id field
            )
            
            if patient_data:
                return PatientResponse(**patient_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding patient by document {documento}: {str(e)}")
            return None

    async def confirm_appointment(self, documento: str) -> bool:
        """
        Confirmar turno de un paciente con validación adicional
        """
        try:
            # First check if patient exists and has an appointment
            existing_patient = await self.collection.find_one(
                {
                    "documento": documento,
                    "turno.medico": {"$exists": True, "$ne": None}
                }
            )
            
            if not existing_patient:
                logger.warning(f"Cannot confirm appointment - patient not found or no appointment: {documento}")
                return False
            
            # Update the appointment confirmation
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
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Appointment confirmed successfully for document: {documento}")
            else:
                logger.warning(f"No appointment was modified for document: {documento}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error confirming appointment for document {documento}: {str(e)}")
            return False

    async def create_patient(self, patient_data: dict) -> Optional[Patient]:
        """
        Crear un nuevo paciente con validación de duplicados
        """
        try:
            # Check if patient already exists
            existing = await self.collection.find_one({"documento": patient_data["documento"]})
            if existing:
                logger.warning(f"Patient already exists: {patient_data['documento']}")
                return None
            
            patient = Patient(**patient_data)
            
            # Insert with error handling for unique constraint
            await self.collection.insert_one(patient.dict())
            logger.info(f"Patient created successfully: {patient.documento}")
            return patient
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return None

    async def get_all_patients_paginated(self, skip: int = 0, limit: int = 50) -> Tuple[List[dict], int]:
        """
        Obtener todos los pacientes con paginación optimizada
        """
        try:
            # Get total count efficiently
            total = await self.collection.count_documents({})
            
            # Get paginated results with projection to exclude _id
            patients = await self.collection.find(
                {},
                {"_id": 0}
            ).skip(skip).limit(limit).to_list(length=limit)
            
            return patients, total
            
        except Exception as e:
            logger.error(f"Error getting paginated patients: {str(e)}")
            return [], 0

    async def get_all_patients(self) -> list:
        """
        Obtener todos los pacientes (legacy method - consider using paginated version)
        """
        try:
            patients = await self.collection.find(
                {},
                {"_id": 0}
            ).limit(1000).to_list(length=1000)
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting all patients: {str(e)}")
            return []

    async def get_confirmed_appointments(self) -> list:
        """
        Obtener turnos confirmados con optimización de consulta
        """
        try:
            # Use compound index on documento and turno.confirmado
            confirmed = await self.collection.find(
                {"turno.confirmado": True},
                {"_id": 0}
            ).sort("turno.fecha_confirmacion", -1).to_list(length=1000)
            
            return confirmed
            
        except Exception as e:
            logger.error(f"Error getting confirmed appointments: {str(e)}")
            return []

    async def get_patients_by_date_range(self, start_date: datetime, end_date: datetime) -> list:
        """
        Obtener pacientes creados en un rango de fechas
        """
        try:
            patients = await self.collection.find(
                {
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                },
                {"_id": 0}
            ).sort("created_at", -1).to_list(length=1000)
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting patients by date range: {str(e)}")
            return []

    async def update_patient(self, documento: str, update_data: dict) -> bool:
        """
        Actualizar información de un paciente
        """
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"documento": documento},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Patient updated successfully: {documento}")
            else:
                logger.warning(f"No patient was updated: {documento}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error updating patient {documento}: {str(e)}")
            return False

    async def delete_patient(self, documento: str) -> bool:
        """
        Eliminar un paciente (soft delete)
        """
        try:
            result = await self.collection.update_one(
                {"documento": documento},
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Patient soft deleted: {documento}")
            else:
                logger.warning(f"No patient was deleted: {documento}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error deleting patient {documento}: {str(e)}")
            return False