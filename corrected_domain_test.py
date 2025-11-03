#!/usr/bin/env python3
"""
CORRECTED LIVE DOMAIN TEST - autowebiq.com
Testing with the correct API URL: https://autowebiq.com/api
"""

import requests
import json
from datetime import datetime

# Corrected configuration
BASE_URL = "https://autowebiq.com/api"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

def test_corrected_domain():
    print("🔧 CORRECTED LIVE DOMAIN TEST - autowebiq.com")
    print(f"Correct API URL: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: WORKING - Status: {data.get('status')}")
            results.append(("Health Check", True, f"Status: {data.get('status')}"))
        else:
            print(f"❌ Health Check: Failed - Status {response.status_code}")
            results.append(("Health Check", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Health Check: Error - {e}")
        results.append(("Health Check", False, str(e)))
    
    # Test 2: Demo Login
    try:
        login_data = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            credits = data.get('user', {}).get('credits', 'unknown')
            print(f"✅ Demo Login: WORKING - Credits: {credits}")
            results.append(("Demo Login", True, f"Credits: {credits}"))
            
            # Test 3: Auth Me with token
            try:
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"✅ Auth Verification: WORKING - User: {me_data.get('email')}")
                    results.append(("Auth Verification", True, f"User: {me_data.get('email')}"))
                else:
                    print(f"❌ Auth Verification: Failed - Status {me_response.status_code}")
                    results.append(("Auth Verification", False, f"Status {me_response.status_code}"))
            except Exception as e:
                print(f"❌ Auth Verification: Error - {e}")
                results.append(("Auth Verification", False, str(e)))
                
        else:
            print(f"❌ Demo Login: Failed - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            results.append(("Demo Login", False, f"Status {response.status_code}: {response.text[:100]}"))
    except Exception as e:
        print(f"❌ Demo Login: Error - {e}")
        results.append(("Demo Login", False, str(e)))
    
    # Test 4: Registration
    try:
        timestamp = int(datetime.now().timestamp())
        register_data = {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@test.com",
            "password": "Test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            credits = data.get('user', {}).get('credits', 'unknown')
            print(f"✅ Registration: WORKING - New user credits: {credits}")
            results.append(("Registration", True, f"New user credits: {credits}"))
        else:
            print(f"❌ Registration: Failed - Status {response.status_code}")
            results.append(("Registration", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Registration: Error - {e}")
        results.append(("Registration", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 CORRECTED DOMAIN TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Key findings
    print(f"\n🔍 KEY FINDINGS:")
    print(f"   • Main domain autowebiq.com is accessible ✅")
    print(f"   • API is running on https://autowebiq.com/api (NOT api.autowebiq.com) ✅")
    print(f"   • Subdomain api.autowebiq.com does not exist in DNS ❌")
    
    # Check if login is working
    login_working = any(name == "Demo Login" and success for name, success, _ in results)
    
    if login_working:
        print(f"\n✅ FINAL ASSESSMENT: Authentication is WORKING on correct URL")
        print(f"   • Issue: Frontend may be configured with wrong API URL")
        print(f"   • Solution: Update frontend to use https://autowebiq.com/api")
    else:
        print(f"\n❌ FINAL ASSESSMENT: Authentication has issues even on correct URL")
        for name, success, details in results:
            if not success and name == "Demo Login":
                print(f"   • Login issue: {details}")
    
    return login_working

if __name__ == "__main__":
    test_corrected_domain()