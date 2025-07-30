import requests
import sys
from datetime import datetime
import json

class HospitalTotemAPITester:
    def __init__(self, base_url="https://c231ba2c-8673-4052-8786-1c01935be265.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"   Response: {response.text}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        
        # Test root health endpoint
        self.run_test("Root Health Check", "GET", "api/", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "api/health", 200)

    def test_patient_endpoints(self):
        """Test patient-related endpoints"""
        print("\n=== TESTING PATIENT ENDPOINTS ===")
        
        # Test invalid document (less than 7 digits)
        self.run_test("Invalid Document (Short)", "GET", "api/patients/123456", 400)
        
        # Test non-existent patient
        self.run_test("Non-existent Patient", "GET", "api/patients/12345678", 404)
        
        # Test get all patients
        self.run_test("Get All Patients", "GET", "api/patients/", 200)
        
        # Test get confirmed appointments
        self.run_test("Get Confirmed Appointments", "GET", "api/patients/confirmed/appointments", 200)
        
        # Test create patient
        patient_data = {
            "documento": "87654321",
            "nombre": "Juan",
            "apellido": "Pérez",
            "turno": {
                "medico": "Dr. García",
                "especialidad": "Cardiología",
                "fecha": "2025-02-15",
                "hora": "10:00",
                "piso": "2p"
            }
        }
        success, response = self.run_test("Create Patient", "POST", "api/patients/", 200, patient_data)
        
        if success:
            # Test finding the created patient
            self.run_test("Find Created Patient", "GET", "api/patients/87654321", 200)
            
            # Test confirm appointment
            confirm_data = {"documento": "87654321"}
            self.run_test("Confirm Appointment", "POST", "api/patients/confirm", 200, confirm_data)

    def test_service_endpoints(self):
        """Test service-related endpoints"""
        print("\n=== TESTING SERVICE ENDPOINTS ===")
        
        # Test invalid document for service log
        service_data_invalid = {
            "documento": "123456",  # Less than 7 digits
            "servicio_id": "consulta_general",
            "secretaria": "pb",
            "piso": "Planta Baja"
        }
        self.run_test("Service Log - Invalid Document", "POST", "api/services/log", 400, service_data_invalid)
        
        # Test invalid secretaria
        service_data_invalid_sec = {
            "documento": "12345678",
            "servicio_id": "consulta_general",
            "secretaria": "invalid",  # Invalid secretaria
            "piso": "Planta Baja"
        }
        self.run_test("Service Log - Invalid Secretaria", "POST", "api/services/log", 400, service_data_invalid_sec)
        
        # Test valid service log
        service_data_valid = {
            "documento": "12345678",
            "servicio_id": "consulta_general",
            "secretaria": "pb",
            "piso": "Planta Baja"
        }
        success, response = self.run_test("Service Log - Valid", "POST", "api/services/log", 200, service_data_valid)
        
        # Test get service stats
        self.run_test("Get Service Stats", "GET", "api/services/stats", 200)
        
        # Test get recent services
        self.run_test("Get Recent Services", "GET", "api/services/recent", 200)
        
        if success and isinstance(response, dict) and 'id' in response:
            service_id = response['id']
            # Test update service status
            self.run_test("Update Service Status", "PUT", f"api/services/{service_id}/status?estado=atendido", 200)

def main():
    print("🏥 Hospital Totem API Testing Suite")
    print("=" * 50)
    
    # Setup
    tester = HospitalTotemAPITester()
    
    # Run all tests
    tester.test_health_endpoints()
    tester.test_patient_endpoints()
    tester.test_service_endpoints()
    
    # Print final results
    print(f"\n📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())