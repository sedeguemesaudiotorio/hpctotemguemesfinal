import requests
import sys
from datetime import datetime
import json

class HospitalTotemAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_response_keys=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check response structure if specified
                if expected_response_keys:
                    try:
                        response_data = response.json()
                        for key in expected_response_keys:
                            if key not in response_data:
                                print(f"⚠️  Warning: Expected key '{key}' not found in response")
                            else:
                                print(f"   ✓ Found expected key: {key}")
                    except:
                        print("   ⚠️  Could not parse JSON response")
                
                return True, response.json() if response.content else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        print(f"   Error details: {error_data}")
                    except:
                        print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH ENDPOINTS")
        print("="*50)
        
        # Test root health endpoint
        self.run_test(
            "Root Health Check",
            "GET",
            "",
            200,
            expected_response_keys=["message", "status"]
        )
        
        # Test specific health endpoint
        self.run_test(
            "Health Check Endpoint",
            "GET",
            "health",
            200,
            expected_response_keys=["status", "service", "version"]
        )

    def test_patient_endpoints(self):
        """Test patient-related endpoints"""
        print("\n" + "="*50)
        print("TESTING PATIENT ENDPOINTS")
        print("="*50)
        
        # Test with existing patient (should have appointment)
        print("\n--- Testing with existing patient (12345678) ---")
        success, response = self.run_test(
            "Get Patient with Appointment (12345678)",
            "GET",
            "patients/12345678",
            200,
            expected_response_keys=["status", "data"]
        )
        
        if success and "data" in response:
            patient_data = response["data"]
            print(f"   Patient: {patient_data.get('nombre', 'N/A')} {patient_data.get('apellido', 'N/A')}")
            if "turno" in patient_data:
                turno = patient_data["turno"]
                print(f"   Appointment: Dr. {turno.get('medico', 'N/A')} at {turno.get('hora', 'N/A')} - Floor: {turno.get('piso', 'N/A')}")
        
        # Test with another existing patient
        print("\n--- Testing with existing patient (87654321) ---")
        self.run_test(
            "Get Patient with Appointment (87654321)",
            "GET",
            "patients/87654321",
            200,
            expected_response_keys=["status", "data"]
        )
        
        # Test with third existing patient
        print("\n--- Testing with existing patient (11223344) ---")
        self.run_test(
            "Get Patient with Appointment (11223344)",
            "GET",
            "patients/11223344",
            200,
            expected_response_keys=["status", "data"]
        )
        
        # Test with non-existing patient (should redirect to other services)
        print("\n--- Testing with non-existing patient (99999999) ---")
        self.run_test(
            "Get Non-existing Patient (99999999)",
            "GET",
            "patients/99999999",
            404  # Should return 404 for non-existing patients
        )
        
        # Test invalid document format
        print("\n--- Testing with invalid document format ---")
        self.run_test(
            "Get Patient with Invalid Document (123)",
            "GET",
            "patients/123",
            400  # Should return 400 for invalid document format
        )
        
        # Test appointment confirmation
        print("\n--- Testing appointment confirmation ---")
        self.run_test(
            "Confirm Appointment (12345678)",
            "POST",
            "patients/confirm",
            200,
            data={"documento": "12345678", "confirmado": True},
            expected_response_keys=["message", "documento"]
        )
        
        # Test get all patients (admin endpoint)
        print("\n--- Testing admin endpoints ---")
        self.run_test(
            "Get All Patients (Admin)",
            "GET",
            "patients/",
            200
        )
        
        # Test get confirmed appointments
        self.run_test(
            "Get Confirmed Appointments",
            "GET",
            "patients/confirmed/appointments",
            200
        )

    def test_service_endpoints(self):
        """Test service-related endpoints"""
        print("\n" + "="*50)
        print("TESTING SERVICE ENDPOINTS")
        print("="*50)
        
        # Test logging service request for each secretary
        secretaries = [
            {"id": "pb", "floor": "Planta Baja"},
            {"id": "pp", "floor": "Primer Piso"},
            {"id": "2p", "floor": "Segundo Piso"},
            {"id": "3p", "floor": "Tercer Piso"}
        ]
        
        for secretary in secretaries:
            print(f"\n--- Testing service request for {secretary['id'].upper()} ---")
            success, response = self.run_test(
                f"Log Service Request ({secretary['id'].upper()})",
                "POST",
                "services/log",
                200,
                data={
                    "documento": "99999999",
                    "secretaria": secretary["id"],
                    "piso": secretary["floor"]
                },
                expected_response_keys=["message", "id", "piso", "timestamp"]
            )
            
            if success and "id" in response:
                service_id = response["id"]
                print(f"   Service ID: {service_id}")
                
                # Test updating service status
                print(f"   Testing status update for service {service_id}")
                self.run_test(
                    f"Update Service Status ({secretary['id'].upper()})",
                    "PUT",
                    f"services/{service_id}/status",
                    200,
                    data={"estado": "atendido"},
                    expected_response_keys=["message"]
                )
        
        # Test invalid secretary
        print("\n--- Testing invalid secretary ---")
        self.run_test(
            "Log Service Request (Invalid Secretary)",
            "POST",
            "services/log",
            400,  # Should return 400 for invalid secretary
            data={
                "documento": "99999999",
                "secretaria": "invalid",
                "piso": "Invalid Floor"
            }
        )
        
        # Test invalid document
        print("\n--- Testing invalid document for service ---")
        self.run_test(
            "Log Service Request (Invalid Document)",
            "POST",
            "services/log",
            400,  # Should return 400 for invalid document
            data={
                "documento": "123",
                "secretaria": "pb",
                "piso": "Planta Baja"
            }
        )
        
        # Test service statistics
        print("\n--- Testing service statistics ---")
        self.run_test(
            "Get Service Statistics",
            "GET",
            "services/stats",
            200
        )
        
        # Test recent services
        self.run_test(
            "Get Recent Services",
            "GET",
            "services/recent?limit=10",
            200,
            expected_response_keys=["services"]
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🏥 HOSPITAL TOTEM API TESTING")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("="*60)
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_patient_endpoints()
        self.test_service_endpoints()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            failed = self.tests_run - self.tests_passed
            print(f"❌ {failed} test(s) failed")
            return 1

def main():
    tester = HospitalTotemAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())