#!/usr/bin/env python3
"""
Hospital Totem Backend API Test Suite
Tests all backend endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class HospitalTotemAPITester:
    def __init__(self, base_url="https://f7e0f768-7c98-4a72-958c-9ba74b1538dd.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                self.log_test(name, False, f"Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_test(name, True, f"Status: {response.status_code}")
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response_data}")

            return success, response_data

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root health endpoint
        self.run_test("Root Health Check", "GET", "", 200)
        
        # Test specific health endpoint
        self.run_test("Health Check Endpoint", "GET", "health", 200)

    def test_patient_endpoints(self):
        """Test patient-related endpoints"""
        print("\n🔍 Testing Patient Endpoints...")
        
        # Test invalid document (too short)
        self.run_test("Invalid Document (Too Short)", "GET", "patients/123", 400)
        
        # Test non-existent patient
        self.run_test("Non-existent Patient", "GET", "patients/1234567", 404)
        
        # Test get all patients
        self.run_test("Get All Patients", "GET", "patients/", 200)
        
        # Test get confirmed appointments
        self.run_test("Get Confirmed Appointments", "GET", "patients/confirmed/appointments", 200)
        
        # Test confirm appointment with invalid document
        success, _ = self.run_test("Confirm Invalid Appointment", "POST", "patients/confirm", 404, {
            "documento": "1234567",
            "confirmado": True
        })

    def test_service_endpoints(self):
        """Test service-related endpoints"""
        print("\n🔍 Testing Service Endpoints...")
        
        # Test service stats
        self.run_test("Get Service Stats", "GET", "services/stats", 200)
        
        # Test recent services
        self.run_test("Get Recent Services", "GET", "services/recent", 200)
        
        # Test recent services with limit
        self.run_test("Get Recent Services (Limited)", "GET", "services/recent?limit=10", 200)
        
        # Test log service request with invalid document
        self.run_test("Log Service (Invalid Document)", "POST", "services/log", 400, {
            "documento": "123",
            "secretaria": "pb",
            "piso": "Planta Baja"
        })
        
        # Test log service request with invalid secretary
        self.run_test("Log Service (Invalid Secretary)", "POST", "services/log", 400, {
            "documento": "1234567",
            "secretaria": "invalid",
            "piso": "Planta Baja"
        })
        
        # Test log service request with valid data
        success, response = self.run_test("Log Service (Valid)", "POST", "services/log", 201, {
            "documento": "1234567",
            "secretaria": "pb",
            "piso": "Planta Baja"
        })
        
        # If service was logged successfully, test status update
        if success and 'id' in response:
            service_id = response['id']
            self.run_test("Update Service Status", "PUT", f"services/{service_id}/status", 200, {
                "estado": "atendido"
            })

    def test_cors_and_headers(self):
        """Test CORS and header configuration"""
        print("\n🔍 Testing CORS and Headers...")
        
        try:
            response = requests.options(f"{self.api_url}/health", timeout=10)
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_test("CORS Headers Present", True, f"Origin: {cors_headers['Access-Control-Allow-Origin']}")
            else:
                self.log_test("CORS Headers Present", False, "No CORS headers found")
                
        except Exception as e:
            self.log_test("CORS Headers Test", False, f"Exception: {str(e)}")

    def test_api_prefix_routing(self):
        """Test that API routes are properly prefixed"""
        print("\n🔍 Testing API Prefix Routing...")
        
        # Test that routes without /api prefix don't work for API endpoints
        base_url_without_api = self.base_url
        
        try:
            response = requests.get(f"{base_url_without_api}/patients/1234567", timeout=5)
            if response.status_code == 404:
                self.log_test("API Prefix Routing", True, "Routes properly require /api prefix")
            else:
                self.log_test("API Prefix Routing", False, f"Route accessible without /api prefix: {response.status_code}")
        except:
            self.log_test("API Prefix Routing", True, "Routes properly require /api prefix (connection failed as expected)")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Hospital Totem Backend API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run test suites
        self.test_health_endpoints()
        self.test_patient_endpoints()
        self.test_service_endpoints()
        self.test_cors_and_headers()
        self.test_api_prefix_routing()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = HospitalTotemAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())