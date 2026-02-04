"""
Quick test script to verify the Flask app setup
Run this after starting the Flask server to test endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_server():
    """Test if server is running"""
    try:
        response = requests.get(BASE_URL)
        print("✅ Server is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: python app.py")
        return False

def test_register_doctor():
    """Test doctor registration"""
    data = {
        "name": "Dr. Test Smith",
        "email": "doctor_test@example.com",
        "password": "doctor123",
        "role": "doctor"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=data)
    print(f"\nDoctor Registration: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get('success', False)

def test_register_patient():
    """Test patient registration"""
    data = {
        "name": "John Patient",
        "email": "patient_test@example.com",
        "password": "patient123",
        "role": "patient"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=data)
    print(f"\nPatient Registration: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get('success', False)

def test_login(email, password):
    """Test login"""
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=data)
    print(f"\nLogin ({email}): {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_get_doctors(session):
    """Test getting doctor list"""
    response = session.get(f"{BASE_URL}/api/doctors")
    print(f"\nGet Doctors: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("=" * 50)
    print("Flask App Test Suite")
    print("=" * 50)
    
    if not test_server():
        exit(1)
    
    print("\n" + "=" * 50)
    print("Testing Registration")
    print("=" * 50)
    
    # Create session for maintaining cookies
    session = requests.Session()
    
    # Test registrations
    test_register_doctor()
    test_register_patient()
    
    print("\n" + "=" * 50)
    print("Testing Login")
    print("=" * 50)
    
    # Test login
    test_login("doctor_test@example.com", "doctor123")
    
    # Login as patient and get doctors
    patient_session = requests.Session()
    response = patient_session.post(f"{BASE_URL}/api/login", json={
        "email": "patient_test@example.com",
        "password": "patient123"
    })
    
    if response.json().get('success'):
        test_get_doctors(patient_session)
    
    print("\n" + "=" * 50)
    print("✅ Basic tests completed!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Register a doctor account")
    print("3. Register a patient account (use incognito/different browser)")
    print("4. Patient: Click on doctor to start chat")
    print("5. Test the translation and summary features")
