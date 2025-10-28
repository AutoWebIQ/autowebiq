import requests
import sys
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
import os

class AutoWebIQAPITester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://webbuilder-ai-3.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.session_token = None
        self.user_id = None
        self.test_user_email = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, cookies=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, cookies=cookies)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, cookies=cookies)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, cookies=cookies)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, cookies=cookies)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_test(name, True)
                return True, response_data, response
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response_data}")
                return False, response_data, response

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}, None

    def test_jwt_auth_flow(self):
        """Test existing JWT authentication flow"""
        print("\n🔐 Testing JWT Authentication Flow")
        
        # Generate unique test user
        timestamp = int(time.time())
        test_username = f"testuser_{timestamp}"
        test_email = f"test_{timestamp}@example.com"
        test_password = "TestPass123!"
        self.test_user_email = test_email
        
        # Test registration
        success, response, _ = self.run_test(
            "JWT Registration",
            "POST",
            "auth/register",
            200,
            data={
                "username": test_username,
                "email": test_email,
                "password": test_password
            }
        )
        
        if success and 'access_token' in response:
            self.jwt_token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   JWT Token: {self.jwt_token[:20]}...")
            
            # Test login
            success, response, _ = self.run_test(
                "JWT Login",
                "POST",
                "auth/login",
                200,
                data={
                    "email": test_email,
                    "password": test_password
                }
            )
            
            if success and 'access_token' in response:
                # Test /auth/me with JWT
                success, response, _ = self.run_test(
                    "Get User Info (JWT)",
                    "GET",
                    "auth/me",
                    200,
                    headers={"Authorization": f"Bearer {self.jwt_token}"}
                )
                return success
        
        return False

    def create_test_session_in_db(self):
        """Create test user and session directly in MongoDB using mongosh"""
        print("\n🗄️ Creating Test Session in MongoDB")
        
        # Generate test data
        user_id = f"oauth-user-{int(time.time())}"
        session_token = f"test_session_{int(time.time())}"
        test_email = f"oauth_{int(time.time())}@gmail.com"
        
        # MongoDB script to create test user and session
        mongo_script = f'''
use('autowebiq_db');
db.users.insertOne({{
  id: "{user_id}",
  username: "OAuth Test User",
  email: "{test_email}",
  password_hash: "",
  credits: 50,
  picture: "https://via.placeholder.com/150",
  auth_provider: "google",
  created_at: new Date().toISOString()
}});
db.user_sessions.insertOne({{
  id: "{str(uuid.uuid4())}",
  user_id: "{user_id}",
  session_token: "{session_token}",
  expires_at: new Date(Date.now() + 7*24*60*60*1000),
  created_at: new Date().toISOString()
}});
print("Test session created successfully");
print("Session token: {session_token}");
print("User ID: {user_id}");
'''
        
        try:
            # Write script to temp file and execute
            with open('/tmp/create_test_session.js', 'w') as f:
                f.write(mongo_script)
            
            import subprocess
            result = subprocess.run(['mongosh', '--file', '/tmp/create_test_session.js'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.session_token = session_token
                self.user_id = user_id
                print(f"   ✅ Test session created: {session_token[:20]}...")
                return True
            else:
                print(f"   ❌ MongoDB script failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to create test session: {str(e)}")
            return False

    def test_google_oauth_session_endpoint(self):
        """Test POST /api/auth/google/session endpoint"""
        print("\n🔗 Testing Google OAuth Session Endpoint")
        
        # This endpoint requires a real session_id from Google OAuth
        # Since we can't get a real one, we'll test the error handling
        success, response, _ = self.run_test(
            "Google OAuth Session (No Session ID)",
            "POST",
            "auth/google/session",
            400  # Should return 400 for missing session ID
        )
        
        # Test with invalid session ID
        success, response, _ = self.run_test(
            "Google OAuth Session (Invalid Session ID)",
            "POST",
            "auth/google/session",
            400,  # Should return 400 for invalid session ID
            headers={"X-Session-ID": "invalid_session_id_123"}
        )
        
        return True  # These tests are expected to fail with 400, which is correct behavior

    def test_auth_me_with_session_token(self):
        """Test GET /api/auth/me with session token"""
        print("\n👤 Testing /auth/me with Session Token")
        
        if not self.session_token:
            print("   ⚠️ No session token available, skipping test")
            return False
        
        # Test with session token in Authorization header
        success, response, _ = self.run_test(
            "Get User Info (Session Token - Header)",
            "GET",
            "auth/me",
            200,
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        
        if success:
            # Test with session token in cookie
            success, response, _ = self.run_test(
                "Get User Info (Session Token - Cookie)",
                "GET",
                "auth/me",
                200,
                cookies={"session_token": self.session_token}
            )
        
        return success

    def test_logout_endpoint(self):
        """Test POST /api/auth/logout endpoint"""
        print("\n🚪 Testing Logout Endpoint")
        
        if not self.session_token:
            print("   ⚠️ No session token available, skipping test")
            return False
        
        # Test logout with session token cookie
        success, response, resp_obj = self.run_test(
            "Logout (Session Token)",
            "POST",
            "auth/logout",
            200,
            cookies={"session_token": self.session_token}
        )
        
        if success:
            # Verify session is deleted by trying to use it again
            success, response, _ = self.run_test(
                "Verify Session Deleted",
                "GET",
                "auth/me",
                401,  # Should return 401 after logout
                cookies={"session_token": self.session_token}
            )
            return success
        
        return False

    def test_flexible_auth_system(self):
        """Test that the system supports both JWT and session tokens"""
        print("\n🔄 Testing Flexible Authentication System")
        
        # Test JWT auth still works
        if self.jwt_token:
            success, response, _ = self.run_test(
                "JWT Auth Still Works",
                "GET",
                "auth/me",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            if not success:
                return False
        
        # Test invalid token handling
        success, response, _ = self.run_test(
            "Invalid JWT Token",
            "GET",
            "auth/me",
            401,
            headers={"Authorization": "Bearer invalid_jwt_token"}
        )
        
        # Test no auth
        success, response, _ = self.run_test(
            "No Authentication",
            "GET",
            "auth/me",
            401
        )
        
        return True

    def test_protected_endpoints(self):
        """Test that protected endpoints work with both auth methods"""
        print("\n🛡️ Testing Protected Endpoints")
        
        # Test projects endpoint with JWT
        if self.jwt_token:
            success, response, _ = self.run_test(
                "Get Projects (JWT)",
                "GET",
                "projects",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            if not success:
                return False
        
        return True

    def cleanup_test_data(self):
        """Clean up test data from MongoDB"""
        print("\n🧹 Cleaning Up Test Data")
        
        mongo_script = f'''
use autowebiq_db;
db.users.deleteMany({{email: /test_.*@example\\.com/}});
db.users.deleteMany({{email: /oauth_.*@gmail\\.com/}});
db.user_sessions.deleteMany({{session_token: /test_session/}});
print("Test data cleaned up");
'''
        
        try:
            with open('/tmp/cleanup_test_data.js', 'w') as f:
                f.write(mongo_script)
            
            import subprocess
            result = subprocess.run(['mongosh', '--file', '/tmp/cleanup_test_data.js'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Test data cleaned up successfully")
            else:
                print(f"   ⚠️ Cleanup warning: {result.stderr}")
                
        except Exception as e:
            print(f"   ⚠️ Cleanup failed: {str(e)}")

    def run_all_tests(self):
        """Run all Google OAuth authentication tests"""
        print("🚀 Starting AutoWebIQ Google OAuth API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 70)

        # Test 1: Existing JWT auth flow
        if not self.test_jwt_auth_flow():
            print("❌ JWT authentication failed, but continuing with OAuth tests")

        # Test 2: Create test session in MongoDB
        if not self.create_test_session_in_db():
            print("❌ Failed to create test session, skipping session-based tests")
            return False

        # Test 3: Google OAuth session endpoint (error handling)
        self.test_google_oauth_session_endpoint()

        # Test 4: /auth/me with session token
        self.test_auth_me_with_session_token()

        # Test 5: Logout endpoint
        self.test_logout_endpoint()

        # Test 6: Flexible auth system
        self.test_flexible_auth_system()

        # Test 7: Protected endpoints
        self.test_protected_endpoints()

        # Cleanup
        self.cleanup_test_data()

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 GOOGLE OAUTH TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AutoWebIQAPITester()
    
    try:
        success = tester.run_all_tests()
        all_passed = tester.print_summary()
        return 0 if all_passed else 1
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())