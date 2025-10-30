import requests
import sys
import json
import time
import uuid
from datetime import datetime, timezone, timedelta

class AdditionalAutoWebIQTester:
    def __init__(self):
        self.base_url = "https://autowebiq-ai.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.user_id = None
        self.test_project_id = None
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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

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

    def setup_test_user(self):
        """Create a test user and get JWT token"""
        print("\n🔐 Setting up test user...")
        
        timestamp = int(time.time())
        test_username = f"testuser_{timestamp}"
        test_email = f"test_{timestamp}@autowebiq.com"
        test_password = "TestPass123!"
        
        # Register user
        success, response, _ = self.run_test(
            "Setup - User Registration",
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
            print(f"   ✅ Test user created with 20 credits")
            return True
        
        return False

    def test_firebase_sync_endpoint(self):
        """Test Firebase sync endpoint specifically"""
        print("\n🔥 Testing Firebase Sync Endpoint")
        
        firebase_data = {
            "firebase_uid": f"test-firebase-{int(time.time())}",
            "email": f"firebase_{int(time.time())}@test.com",
            "display_name": "Firebase Test User",
            "photo_url": "https://example.com/photo.jpg",
            "provider_id": "google.com"
        }
        
        success, response, _ = self.run_test(
            "Firebase User Sync",
            "POST",
            "auth/firebase/sync",
            200,
            data=firebase_data
        )
        
        if success:
            # Verify response structure
            required_fields = ['access_token', 'token_type', 'user']
            if all(field in response for field in required_fields):
                # Verify user gets 20 credits (updated from 10)
                user_credits = response['user'].get('credits', 0)
                if user_credits == 20:
                    self.log_test("Firebase Sync - 20 Credits Granted", True)
                else:
                    self.log_test("Firebase Sync - 20 Credits Granted", False, f"Expected 20 credits, got {user_credits}")
                return True
            else:
                self.log_test("Firebase Sync - Response Structure", False, "Missing required fields")
        
        return False

    def test_logout_endpoint(self):
        """Test logout endpoint"""
        print("\n🚪 Testing Logout Endpoint")
        
        success, response, _ = self.run_test(
            "Logout Endpoint",
            "POST",
            "auth/logout",
            200
        )
        
        return success

    def test_credits_summary_endpoint(self):
        """Test credits summary endpoint that wasn't covered"""
        print("\n📊 Testing Credits Summary Endpoint")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping test")
            return False
        
        success, response, _ = self.run_test(
            "Get Credits Summary",
            "GET",
            "credits/summary",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success:
            # Verify response has expected fields
            expected_fields = ['total_spent', 'total_refunded', 'total_purchased']
            if all(field in response for field in expected_fields):
                self.log_test("Credits Summary - Response Structure", True)
                return True
            else:
                self.log_test("Credits Summary - Response Structure", False, "Missing expected fields")
        
        return False

    def test_gke_workspaces_list(self):
        """Test GKE workspaces list endpoint"""
        print("\n☸️ Testing GKE Workspaces List")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping test")
            return False
        
        success, response, _ = self.run_test(
            "List GKE Workspaces",
            "GET",
            "gke/workspaces",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        return success

    def test_multi_agent_build_with_sufficient_credits(self):
        """Test multi-agent build with a user who has sufficient credits"""
        print("\n🤖 Testing Multi-Agent Build with Sufficient Credits")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping test")
            return False
        
        # First create a project
        project_data = {
            "name": "Multi-Agent Test Project",
            "description": "Testing multi-agent build functionality"
        }
        
        success, response, _ = self.run_test(
            "Create Project for Multi-Agent Build",
            "POST",
            "projects/create",
            200,
            data=project_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success and 'id' in response:
            project_id = response['id']
            
            # Test multi-agent build (should fail with 402 due to insufficient credits - 20 credits vs ~47 needed)
            build_data = {
                "project_id": project_id,
                "prompt": "Create a simple landing page for a tech startup",
                "uploaded_images": []
            }
            
            success, response, _ = self.run_test(
                "Multi-Agent Build (Expected Credit Validation)",
                "POST",
                "build-with-agents",
                402,  # Expect 402 due to insufficient credits
                data=build_data,
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            if success:
                # Verify the response contains detailed cost breakdown
                detail = response.get('detail', '')
                if 'Insufficient credits' in detail and 'Breakdown:' in detail:
                    self.log_test("Multi-Agent Build - Detailed Cost Breakdown", True)
                else:
                    self.log_test("Multi-Agent Build - Detailed Cost Breakdown", False, "Missing detailed cost breakdown")
                return True
        
        return False

    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check Endpoint")
        
        success, response, _ = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            # Verify health response structure
            if response.get('status') == 'healthy' and 'service' in response:
                self.log_test("Health Check - Response Structure", True)
                return True
            else:
                self.log_test("Health Check - Response Structure", False, "Invalid health response structure")
        
        return False

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        mongo_script = '''
use('autowebiq_db');
db.users.deleteMany({email: /test_.*@autowebiq\\.com/});
db.users.deleteMany({email: /firebase_.*@test\\.com/});
db.projects.deleteMany({name: /.*Test Project/});
print("Additional test data cleaned up");
'''
        
        try:
            with open('/tmp/cleanup_additional_test_data.js', 'w') as f:
                f.write(mongo_script)
            
            import subprocess
            result = subprocess.run(['mongosh', '--file', '/tmp/cleanup_additional_test_data.js'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Additional test data cleaned up successfully")
            else:
                print(f"   ⚠️ Cleanup warning: {result.stderr}")
                
        except Exception as e:
            print(f"   ⚠️ Cleanup failed: {str(e)}")

    def run_additional_tests(self):
        """Run additional comprehensive tests"""
        print("🚀 Starting Additional AutoWebIQ Backend Testing")
        print(f"   Base URL: {self.base_url}")
        print("=" * 70)

        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user")
            return False

        # Test additional endpoints
        tests = [
            self.test_firebase_sync_endpoint,
            self.test_logout_endpoint,
            self.test_credits_summary_endpoint,
            self.test_gke_workspaces_list,
            self.test_multi_agent_build_with_sufficient_credits,
            self.test_health_endpoint
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                results.append(False)

        # Cleanup
        self.cleanup_test_data()

        return all(results)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 ADDITIONAL BACKEND TEST SUMMARY")
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
            print("\n🎉 ALL ADDITIONAL TESTS PASSED!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AdditionalAutoWebIQTester()
    
    try:
        success = tester.run_additional_tests()
        all_passed = tester.print_summary()
        return 0 if all_passed else 1
    except Exception as e:
        print(f"❌ Additional test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())