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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted: bool = False
    deleted_at: Optional[datetime] = None

class ServiceLogCreate(BaseModel):
    documento: str
    secretaria: str
    piso: str

class ServiceLogUpdate(BaseModel):
    estado: Optional[str] = None
    piso: Optional[str] = None

class ServiceStats(BaseModel):
    total_gestiones: int
    por_secretaria: dict
    por_dia: dict
    gestiones_recientes: list

class ServiceResponse(BaseModel):
    id: str
    documento: str
    secretaria: str
    piso: str
    timestamp: datetime
    estado: str
    created_at: datetime
    updated_at: datetime

class BulkStatusUpdate(BaseModel):
    service_ids: list[str]
    new_estado: str

class ServiceFilter(BaseModel):
    secretaria: Optional[str] = None
    estado: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    documento: Optional[str] = None