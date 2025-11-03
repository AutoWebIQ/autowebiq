#!/usr/bin/env python3
"""
CRITICAL PRODUCTION VERIFICATION TESTING - autowebiq.com
Test Configuration:
- Backend URL: http://localhost:8001
- Host Header: api.autowebiq.com (REQUIRED)
- Demo Account: demo@test.com / Demo123456
- MongoDB: Local (mongodb://localhost:27017)
"""

import requests
import json
import sys
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8001"
HOST_HEADER = "api.autowebiq.com"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

# Headers with required Host header
HEADERS = {
    "Host": HOST_HEADER,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class ProductionTester:
    def __init__(self):
        self.test_results = []
        self.critical_failures = []
        self.jwt_token = None
        self.demo_user_data = None
        
    def log_test(self, test_name, status, details="", priority="MEDIUM"):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        priority_prefix = f"[{priority}]" if priority in ["CRITICAL", "HIGH"] else ""
        print(f"{status_icon} {priority_prefix} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        
        if status == "FAIL" and priority == "CRITICAL":
            self.critical_failures.append(test_name)
            
    def make_request(self, method, endpoint, data=None, auth_token=None, expect_status=200):
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        headers = HEADERS.copy()
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            return None
            
    def test_health_check(self):
        """CRITICAL: Test health endpoint"""
        print("\n🔍 CRITICAL TEST: Health Check")
        
        response = self.make_request("GET", "/api/health")
        
        if not response:
            self.log_test("Health Check - Connection", "FAIL", "Failed to connect to backend", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Health Check - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check status
            if data.get("status") != "healthy":
                self.log_test("Health Check - Status", "FAIL", f"Status: {data.get('status')}", "CRITICAL")
                return False
                
            # Check MongoDB connection
            databases = data.get("databases", {})
            mongodb_status = databases.get("mongodb")
            if mongodb_status != "connected":
                self.log_test("Health Check - MongoDB", "FAIL", f"MongoDB: {mongodb_status}", "CRITICAL")
                return False
                
            self.log_test("Health Check", "PASS", f"Status: {data.get('status')}, MongoDB: {mongodb_status}", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Health Check - JSON", "FAIL", "Invalid JSON response", "CRITICAL")
            return False
            
    def test_demo_login(self):
        """CRITICAL: Test demo account login"""
        print("\n🔍 CRITICAL TEST: Demo Account Login")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        response = self.make_request("POST", "/api/auth/login", login_data)
        
        if not response:
            self.log_test("Demo Login - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Demo Login - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check token
            if not data.get("access_token"):
                self.log_test("Demo Login - Token", "FAIL", "No access token returned", "CRITICAL")
                return False
                
            # Check user data
            user = data.get("user", {})
            if user.get("email") != DEMO_EMAIL:
                self.log_test("Demo Login - User Email", "FAIL", f"Expected {DEMO_EMAIL}, got {user.get('email')}", "CRITICAL")
                return False
                
            # Store for later tests
            self.jwt_token = data["access_token"]
            self.demo_user_data = user
            
            credits = user.get("credits", 0)
            self.log_test("Demo Login", "PASS", f"Token received, Credits: {credits}", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Demo Login - JSON", "FAIL", "Invalid JSON response", "CRITICAL")
            return False
            
    def test_user_registration(self):
        """CRITICAL: Test new user registration"""
        print("\n🔍 CRITICAL TEST: User Registration")
        
        # Generate unique test user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"test_{timestamp}@test.com"
        
        register_data = {
            "username": f"TestUser_{timestamp}",
            "email": test_email,
            "password": "Test123456"
        }
        
        response = self.make_request("POST", "/api/auth/register", register_data)
        
        if not response:
            self.log_test("User Registration - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("User Registration - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check token
            if not data.get("access_token"):
                self.log_test("User Registration - Token", "FAIL", "No access token returned", "CRITICAL")
                return False
                
            # Check user data
            user = data.get("user", {})
            if user.get("email") != test_email:
                self.log_test("User Registration - Email", "FAIL", f"Expected {test_email}, got {user.get('email')}", "CRITICAL")
                return False
                
            # Check credits (should be 20)
            credits = user.get("credits", 0)
            if credits != 20:
                self.log_test("User Registration - Credits", "FAIL", f"Expected 20 credits, got {credits}", "CRITICAL")
                return False
                
            self.log_test("User Registration", "PASS", f"User created with 20 credits", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("User Registration - JSON", "FAIL", "Invalid JSON response", "CRITICAL")
            return False
            
    def test_auth_me(self):
        """CRITICAL: Test /auth/me endpoint"""
        print("\n🔍 CRITICAL TEST: Auth Me Endpoint")
        
        if not self.jwt_token:
            self.log_test("Auth Me - No Token", "FAIL", "No JWT token available", "CRITICAL")
            return False
            
        response = self.make_request("GET", "/api/auth/me", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Auth Me - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Auth Me - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check user data
            if data.get("email") != DEMO_EMAIL:
                self.log_test("Auth Me - Email", "FAIL", f"Expected {DEMO_EMAIL}, got {data.get('email')}", "CRITICAL")
                return False
                
            if not data.get("id"):
                self.log_test("Auth Me - User ID", "FAIL", "No user ID returned", "CRITICAL")
                return False
                
            credits = data.get("credits", 0)
            self.log_test("Auth Me", "PASS", f"User data retrieved, Credits: {credits}", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Auth Me - JSON", "FAIL", "Invalid JSON response", "CRITICAL")
            return False
            
    def test_projects_list(self):
        """HIGH: Test projects list"""
        print("\n🔍 HIGH PRIORITY TEST: Projects List")
        
        if not self.jwt_token:
            self.log_test("Projects List - No Token", "FAIL", "No JWT token available", "HIGH")
            return False
            
        response = self.make_request("GET", "/api/projects", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Projects List - Connection", "FAIL", "Failed to connect", "HIGH")
            return False
            
        if response.status_code != 200:
            self.log_test("Projects List - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "HIGH")
            return False
            
        try:
            data = response.json()
            
            if "projects" not in data:
                self.log_test("Projects List - Structure", "FAIL", "No 'projects' key in response", "HIGH")
                return False
                
            projects = data["projects"]
            if not isinstance(projects, list):
                self.log_test("Projects List - Type", "FAIL", "Projects is not a list", "HIGH")
                return False
                
            self.log_test("Projects List", "PASS", f"Retrieved {len(projects)} projects", "HIGH")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Projects List - JSON", "FAIL", "Invalid JSON response", "HIGH")
            return False
            
    def test_project_creation(self):
        """HIGH: Test project creation"""
        print("\n🔍 HIGH PRIORITY TEST: Project Creation")
        
        if not self.jwt_token:
            self.log_test("Project Creation - No Token", "FAIL", "No JWT token available", "HIGH")
            return False
            
        project_data = {
            "name": "Test Project Production",
            "description": "Production verification test project",
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = self.make_request("POST", "/api/projects/create", project_data, auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Project Creation - Connection", "FAIL", "Failed to connect", "HIGH")
            return False
            
        if response.status_code != 200:
            self.log_test("Project Creation - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "HIGH")
            return False
            
        try:
            data = response.json()
            
            if not data.get("id"):
                self.log_test("Project Creation - ID", "FAIL", "No project ID returned", "HIGH")
                return False
                
            if data.get("name") != project_data["name"]:
                self.log_test("Project Creation - Name", "FAIL", f"Name mismatch", "HIGH")
                return False
                
            self.log_test("Project Creation", "PASS", f"Project created with ID: {data['id'][:8]}...", "HIGH")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Project Creation - JSON", "FAIL", "Invalid JSON response", "HIGH")
            return False
            
    def test_credit_balance(self):
        """HIGH: Test credit balance endpoint"""
        print("\n🔍 HIGH PRIORITY TEST: Credit Balance")
        
        if not self.jwt_token:
            self.log_test("Credit Balance - No Token", "FAIL", "No JWT token available", "HIGH")
            return False
            
        response = self.make_request("GET", "/api/credits/balance", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Credit Balance - Connection", "FAIL", "Failed to connect", "HIGH")
            return False
            
        if response.status_code != 200:
            self.log_test("Credit Balance - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "HIGH")
            return False
            
        try:
            data = response.json()
            
            if "credits" not in data:
                self.log_test("Credit Balance - Structure", "FAIL", "No 'credits' key in response", "HIGH")
                return False
                
            balance = data["credits"]
            if not isinstance(balance, (int, float)):
                self.log_test("Credit Balance - Type", "FAIL", "Balance is not a number", "HIGH")
                return False
                
            self.log_test("Credit Balance", "PASS", f"Balance: {balance} credits", "HIGH")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Credit Balance - JSON", "FAIL", "Invalid JSON response", "HIGH")
            return False
            
    def test_credit_pricing(self):
        """HIGH: Test credit pricing endpoint"""
        print("\n🔍 HIGH PRIORITY TEST: Credit Pricing")
        
        response = self.make_request("GET", "/api/credits/pricing")
        
        if not response:
            self.log_test("Credit Pricing - Connection", "FAIL", "Failed to connect", "HIGH")
            return False
            
        if response.status_code != 200:
            self.log_test("Credit Pricing - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "HIGH")
            return False
            
        try:
            data = response.json()
            
            # Should have agent_costs and model_costs
            if "agent_costs" not in data or "model_costs" not in data:
                self.log_test("Credit Pricing - Structure", "FAIL", "Missing agent_costs or model_costs", "HIGH")
                return False
                
            agent_costs = data["agent_costs"]
            model_costs = data["model_costs"]
            
            if not isinstance(agent_costs, dict) or not isinstance(model_costs, dict):
                self.log_test("Credit Pricing - Types", "FAIL", "Costs are not dictionaries", "HIGH")
                return False
                
            self.log_test("Credit Pricing", "PASS", f"Agent costs: {len(agent_costs)}, Model costs: {len(model_costs)}", "HIGH")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Credit Pricing - JSON", "FAIL", "Invalid JSON response", "HIGH")
            return False
            
    def test_subscription_plans(self):
        """MEDIUM: Test subscription plans"""
        print("\n🔍 MEDIUM PRIORITY TEST: Subscription Plans")
        
        response = self.make_request("GET", "/api/subscriptions/plans")
        
        if not response:
            self.log_test("Subscription Plans - Connection", "FAIL", "Failed to connect", "MEDIUM")
            return False
            
        if response.status_code != 200:
            self.log_test("Subscription Plans - Status Code", "FAIL", f"Expected 200, got {response.status_code}", "MEDIUM")
            return False
            
        try:
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Subscription Plans - Success", "FAIL", "Success flag is false", "MEDIUM")
                return False
                
            plans = data.get("plans", [])
            if len(plans) != 4:
                self.log_test("Subscription Plans - Count", "FAIL", f"Expected 4 plans, got {len(plans)}", "MEDIUM")
                return False
                
            # Check for required plans
            plan_names = [plan.get("name", "") for plan in plans]
            required_plans = ["Free", "Starter", "Pro", "Enterprise"]
            
            for required_plan in required_plans:
                if required_plan not in plan_names:
                    self.log_test("Subscription Plans - Missing Plan", "FAIL", f"Missing {required_plan} plan", "MEDIUM")
                    return False
                    
            self.log_test("Subscription Plans", "PASS", f"All 4 plans found: {', '.join(plan_names)}", "MEDIUM")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Subscription Plans - JSON", "FAIL", "Invalid JSON response", "MEDIUM")
            return False
            
    def run_all_tests(self):
        """Run all tests in priority order"""
        print("🚀 STARTING CRITICAL PRODUCTION VERIFICATION TESTING")
        print(f"Backend URL: {BASE_URL}")
        print(f"Host Header: {HOST_HEADER}")
        print(f"Demo Account: {DEMO_EMAIL}")
        print("=" * 60)
        
        # CRITICAL TESTS (must pass 100%)
        critical_tests = [
            self.test_health_check,
            self.test_demo_login,
            self.test_user_registration,
            self.test_auth_me
        ]
        
        critical_passed = 0
        for test in critical_tests:
            if test():
                critical_passed += 1
            else:
                print(f"\n🚨 CRITICAL TEST FAILED - STOPPING EXECUTION")
                break
                
        # Only continue if all critical tests pass
        if critical_passed == len(critical_tests):
            print(f"\n✅ ALL CRITICAL TESTS PASSED ({critical_passed}/{len(critical_tests)})")
            
            # HIGH PRIORITY TESTS
            high_tests = [
                self.test_projects_list,
                self.test_project_creation,
                self.test_credit_balance,
                self.test_credit_pricing
            ]
            
            for test in high_tests:
                test()
                
            # MEDIUM PRIORITY TESTS
            medium_tests = [
                self.test_subscription_plans
            ]
            
            for test in medium_tests:
                test()
        else:
            print(f"\n❌ CRITICAL TESTS FAILED ({critical_passed}/{len(critical_tests)}) - PRODUCTION NOT READY")
            
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        critical_tests = [t for t in self.test_results if t["priority"] == "CRITICAL"]
        critical_passed = len([t for t in critical_tests if t["status"] == "PASS"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Critical Tests: {critical_passed}/{len(critical_tests)} passed")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   - {failure}")
                
        # Production readiness assessment
        if critical_passed == len(critical_tests) and passed_tests >= total_tests * 0.95:
            print(f"\n✅ PRODUCTION ASSESSMENT: READY FOR DEPLOYMENT")
            print(f"   All critical tests passed, {(passed_tests/total_tests)*100:.1f}% success rate")
        else:
            print(f"\n❌ PRODUCTION ASSESSMENT: NOT READY")
            print(f"   Critical failures or success rate below 95%")
            
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = ProductionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)