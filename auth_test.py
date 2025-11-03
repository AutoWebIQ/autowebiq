#!/usr/bin/env python3
"""
CRITICAL Authentication Flow Testing for AutoWebIQ
Tests authentication after fix as requested in review:
1. POST /api/auth/register - Register new user (test123@test.com, Test123456)
2. POST /api/auth/login - Login with demo account (demo@test.com, Demo123456)
3. GET /api/auth/me - Verify token works (use token from login)

Backend URL: http://localhost:8001
Host header: api.autowebiq.com
Priority: CRITICAL - User is waiting
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Test Configuration
BACKEND_URL = "http://localhost:8001/api"
HOST_HEADER = "api.autowebiq.com"

# Test Credentials
TEST_EMAIL = "test123@test.com"
TEST_PASSWORD = "Test123456"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class AuthenticationTester:
    """Critical authentication flow tester"""
    
    def __init__(self):
        self.test_results = []
        self.demo_token = None
        self.test_user_token = None
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            print(f"✅ [{timestamp}] {name}")
        else:
            print(f"❌ [{timestamp}] {name}: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Default headers
        request_headers = {
            "Host": HOST_HEADER,
            "Content-Type": "application/json",
            "User-Agent": "AutoWebIQ-AuthTest/1.0"
        }
        
        # Add custom headers
        if headers:
            request_headers.update(headers)
        
        print(f"🔗 {method} {url}")
        print(f"   Host: {HOST_HEADER}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   Response: {response.status_code}")
            return response
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            raise
    
    def test_register_new_user(self) -> Dict:
        """Test 1: POST /api/auth/register - Register new user"""
        print(f"\n🔐 TEST 1: Register New User")
        print(f"Email: {TEST_EMAIL}")
        print(f"Password: {TEST_PASSWORD}")
        
        try:
            response = self.make_request("POST", "/auth/register", {
                "username": "TestUser123",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 400:
                # User might already exist, try to continue
                response_data = response.json()
                if "already registered" in response_data.get("detail", "").lower():
                    print(f"   ℹ️  User already exists, continuing with login test")
                    self.log_test("Register New User", True, "User already exists (acceptable)")
                    return {"success": True, "already_exists": True}
                else:
                    raise Exception(f"Registration failed: {response_data.get('detail', 'Unknown error')}")
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Verify response structure
            required_fields = ["access_token", "token_type", "user"]
            for field in required_fields:
                if field not in response_data:
                    raise Exception(f"Missing field in response: {field}")
            
            user_data = response_data["user"]
            self.test_user_token = response_data["access_token"]
            
            # Verify user data
            if user_data["email"] != TEST_EMAIL:
                raise Exception(f"Email mismatch: expected {TEST_EMAIL}, got {user_data['email']}")
            
            # Check credits (should be 20 for new users)
            credits = user_data.get("credits", 0)
            if credits != 20:
                print(f"   ⚠️  Credits: {credits} (expected 20)")
            else:
                print(f"   ✅ Credits: {credits} (correct)")
            
            print(f"   ✅ User ID: {user_data['id']}")
            print(f"   ✅ Username: {user_data['username']}")
            print(f"   ✅ Token: {self.test_user_token[:20]}...")
            
            self.log_test("Register New User", True, f"Credits: {credits}, User ID: {user_data['id']}")
            
            return {
                "success": True,
                "user_id": user_data["id"],
                "credits": credits,
                "token": self.test_user_token
            }
            
        except Exception as e:
            self.log_test("Register New User", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_demo_login(self) -> Dict:
        """Test 2: POST /api/auth/login - Login with demo account"""
        print(f"\n🔐 TEST 2: Demo Account Login")
        print(f"Email: {DEMO_EMAIL}")
        print(f"Password: {DEMO_PASSWORD}")
        
        try:
            response = self.make_request("POST", "/auth/login", {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            })
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Verify response structure
            required_fields = ["access_token", "token_type", "user"]
            for field in required_fields:
                if field not in response_data:
                    raise Exception(f"Missing field in response: {field}")
            
            user_data = response_data["user"]
            self.demo_token = response_data["access_token"]
            
            # Verify user data
            if user_data["email"] != DEMO_EMAIL:
                raise Exception(f"Email mismatch: expected {DEMO_EMAIL}, got {user_data['email']}")
            
            credits = user_data.get("credits", 0)
            
            print(f"   ✅ User ID: {user_data['id']}")
            print(f"   ✅ Username: {user_data['username']}")
            print(f"   ✅ Credits: {credits}")
            print(f"   ✅ Token: {self.demo_token[:20]}...")
            
            self.log_test("Demo Account Login", True, f"Credits: {credits}, User ID: {user_data['id']}")
            
            return {
                "success": True,
                "user_id": user_data["id"],
                "credits": credits,
                "token": self.demo_token
            }
            
        except Exception as e:
            self.log_test("Demo Account Login", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_token_verification(self) -> Dict:
        """Test 3: GET /api/auth/me - Verify token works"""
        print(f"\n🔐 TEST 3: Token Verification")
        
        if not self.demo_token:
            error = "No demo token available from login test"
            self.log_test("Token Verification", False, error)
            return {"success": False, "error": error}
        
        try:
            # Test with demo token
            response = self.make_request("GET", "/auth/me", headers={
                "Authorization": f"Bearer {self.demo_token}"
            })
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Verify response structure
            required_fields = ["id", "email", "username", "credits"]
            for field in required_fields:
                if field not in response_data:
                    raise Exception(f"Missing field in response: {field}")
            
            # Verify this matches demo account
            if response_data["email"] != DEMO_EMAIL:
                raise Exception(f"Email mismatch: expected {DEMO_EMAIL}, got {response_data['email']}")
            
            print(f"   ✅ User ID: {response_data['id']}")
            print(f"   ✅ Email: {response_data['email']}")
            print(f"   ✅ Username: {response_data['username']}")
            print(f"   ✅ Credits: {response_data['credits']}")
            print(f"   ✅ Created: {response_data.get('created_at', 'N/A')}")
            
            self.log_test("Token Verification", True, f"User: {response_data['email']}, Credits: {response_data['credits']}")
            
            return {
                "success": True,
                "user_data": response_data
            }
            
        except Exception as e:
            self.log_test("Token Verification", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_additional_token_verification(self) -> Dict:
        """Additional Test: Verify new user token also works"""
        print(f"\n🔐 ADDITIONAL TEST: New User Token Verification")
        
        if not self.test_user_token:
            print(f"   ℹ️  Skipping - no test user token available")
            return {"success": True, "skipped": True}
        
        try:
            response = self.make_request("GET", "/auth/me", headers={
                "Authorization": f"Bearer {self.test_user_token}"
            })
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Verify this matches test account
            if response_data["email"] != TEST_EMAIL:
                raise Exception(f"Email mismatch: expected {TEST_EMAIL}, got {response_data['email']}")
            
            print(f"   ✅ Test user token verified")
            print(f"   ✅ Email: {response_data['email']}")
            print(f"   ✅ Credits: {response_data['credits']}")
            
            self.log_test("New User Token Verification", True, f"User: {response_data['email']}")
            
            return {
                "success": True,
                "user_data": response_data
            }
            
        except Exception as e:
            self.log_test("New User Token Verification", False, str(e))
            return {"success": False, "error": str(e)}
    
    def run_critical_auth_test(self) -> Dict:
        """Run complete critical authentication test"""
        print(f"\n🚨 CRITICAL AUTHENTICATION FLOW TEST")
        print(f"=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Host Header: {HOST_HEADER}")
        print(f"Priority: CRITICAL - User is waiting")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "host_header": HOST_HEADER,
            "register_test": {},
            "demo_login_test": {},
            "token_verification_test": {},
            "additional_verification_test": {},
            "overall_success": False
        }
        
        try:
            # Test 1: Register new user
            register_result = self.test_register_new_user()
            results["register_test"] = register_result
            
            # Test 2: Demo login (critical)
            demo_login_result = self.test_demo_login()
            results["demo_login_test"] = demo_login_result
            
            # Test 3: Token verification (critical)
            token_verification_result = self.test_token_verification()
            results["token_verification_test"] = token_verification_result
            
            # Additional test: New user token verification
            additional_verification_result = self.test_additional_token_verification()
            results["additional_verification_test"] = additional_verification_result
            
            # Calculate overall success (critical tests must pass)
            critical_tests = [
                demo_login_result.get("success", False),
                token_verification_result.get("success", False)
            ]
            
            # Register test is important but not critical (user might exist)
            register_success = register_result.get("success", False)
            additional_success = additional_verification_result.get("success", False) or additional_verification_result.get("skipped", False)
            
            results["overall_success"] = all(critical_tests) and register_success and additional_success
            results["critical_success"] = all(critical_tests)
            results["success_rate"] = (sum(critical_tests) + int(register_success) + int(additional_success)) / 4 * 100
            
            return results
            
        except Exception as e:
            print(f"❌ Critical authentication test failed: {str(e)}")
            results["error"] = str(e)
            return results
        
        finally:
            results["test_end_time"] = datetime.now().isoformat()
            results["test_results"] = self.test_results

def main():
    """Main test execution"""
    print(f"🚨 AutoWebIQ Critical Authentication Test")
    print(f"Testing authentication flow after fix")
    
    tester = AuthenticationTester()
    results = tester.run_critical_auth_test()
    
    # Print final summary
    print(f"\n" + "=" * 60)
    print(f"🏁 CRITICAL AUTHENTICATION TEST SUMMARY")
    print(f"=" * 60)
    
    overall_success = results.get('overall_success', False)
    critical_success = results.get('critical_success', False)
    
    print(f"Overall Success: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"Critical Tests: {'✅ PASSED' if critical_success else '❌ FAILED'}")
    print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
    
    print(f"\n📊 Test Results:")
    print(f"  1. Register New User: {'✅' if results['register_test'].get('success') else '❌'}")
    print(f"  2. Demo Account Login: {'✅' if results['demo_login_test'].get('success') else '❌'} (CRITICAL)")
    print(f"  3. Token Verification: {'✅' if results['token_verification_test'].get('success') else '❌'} (CRITICAL)")
    print(f"  4. Additional Token Test: {'✅' if results['additional_verification_test'].get('success') or results['additional_verification_test'].get('skipped') else '❌'}")
    
    # Print detailed test results
    print(f"\n📋 Detailed Test Results:")
    for i, test in enumerate(tester.test_results, 1):
        status = "✅" if test['success'] else "❌"
        print(f"  {i:2d}. [{test['timestamp']}] {status} {test['test']}")
        if test['details']:
            print(f"      Details: {test['details']}")
    
    # Critical assessment
    if critical_success:
        print(f"\n🎉 CRITICAL TESTS PASSED - Authentication is working!")
        print(f"   ✅ Users can login with demo account")
        print(f"   ✅ JWT tokens are working correctly")
        print(f"   ✅ /api/auth/me endpoint is functional")
    else:
        print(f"\n🚨 CRITICAL TESTS FAILED - Authentication needs fixing!")
        if not results['demo_login_test'].get('success'):
            print(f"   ❌ Demo account login failed")
        if not results['token_verification_test'].get('success'):
            print(f"   ❌ Token verification failed")
    
    # Return exit code based on critical success
    return 0 if critical_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)