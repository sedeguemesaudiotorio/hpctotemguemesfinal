#!/usr/bin/env python3
"""
Hospital Totem API Backend Test Suite
Tests all API endpoints for the Hospital Totem application
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://7a99b684-5daa-44ea-bce8-52567bd5f76c.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {test_name} ==={Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def test_health_endpoints():
    """Test basic API connectivity and health endpoints"""
    print_test_header("Testing Health Endpoints")
    
    # Test root endpoint
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_success("GET /api/ - Root endpoint working correctly")
            else:
                print_error(f"GET /api/ - Unexpected response: {data}")
        else:
            print_error(f"GET /api/ - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/ - Connection error: {str(e)}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("service") == "Hospital Totem API":
                print_success("GET /api/health - Health endpoint working correctly")
            else:
                print_error(f"GET /api/health - Unexpected response: {data}")
        else:
            print_error(f"GET /api/health - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/health - Connection error: {str(e)}")

def test_patient_endpoints():
    """Test patient endpoints with seeded data"""
    print_test_header("Testing Patient Endpoints")
    
    # Test existing patient
    try:
        response = requests.get(f"{API_BASE}/patients/12345678", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("data", {}).get("documento") == "12345678":
                print_success("GET /api/patients/12345678 - Patient found successfully")
                print_info(f"Patient: {data['data']['nombre']} {data['data']['apellido']}")
                print_info(f"Doctor: {data['data']['turno']['medico']}")
            else:
                print_error(f"GET /api/patients/12345678 - Unexpected response: {data}")
        else:
            print_error(f"GET /api/patients/12345678 - Status code: {response.status_code}")
            if response.status_code == 404:
                print_warning("Patient not found - database may not be seeded")
    except Exception as e:
        print_error(f"GET /api/patients/12345678 - Connection error: {str(e)}")
    
    # Test another existing patient
    try:
        response = requests.get(f"{API_BASE}/patients/87654321", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("data", {}).get("documento") == "87654321":
                print_success("GET /api/patients/87654321 - Patient found successfully")
                print_info(f"Patient: {data['data']['nombre']} {data['data']['apellido']}")
            else:
                print_error(f"GET /api/patients/87654321 - Unexpected response: {data}")
        else:
            print_error(f"GET /api/patients/87654321 - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/patients/87654321 - Connection error: {str(e)}")
    
    # Test non-existent patient
    try:
        response = requests.get(f"{API_BASE}/patients/99999999", timeout=10)
        if response.status_code == 404:
            data = response.json()
            if "error" in data.get("detail", {}):
                print_success("GET /api/patients/99999999 - Correctly returns 404 for non-existent patient")
                print_info(f"Error type: {data['detail']['error']}")
            else:
                print_success("GET /api/patients/99999999 - Correctly returns 404 for non-existent patient")
        else:
            print_error(f"GET /api/patients/99999999 - Expected 404, got: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/patients/99999999 - Connection error: {str(e)}")
    
    # Test confirm appointment
    try:
        payload = {"documento": "12345678"}
        response = requests.post(f"{API_BASE}/patients/confirm", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "confirmado exitosamente" in data.get("message", ""):
                print_success("POST /api/patients/confirm - Appointment confirmed successfully")
            else:
                print_error(f"POST /api/patients/confirm - Unexpected response: {data}")
        else:
            print_error(f"POST /api/patients/confirm - Status code: {response.status_code}")
            if response.status_code == 404:
                print_warning("Patient not found for confirmation - database may not be seeded")
    except Exception as e:
        print_error(f"POST /api/patients/confirm - Connection error: {str(e)}")
    
    # Test get all patients
    try:
        response = requests.get(f"{API_BASE}/patients/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"GET /api/patients/ - Retrieved {len(data)} patients")
                if len(data) == 0:
                    print_warning("No patients found - database may not be seeded")
            else:
                print_error(f"GET /api/patients/ - Expected list, got: {type(data)}")
        else:
            print_error(f"GET /api/patients/ - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/patients/ - Connection error: {str(e)}")
    
    # Test get confirmed appointments
    try:
        response = requests.get(f"{API_BASE}/patients/confirmed/appointments", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success(f"GET /api/patients/confirmed/appointments - Retrieved {len(data)} confirmed appointments")
            else:
                print_error(f"GET /api/patients/confirmed/appointments - Expected list, got: {type(data)}")
        else:
            print_error(f"GET /api/patients/confirmed/appointments - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/patients/confirmed/appointments - Connection error: {str(e)}")

def test_service_endpoints():
    """Test service endpoints"""
    print_test_header("Testing Service Endpoints")
    
    # Test log service request
    try:
        payload = {
            "documento": "12345678",
            "secretaria": "pb",
            "piso": "Planta Baja"
        }
        response = requests.post(f"{API_BASE}/services/log", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "registrada exitosamente" in data.get("message", ""):
                print_success("POST /api/services/log - Service request logged successfully")
                print_info(f"Service ID: {data.get('id', 'N/A')}")
                print_info(f"Floor: {data.get('piso', 'N/A')}")
            else:
                print_error(f"POST /api/services/log - Unexpected response: {data}")
        else:
            print_error(f"POST /api/services/log - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"POST /api/services/log - Connection error: {str(e)}")
    
    # Test get service stats
    try:
        response = requests.get(f"{API_BASE}/services/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "total_gestiones" in data:
                print_success("GET /api/services/stats - Service stats retrieved successfully")
                print_info(f"Total services: {data.get('total_gestiones', 0)}")
                print_info(f"By secretary: {data.get('por_secretaria', {})}")
            else:
                print_error(f"GET /api/services/stats - Unexpected response structure: {data}")
        else:
            print_error(f"GET /api/services/stats - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/services/stats - Connection error: {str(e)}")
    
    # Test get recent services
    try:
        response = requests.get(f"{API_BASE}/services/recent", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "services" in data and isinstance(data["services"], list):
                print_success(f"GET /api/services/recent - Retrieved {len(data['services'])} recent services")
            else:
                print_error(f"GET /api/services/recent - Unexpected response structure: {data}")
        else:
            print_error(f"GET /api/services/recent - Status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/services/recent - Connection error: {str(e)}")

def test_cors_and_browser_compatibility():
    """Test CORS headers and browser compatibility"""
    print_test_header("Testing CORS and Browser Compatibility")
    
    try:
        # Test with browser-like headers
        headers = {
            "Origin": "https://example.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/health", headers=headers, timeout=10)
        
        # Check CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print_success("CORS headers present - API should work in browsers")
            print_info(f"Allow-Origin: {cors_headers['Access-Control-Allow-Origin']}")
            print_info(f"Allow-Methods: {cors_headers['Access-Control-Allow-Methods']}")
        else:
            print_error("CORS headers missing - API may not work in browsers")
            
    except Exception as e:
        print_error(f"CORS test failed: {str(e)}")

def test_error_handling():
    """Test error handling and validation"""
    print_test_header("Testing Error Handling")
    
    # Test invalid document number (too short)
    try:
        response = requests.get(f"{API_BASE}/patients/123", timeout=10)
        if response.status_code == 400:
            print_success("GET /api/patients/123 - Correctly validates document length")
        else:
            print_warning(f"GET /api/patients/123 - Expected 400, got: {response.status_code}")
    except Exception as e:
        print_error(f"GET /api/patients/123 - Connection error: {str(e)}")
    
    # Test invalid service log data
    try:
        payload = {
            "documento": "123",  # Too short
            "secretaria": "invalid",  # Invalid secretary
            "piso": "Test Floor"
        }
        response = requests.post(f"{API_BASE}/services/log", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        if response.status_code == 400:
            print_success("POST /api/services/log - Correctly validates input data")
        else:
            print_warning(f"POST /api/services/log - Expected 400, got: {response.status_code}")
    except Exception as e:
        print_error(f"POST /api/services/log - Connection error: {str(e)}")

def run_all_tests():
    """Run all test suites"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("    HOSPITAL TOTEM API BACKEND TEST SUITE")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    print_info(f"Testing backend at: {BACKEND_URL}")
    print_info(f"API base URL: {API_BASE}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all test suites
    test_health_endpoints()
    test_patient_endpoints()
    test_service_endpoints()
    test_cors_and_browser_compatibility()
    test_error_handling()
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("    TEST SUITE COMPLETED")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    print_info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_all_tests()