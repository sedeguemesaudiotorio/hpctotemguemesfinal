import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_database
from models.patient import Patient, Appointment
from datetime import datetime

async def seed_patients():
    """Seed initial patient data"""
    db = await get_database()
    
    # Clear existing data
    await db.patients.delete_many({})
    
    # Sample patient data
    patients_data = [
        {
            "documento": "12345678",
            "nombre": "Juan Carlos",
            "apellido": "Pérez",
            "turno": {
                "medico": "Dr. García",
                "hora": "10:30",
                "piso": "Primer Piso",
                "fecha": "2025-01-28",
                "especialidad": "Cardiología",
                "consultorio": "201",
                "confirmado": False
            }
        },
        {
            "documento": "87654321",
            "nombre": "María Elena",
            "apellido": "Rodriguez",
            "turno": {
                "medico": "Dra. López",
                "hora": "14:15",
                "piso": "Segundo Piso",
                "fecha": "2025-01-28",
                "especialidad": "Dermatología",
                "consultorio": "305",
                "confirmado": False
            }
        },
        {
            "documento": "11223344",
            "nombre": "Carlos Alberto",
            "apellido": "Fernández",
            "turno": {
                "medico": "Dr. Martínez",
                "hora": "09:00",
                "piso": "Planta Baja",
                "fecha": "2025-01-28",
                "especialidad": "Clínica Médica",
                "consultorio": "105",
                "confirmado": False
            }
        },
        {
            "documento": "55667788",
            "nombre": "Ana Patricia",
            "apellido": "González",
            "turno": {
                "medico": "Dra. Sánchez",
                "hora": "16:45",
                "piso": "Tercer Piso",
                "fecha": "2025-01-28",
                "especialidad": "Ginecología",
                "consultorio": "404",
                "confirmado": False
            }
        },
        {
            "documento": "99887766",
            "nombre": "Roberto José",
            "apellido": "Morales",
            "turno": {
                "medico": "Dr. Ramírez",
                "hora": "11:20",
                "piso": "Primer Piso",
                "fecha": "2025-01-28",
                "especialidad": "Traumatología",
                "consultorio": "210",
                "confirmado": False
            }
        },
        {
            "documento": "44556677",
            "nombre": "Carmen Lucía",
            "apellido": "Vega",
            "turno": {
                "medico": "Dr. Torres",
                "hora": "13:30",
                "piso": "Segundo Piso",
                "fecha": "2025-01-28",
                "especialidad": "Pediatría",
                "consultorio": "308",
                "confirmado": False
            }
        },
        {
            "documento": "33445566",
            "nombre": "Luis Fernando",
            "apellido": "Castillo",
            "turno": {
                "medico": "Dra. Herrera",
                "hora": "08:45",
                "piso": "Planta Baja",
                "fecha": "2025-01-28",
                "especialidad": "Oftalmología",
                "consultorio": "110",
                "confirmado": False
            }
        },
        {
            "documento": "77889900",
            "nombre": "Isabel María",
            "apellido": "Ruiz",
            "turno": {
                "medico": "Dr. Medina",
                "hora": "15:00",
                "piso": "Tercer Piso",
                "fecha": "2025-01-28",
                "especialidad": "Neurología",
                "consultorio": "407",
                "confirmado": False
            }
        }
    ]
    
    # Insert patients
    for patient_data in patients_data:
        patient = Patient(**patient_data)
        await db.patients.insert_one(patient.dict())
    
    print(f"✅ Seeded {len(patients_data)} patients successfully")
    
    # Create indexes
    await db.patients.create_index("documento", unique=True)
    await db.service_logs.create_index("documento")
    await db.service_logs.create_index("timestamp")
    
    print("✅ Created database indexes")

async def main():
    """Main seed function"""
    try:
        await seed_patients()
        print("🎉 Database seeding completed successfully!")
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())