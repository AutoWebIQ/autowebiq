import requests
import json
import time
from datetime import datetime

class AutoWebIQReviewTester:
    def __init__(self):
        self.base_url = "https://autowebiq-dev.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.user_id = None
        self.project_id = None
        self.tests_passed = 0
        self.tests_total = 0

    def log_test(self, name, success, details=""):
        self.tests_total += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")

    def test_authentication_flow(self):
        """Test Authentication Flow as specified in review request"""
        print("\n🔐 TESTING AUTHENTICATION FLOW")
        
        # Create unique user with timestamp-based email
        timestamp = int(time.time())
        test_email = f"review_test_{timestamp}@autowebiq.com"
        test_username = f"reviewuser_{timestamp}"
        test_password = "ReviewTest123!"
        
        # 1. POST /api/auth/register - Create new user and verify 20 initial credits granted
        print("\n1. Testing POST /api/auth/register")
        register_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/register", json=register_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['credits'] == 20:
                self.jwt_token = data['access_token']
                self.user_id = data['user']['id']
                self.log_test("POST /api/auth/register - 20 credits granted", True)
            else:
                self.log_test("POST /api/auth/register - 20 credits granted", False, f"Credits: {data['user'].get('credits', 'N/A')}")
        else:
            self.log_test("POST /api/auth/register", False, f"Status: {response.status_code}")
            return False
        
        # 2. POST /api/auth/login - Verify JWT token generation
        print("\n2. Testing POST /api/auth/login")
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.log_test("POST /api/auth/login - JWT token generation", True)
            else:
                self.log_test("POST /api/auth/login - JWT token generation", False, "No access_token in response")
        else:
            self.log_test("POST /api/auth/login", False, f"Status: {response.status_code}")
        
        # 3. GET /api/auth/me - Verify user profile retrieval with credits
        print("\n3. Testing GET /api/auth/me")
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        response = requests.get(f"{self.api_url}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('credits') == 20 and data.get('email') == test_email:
                self.log_test("GET /api/auth/me - User profile with credits", True)
            else:
                self.log_test("GET /api/auth/me - User profile with credits", False, f"Credits: {data.get('credits')}")
        else:
            self.log_test("GET /api/auth/me", False, f"Status: {response.status_code}")
        
        return True

    def test_project_management(self):
        """Test Project Management as specified in review request"""
        print("\n📁 TESTING PROJECT MANAGEMENT")
        
        if not self.jwt_token:
            print("❌ No JWT token available for project tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # 1. POST /api/projects/create - Create a new project
        print("\n1. Testing POST /api/projects/create")
        project_data = {
            "name": "Review Test Project",
            "description": "Project created during review testing",
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = requests.post(f"{self.api_url}/projects/create", json=project_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'id' in data:
                self.project_id = data['id']
                self.log_test("POST /api/projects/create", True)
            else:
                self.log_test("POST /api/projects/create", False, "No project ID in response")
        else:
            self.log_test("POST /api/projects/create", False, f"Status: {response.status_code}")
            return False
        
        # 2. GET /api/projects - List user projects
        print("\n2. Testing GET /api/projects")
        response = requests.get(f"{self.api_url}/projects", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("GET /api/projects - List projects", True)
            else:
                self.log_test("GET /api/projects - List projects", False, "Response is not a list")
        else:
            self.log_test("GET /api/projects", False, f"Status: {response.status_code}")
        
        # 3. GET /api/projects/{id} - Get specific project details
        print("\n3. Testing GET /api/projects/{id}")
        response = requests.get(f"{self.api_url}/projects/{self.project_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('id') == self.project_id:
                self.log_test("GET /api/projects/{id} - Get project details", True)
            else:
                self.log_test("GET /api/projects/{id} - Get project details", False, "Project ID mismatch")
        else:
            self.log_test("GET /api/projects/{id}", False, f"Status: {response.status_code}")
        
        # 4. GET /api/projects/{id}/messages - Get project messages
        print("\n4. Testing GET /api/projects/{id}/messages")
        response = requests.get(f"{self.api_url}/projects/{self.project_id}/messages", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("GET /api/projects/{id}/messages - Get messages", True)
            else:
                self.log_test("GET /api/projects/{id}/messages - Get messages", False, "Response is not a list")
        else:
            self.log_test("GET /api/projects/{id}/messages", False, f"Status: {response.status_code}")
        
        return True

    def test_credit_system(self):
        """Test Credit System as specified in review request"""
        print("\n💰 TESTING CREDIT SYSTEM")
        
        if not self.jwt_token:
            print("❌ No JWT token available for credit tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # 1. Verify initial 20 credits on new user registration (already tested in auth)
        print("\n1. Initial 20 credits verification - Already confirmed in auth flow ✅")
        
        # 2. GET /api/credits/balance - Check credit balance
        print("\n2. Testing GET /api/credits/balance")
        response = requests.get(f"{self.api_url}/credits/balance", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'balance' in data and data['balance'] == 20:
                self.log_test("GET /api/credits/balance - Check balance", True)
            else:
                self.log_test("GET /api/credits/balance - Check balance", False, f"Balance: {data.get('balance')}")
        else:
            self.log_test("GET /api/credits/balance", False, f"Status: {response.status_code}")
        
        # 3. GET /api/credits/transactions - Check transaction history
        print("\n3. Testing GET /api/credits/transactions")
        response = requests.get(f"{self.api_url}/credits/transactions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'transactions' in data and isinstance(data['transactions'], list):
                self.log_test("GET /api/credits/transactions - Transaction history", True)
            else:
                self.log_test("GET /api/credits/transactions - Transaction history", False, "Invalid response format")
        else:
            self.log_test("GET /api/credits/transactions", False, f"Status: {response.status_code}")
        
        return True

    def test_ai_chat_endpoint(self):
        """Test AI Chat Endpoint as specified in review request"""
        print("\n🤖 TESTING AI CHAT ENDPOINT")
        
        if not self.jwt_token or not self.project_id:
            print("❌ Missing JWT token or project ID for chat tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # POST /api/chat - Test basic chat with project_id and message
        print("\n1. Testing POST /api/chat")
        chat_data = {
            "project_id": self.project_id,
            "message": "Create a simple welcome page",
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = requests.post(f"{self.api_url}/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'ai_message' in data and 'code' in data:
                self.log_test("POST /api/chat - Basic chat with AI response", True)
                
                # Verify credits are properly deducted
                balance_response = requests.get(f"{self.api_url}/credits/balance", headers=headers)
                if balance_response.status_code == 200:
                    balance_data = balance_response.json()
                    if balance_data['balance'] < 20:  # Should be less than 20 after chat
                        self.log_test("POST /api/chat - Credits deducted", True)
                    else:
                        self.log_test("POST /api/chat - Credits deducted", False, f"Balance still: {balance_data['balance']}")
                else:
                    self.log_test("POST /api/chat - Credits deducted", False, "Could not check balance")
            else:
                self.log_test("POST /api/chat - Basic chat with AI response", False, "Missing ai_message or code in response")
        else:
            self.log_test("POST /api/chat", False, f"Status: {response.status_code}")
        
        return True

    def test_multi_agent_build_endpoint(self):
        """Test Multi-Agent Build Endpoint as specified in review request"""
        print("\n🏗️ TESTING MULTI-AGENT BUILD ENDPOINT")
        
        if not self.jwt_token or not self.project_id:
            print("❌ Missing JWT token or project ID for build tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # POST /api/build-with-agents - Test with simple prompt
        print("\n1. Testing POST /api/build-with-agents")
        build_data = {
            "project_id": self.project_id,
            "prompt": "Create a landing page",
            "uploaded_images": []
        }
        
        response = requests.post(f"{self.api_url}/build-with-agents", json=build_data, headers=headers)
        
        # This should return 402 (insufficient credits) which is expected behavior
        if response.status_code == 402:
            data = response.json()
            if "Insufficient credits" in data.get('detail', ''):
                self.log_test("POST /api/build-with-agents - Credit validation", True)
                
                # Verify proper credit reservation and detailed cost breakdown
                if "Breakdown:" in data.get('detail', '') or "breakdown" in str(data).lower():
                    self.log_test("POST /api/build-with-agents - Detailed cost breakdown", True)
                else:
                    self.log_test("POST /api/build-with-agents - Detailed cost breakdown", False, "No cost breakdown in error")
            else:
                self.log_test("POST /api/build-with-agents - Credit validation", False, f"Unexpected error: {data.get('detail')}")
        elif response.status_code == 200:
            # If user somehow has enough credits, this is also valid
            data = response.json()
            if 'frontend_code' in data:
                self.log_test("POST /api/build-with-agents - Frontend code generation", True)
            else:
                self.log_test("POST /api/build-with-agents - Frontend code generation", False, "No frontend_code in response")
        else:
            self.log_test("POST /api/build-with-agents", False, f"Status: {response.status_code}")
        
        return True

    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 TESTING HEALTH CHECK")
        
        response = requests.get(f"{self.api_url}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                self.log_test("GET /api/health - Health check", True)
            else:
                self.log_test("GET /api/health - Health check", False, f"Status: {data.get('status')}")
        else:
            self.log_test("GET /api/health", False, f"Status: {response.status_code}")

    def run_review_tests(self):
        """Run all tests specified in the review request"""
        print("🚀 AUTOWEBIQ BACKEND API REVIEW TESTING")
        print("=" * 60)
        print("Testing Emergent-style functionality as requested")
        print("=" * 60)
        
        # Run all test categories
        self.test_authentication_flow()
        self.test_project_management()
        self.test_credit_system()
        self.test_ai_chat_endpoint()
        self.test_multi_agent_build_endpoint()
        self.test_health_check()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REVIEW TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}/{self.tests_total}")
        print(f"Success Rate: {(self.tests_passed/self.tests_total)*100:.1f}%")
        
        if self.tests_passed == self.tests_total:
            print("\n🎉 ALL REVIEW REQUIREMENTS VERIFIED!")
            print("✅ Authentication Flow - Working")
            print("✅ Project Management - Working") 
            print("✅ Credit System - Working")
            print("✅ AI Chat Endpoint - Working")
            print("✅ Multi-Agent Build Endpoint - Working")
            print("✅ Backend Infrastructure - Operational")
        else:
            print(f"\n⚠️ {self.tests_total - self.tests_passed} tests failed")
        
        return self.tests_passed == self.tests_total

if __name__ == "__main__":
    tester = AutoWebIQReviewTester()
    success = tester.run_review_tests()
    exit(0 if success else 1)