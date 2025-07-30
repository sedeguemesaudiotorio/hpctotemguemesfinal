#!/usr/bin/env python3
"""
Script para configurar datos de prueba en la base de datos
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

async def setup_test_data():
    """Configurar datos de prueba"""
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🚀 Configurando datos de prueba...")
    
    # Clear existing data
    await db.patients.delete_many({})
    await db.service_logs.delete_many({})
    print("📭 Base de datos limpiada")
    
    # Test patients data
    test_patients = [
        {
            "id": "patient-001",
            "documento": "1234567",
            "nombre": "Juan Carlos",
            "apellido": "Pérez",
            "turno": {
                "medico": "Dr. López",
                "hora": "10:30",
                "piso": "Primer Piso",
                "fecha": "2025-01-15",
                "especialidad": "Cardiología",
                "consultorio": "201",
                "confirmado": False,
                "fecha_confirmacion": None
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "patient-002", 
            "documento": "7654321",
            "nombre": "María Elena",
            "apellido": "González",
            "turno": {
                "medico": "Dra. Martínez",
                "hora": "14:00",
                "piso": "Segundo Piso",
                "fecha": "2025-01-15",
                "especialidad": "Ginecología",
                "consultorio": "305",
                "confirmado": True,
                "fecha_confirmacion": datetime.utcnow() - timedelta(hours=1)
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "patient-003",
            "documento": "9876543", 
            "nombre": "Roberto",
            "apellido": "Silva",
            "turno": {
                "medico": "Dr. Rodríguez",
                "hora": "09:15",
                "piso": "Planta Baja",
                "fecha": "2025-01-16",
                "especialidad": "Traumatología",
                "consultorio": "105",
                "confirmado": False,
                "fecha_confirmacion": None
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert test patients
    await db.patients.insert_many(test_patients)
    print(f"👥 {len(test_patients)} pacientes de prueba creados")
    
    # Test service logs
    test_service_logs = [
        {
            "id": "service-001",
            "documento": "1111111",
            "secretaria": "pb",
            "piso": "Planta Baja",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "estado": "atendido"
        },
        {
            "id": "service-002",
            "documento": "2222222", 
            "secretaria": "pp",
            "piso": "Primer Piso",
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "estado": "pendiente"
        },
        {
            "id": "service-003",
            "documento": "3333333",
            "secretaria": "2p", 
            "piso": "Segundo Piso",
            "timestamp": datetime.utcnow() - timedelta(minutes=30),
            "estado": "pendiente"
        }
    ]
    
    # Insert test service logs
    await db.service_logs.insert_many(test_service_logs)
    print(f"📊 {len(test_service_logs)} registros de servicio de prueba creados")
    
    print("✅ Datos de prueba configurados exitosamente!")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_test_data())