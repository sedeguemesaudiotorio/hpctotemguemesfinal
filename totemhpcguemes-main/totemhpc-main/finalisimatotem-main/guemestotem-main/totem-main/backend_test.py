import requests
import sys
import json
from datetime import datetime

class HospitalTotemAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")

            return success, response

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, None
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, None
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("Root Health Check", "GET", "", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health", 200)

    def test_patient_endpoints(self):
        """Test patient-related endpoints"""
        print("\n" + "="*50)
        print("TESTING PATIENT ENDPOINTS")
        print("="*50)
        
        # Test patient search with invalid document
        self.run_test("Patient Search - Invalid Document", "GET", "patients/123", 400)
        
        # Test patient search with valid but non-existent document
        self.run_test("Patient Search - Non-existent", "GET", "patients/12345678", 404)
        
        # Test get all patients
        self.run_test("Get All Patients", "GET", "patients/", 200)
        
        # Test get confirmed appointments
        self.run_test("Get Confirmed Appointments", "GET", "patients/confirmed/appointments", 200)
        
        # Test appointment confirmation with non-existent patient
        confirmation_data = {
            "documento": "12345678",
            "confirmado": True
        }
        self.run_test("Confirm Appointment - Non-existent", "POST", "patients/confirm", 404, confirmation_data)

    def test_service_endpoints(self):
        """Test service-related endpoints"""
        print("\n" + "="*50)
        print("TESTING SERVICE ENDPOINTS")
        print("="*50)
        
        # Test service log with valid data
        service_data = {
            "documento": "12345678",
            "secretaria": "pb",
            "piso": "Planta Baja"
        }
        success, response = self.run_test("Log Service Request - Valid", "POST", "services/log", 200, service_data)
        
        service_id = None
        if success and response:
            try:
                response_data = response.json()
                service_id = response_data.get('id')
            except:
                pass
        
        # Test service log with invalid document
        invalid_service_data = {
            "documento": "123",
            "secretaria": "pb",
            "piso": "Planta Baja"
        }
        self.run_test("Log Service Request - Invalid Document", "POST", "services/log", 400, invalid_service_data)
        
        # Test service log with invalid secretaria
        invalid_secretaria_data = {
            "documento": "12345678",
            "secretaria": "invalid",
            "piso": "Planta Baja"
        }
        self.run_test("Log Service Request - Invalid Secretaria", "POST", "services/log", 400, invalid_secretaria_data)
        
        # Test get service stats
        self.run_test("Get Service Stats", "GET", "services/stats", 200)
        
        # Test get recent services
        self.run_test("Get Recent Services", "GET", "services/recent", 200)
        
        # Test get recent services with limit
        self.run_test("Get Recent Services - Limited", "GET", "services/recent?limit=10", 200)
        
        # Test update service status if we have a service_id
        if service_id:
            self.run_test("Update Service Status", "PUT", f"services/{service_id}/status?estado=atendido", 200)
        
        # Test update service status with invalid status
        if service_id:
            self.run_test("Update Service Status - Invalid", "PUT", f"services/{service_id}/status?estado=invalid", 400)

    def test_secretary_options_flow(self):
        """Test the complete secretary selection flow"""
        print("\n" + "="*50)
        print("TESTING SECRETARY OPTIONS FLOW")
        print("="*50)
        
        # Test all secretary options from the frontend
        secretary_options = [
            { 'id': 'pb', 'name': 'Secretaría PB', 'floor': 'Planta Baja' },
            { 'id': 'pp', 'name': 'Secretaría PP', 'floor': 'Primer Piso' },
            { 'id': '2p', 'name': 'Secretaría 2P', 'floor': 'Segundo Piso' },
            { 'id': '3p', 'name': 'Secretaría 3P', 'floor': 'Tercer Piso' }
        ]
        
        test_document = "87654321"
        
        for option in secretary_options:
            service_data = {
                "documento": test_document,
                "secretaria": option['id'],
                "piso": option['floor']
            }
            self.run_test(f"Secretary Flow - {option['name']}", "POST", "services/log", 200, service_data)

    def run_all_tests(self):
        """Run all API tests"""
        print("🏥 Hospital Totem API Testing Started")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔗 API URL: {self.api_url}")
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_patient_endpoints()
        self.test_service_endpoints()
        self.test_secretary_options_flow()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed")
            return 1

def main():
    tester = HospitalTotemAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())