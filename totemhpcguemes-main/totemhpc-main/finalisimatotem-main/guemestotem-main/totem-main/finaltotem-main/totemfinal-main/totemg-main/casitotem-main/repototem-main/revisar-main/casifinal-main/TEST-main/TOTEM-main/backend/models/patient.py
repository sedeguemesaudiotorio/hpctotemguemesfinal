from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Appointment(BaseModel):
    medico: str
    hora: str
    piso: str
    fecha: Optional[str] = None
    especialidad: Optional[str] = None
    consultorio: Optional[str] = None
    confirmado: bool = False
    fecha_confirmacion: Optional[datetime] = None

class Patient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    documento: str
    nombre: str
    apellido: str
    turno: Appointment
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PatientCreate(BaseModel):
    documento: str
    nombre: str
    apellido: str
    turno: Appointment

class PatientResponse(BaseModel):
    documento: str
    nombre: str
    apellido: str
    turno: Appointment

class AppointmentConfirmation(BaseModel):
    documento: str
    confirmado: bool = True
    fecha_confirmacion: datetime = Field(default_factory=datetime.utcnow)