#!/usr/bin/env python3
"""
Frontend Integration Test
Tests the frontend-backend integration by simulating the user flow
"""

import requests
import json
import sys

class FrontendIntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001/api"
        self.frontend_url = "http://localhost:3000"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, message=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {message}")
        else:
            print(f"❌ {name}: FAILED {message}")

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            success = response.status_code == 200
            self.log_test("Frontend Accessibility", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Error: {str(e)}")
            return False

    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get('status') == 'healthy'
            self.log_test("Backend Health", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health", False, f"Error: {str(e)}")
            return False

    def test_patient_search_flow(self):
        """Test patient search flow (simulating frontend behavior)"""
        print("\n🔍 Testing Patient Search Flow:")
        
        # Test 1: Invalid document (too short)
        try:
            response = requests.get(f"{self.backend_url}/patients/123", timeout=5)
            success = response.status_code == 400
            self.log_test("Patient Search - Invalid Document", success, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Patient Search - Invalid Document", False, f"Error: {str(e)}")

        # Test 2: Valid document but no patient record
        try:
            response = requests.get(f"{self.backend_url}/patients/12345678", timeout=5)
            success = response.status_code == 404
            if success:
                data = response.json()
                detail = data.get('detail', {})
                success = detail.get('error') == 'no_patient_record' and detail.get('redirect') == 'other_services'
            self.log_test("Patient Search - No Record (Redirect to Other Services)", success, 
                         f"Status: {response.status_code}, Redirect: {detail.get('redirect') if success else 'N/A'}")
        except Exception as e:
            self.log_test("Patient Search - No Record", False, f"Error: {str(e)}")

    def test_service_logging_flow(self):
        """Test service logging flow (simulating OtherServices component)"""
        print("\n📋 Testing Service Logging Flow:")
        
        # Test all secretary options from the frontend
        secretary_options = [
            {'id': 'pb', 'name': 'Secretaría PB', 'floor': 'Planta Baja'},
            {'id': 'pp', 'name': 'Secretaría PP', 'floor': 'Primer Piso'},
            {'id': '2p', 'name': 'Secretaría 2P', 'floor': 'Segundo Piso'},
            {'id': '3p', 'name': 'Secretaría 3P', 'floor': 'Tercer Piso'}
        ]
        
        test_document = "87654321"
        
        for option in secretary_options:
            try:
                service_data = {
                    "documento": test_document,
                    "secretaria": option['id'],
                    "piso": option['floor']
                }
                response = requests.post(f"{self.backend_url}/services/log", 
                                       json=service_data, timeout=5)
                success = response.status_code == 200
                if success:
                    data = response.json()
                    success = 'id' in data and data.get('piso') == option['floor']
                
                self.log_test(f"Service Log - {option['name']}", success, 
                             f"Status: {response.status_code}, Floor: {data.get('piso') if success else 'N/A'}")
            except Exception as e:
                self.log_test(f"Service Log - {option['name']}", False, f"Error: {str(e)}")

    def test_service_stats(self):
        """Test service statistics endpoint"""
        print("\n📊 Testing Service Statistics:")
        
        try:
            response = requests.get(f"{self.backend_url}/services/stats", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = 'total_gestiones' in data and 'por_secretaria' in data
            
            self.log_test("Service Statistics", success, 
                         f"Status: {response.status_code}, Total: {data.get('total_gestiones') if success else 'N/A'}")
        except Exception as e:
            self.log_test("Service Statistics", False, f"Error: {str(e)}")

    def test_recent_services(self):
        """Test recent services endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/services/recent", timeout=5)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = 'services' in data and isinstance(data['services'], list)
            
            self.log_test("Recent Services", success, 
                         f"Status: {response.status_code}, Count: {len(data.get('services', [])) if success else 'N/A'}")
        except Exception as e:
            self.log_test("Recent Services", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all integration tests"""
        print("🏥 Hospital Totem Frontend-Backend Integration Testing")
        print("=" * 60)
        
        # Basic connectivity tests
        frontend_ok = self.test_frontend_accessibility()
        backend_ok = self.test_backend_health()
        
        if not backend_ok:
            print("❌ Backend is not healthy. Stopping tests.")
            return 1
        
        # Integration flow tests
        self.test_patient_search_flow()
        self.test_service_logging_flow()
        self.test_service_stats()
        self.test_recent_services()
        
        # Final results
        print("\n" + "=" * 60)
        print("INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All integration tests passed!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed")
            return 1

def main():
    tester = FrontendIntegrationTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())