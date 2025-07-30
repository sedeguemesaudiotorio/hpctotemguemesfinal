from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class ServiceLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    documento: str
    secretaria: str  # 'pb', 'pp', '2p', '3p'
    piso: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    estado: str = "pendiente"  # pendiente, atendido, cancelado

class ServiceLogCreate(BaseModel):
    documento: str
    secretaria: str
    piso: str

class ServiceStats(BaseModel):
    total_gestiones: int
    por_secretaria: dict
    por_dia: dict
    gestiones_recientes: list