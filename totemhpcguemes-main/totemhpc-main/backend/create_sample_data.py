import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample patients data
sample_patients = [
    {
        "id": str(uuid.uuid4()),
        "documento": "12345678",
        "nombre": "Juan Carlos",
        "apellido": "Pérez",
        "turno": {
            "medico": "Dr. García",
            "hora": "10:30",
            "piso": "Primer Piso",
            "fecha": "2025-07-30",
            "especialidad": "Cardiología",
            "consultorio": "101",
            "confirmado": False,
            "fecha_confirmacion": None
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "documento": "87654321",
        "nombre": "María Elena",
        "apellido": "González",
        "turno": {
            "medico": "Dra. López",
            "hora": "14:00",
            "piso": "Segundo Piso",
            "fecha": "2025-07-30",
            "especialidad": "Ginecología",
            "consultorio": "205",
            "confirmado": False,
            "fecha_confirmacion": None
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "documento": "11223344",
        "nombre": "Pedro Luis",
        "apellido": "Rodríguez",
        "turno": {
            "medico": "Dr. Martínez",
            "hora": "09:15",
            "piso": "Planta Baja",
            "fecha": "2025-07-30",
            "especialidad": "Traumatología",
            "consultorio": "15",
            "confirmado": False,
            "fecha_confirmacion": None
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

async def create_sample_data():
    # MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'hospital_totem_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Clear existing data
        await db.patients.delete_many({})
        await db.service_logs.delete_many({})
        
        # Insert sample patients
        if sample_patients:
            await db.patients.insert_many(sample_patients)
            print(f"✅ Inserted {len(sample_patients)} sample patients")
        
        # Verify insertion
        count = await db.patients.count_documents({})
        print(f"✅ Total patients in database: {count}")
        
        # List all patients for verification
        patients = await db.patients.find({}, {"documento": 1, "nombre": 1, "apellido": 1}).to_list(length=None)
        print("📋 Sample patients:")
        for patient in patients:
            print(f"   - {patient['nombre']} {patient['apellido']} (DNI: {patient['documento']})")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
