#!/usr/bin/env python3
"""
CRITICAL BACKEND TESTING AFTER SYNTAX ERROR FIX
Testing core authentication and project management functionality
as requested in the review after deployment_manager.py syntax fix.

Priority Test Cases:
1. Authentication Flow (CRITICAL) - register, login, /auth/me, verify 20 credits
2. Demo Account Access (HIGH) - login with demo@test.com / Demo123456  
3. Project Management (HIGH) - CRUD operations
4. Credit System (MEDIUM) - balance, transactions, summary, pricing
5. Health Check (LOW) - service status
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Test Configuration
BACKEND_URL = "https://multiagent-web.preview.emergentagent.com/api"

# Demo Account Credentials
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class CriticalBackendTester:
    """Critical backend functionality tester after syntax error fix"""
    
    def __init__(self):
        self.auth_token = None
        self.demo_auth_token = None
        self.user_data = None
        self.demo_user_data = None
        self.test_project_id = None
        self.test_results = []
        self.new_user_email = None
        
    def log_test(self, name: str, success: bool, details: str = "", response_data: dict = None):
        """Log test result with detailed information"""
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def test_health_check(self) -> Dict:
        """Test health check endpoint"""
        print(f"\n🏥 Testing Health Check...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("Health Check", True, f"Status: {health_data.get('status', 'unknown')}")
                return {"success": True, "data": health_data}
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response.json() if response.text else {})
                return {"success": False, "status_code": response.status_code}
                
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_new_user_registration(self) -> Dict:
        """Test new user registration with 20 credits"""
        print(f"\n👤 Testing New User Registration...")
        
        # Generate unique email for testing
        timestamp = int(time.time())
        self.new_user_email = f"testuser{timestamp}@test.com"
        
        registration_data = {
            "username": f"testuser{timestamp}",
            "email": self.new_user_email,
            "password": "TestPassword123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data["access_token"]
                self.user_data = auth_data["user"]
                
                # Verify 20 credits granted
                credits = self.user_data.get("credits", 0)
                credits_correct = credits == 20
                
                details = f"User ID: {self.user_data['id']}, Credits: {credits}"
                self.log_test("New User Registration", True, details)
                self.log_test("20 Credits Granted on Signup", credits_correct, f"Expected: 20, Got: {credits}")
                
                return {
                    "success": True,
                    "user_id": self.user_data["id"],
                    "credits": credits,
                    "credits_correct": credits_correct
                }
            else:
                error_data = response.json() if response.text else {}
                self.log_test("New User Registration", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("New User Registration", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_new_user_login(self) -> Dict:
        """Test login with newly created user"""
        print(f"\n🔐 Testing New User Login...")
        
        if not self.new_user_email:
            self.log_test("New User Login", False, "No new user email available")
            return {"success": False, "error": "No new user created"}
        
        login_data = {
            "email": self.new_user_email,
            "password": "TestPassword123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data["access_token"]
                user = auth_data["user"]
                
                self.log_test("New User Login", True, f"User ID: {user['id']}, Credits: {user['credits']}")
                return {"success": True, "token": token, "user": user}
            else:
                error_data = response.json() if response.text else {}
                self.log_test("New User Login", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("New User Login", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_auth_me_endpoint(self) -> Dict:
        """Test /auth/me endpoint with JWT token"""
        print(f"\n👤 Testing /auth/me Endpoint...")
        
        if not self.auth_token:
            self.log_test("Auth Me Endpoint", False, "No auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Verify user data structure
                required_fields = ["id", "email", "username", "credits"]
                has_all_fields = all(field in user_data for field in required_fields)
                
                details = f"ID: {user_data.get('id', 'missing')}, Credits: {user_data.get('credits', 'missing')}"
                self.log_test("Auth Me Endpoint", True, details)
                self.log_test("User Data Structure", has_all_fields, f"Fields: {list(user_data.keys())}")
                
                return {"success": True, "user_data": user_data, "structure_valid": has_all_fields}
            else:
                error_data = response.json() if response.text else {}
                self.log_test("Auth Me Endpoint", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_demo_account_access(self) -> Dict:
        """Test demo account login"""
        print(f"\n🎯 Testing Demo Account Access...")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.demo_auth_token = auth_data["access_token"]
                self.demo_user_data = auth_data["user"]
                
                details = f"User ID: {self.demo_user_data['id']}, Credits: {self.demo_user_data['credits']}"
                self.log_test("Demo Account Login", True, details)
                
                # Test /auth/me with demo account
                headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
                me_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    self.log_test("Demo Account /auth/me", True, f"Credits: {me_data.get('credits', 0)}")
                else:
                    self.log_test("Demo Account /auth/me", False, f"Status: {me_response.status_code}")
                
                return {"success": True, "user_data": self.demo_user_data}
            else:
                error_data = response.json() if response.text else {}
                self.log_test("Demo Account Login", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("Demo Account Login", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_project_management(self) -> Dict:
        """Test project CRUD operations"""
        print(f"\n📁 Testing Project Management...")
        
        if not self.demo_auth_token:
            self.log_test("Project Management", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        try:
            # 1. Create Project
            project_data = {
                "name": "Critical Test Project",
                "description": "Test project for critical backend testing after syntax fix"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/projects/create",
                json=project_data,
                headers=headers,
                timeout=30
            )
            
            if create_response.status_code == 200:
                project = create_response.json()
                self.test_project_id = project["id"]
                self.log_test("Create Project", True, f"Project ID: {self.test_project_id}")
            else:
                error_data = create_response.json() if create_response.text else {}
                self.log_test("Create Project", False, f"Status: {create_response.status_code}", error_data)
                return {"success": False, "create_error": error_data}
            
            # 2. List Projects
            list_response = requests.get(f"{BACKEND_URL}/projects", headers=headers, timeout=30)
            
            if list_response.status_code == 200:
                projects = list_response.json()
                project_count = len(projects) if isinstance(projects, list) else 0
                self.log_test("List Projects", True, f"Found {project_count} projects")
            else:
                self.log_test("List Projects", False, f"Status: {list_response.status_code}")
            
            # 3. Get Project by ID
            if self.test_project_id:
                get_response = requests.get(
                    f"{BACKEND_URL}/projects/{self.test_project_id}",
                    headers=headers,
                    timeout=30
                )
                
                if get_response.status_code == 200:
                    project_detail = get_response.json()
                    self.log_test("Get Project by ID", True, f"Name: {project_detail.get('name', 'unknown')}")
                else:
                    self.log_test("Get Project by ID", False, f"Status: {get_response.status_code}")
            
            # 4. Delete Project
            if self.test_project_id:
                delete_response = requests.delete(
                    f"{BACKEND_URL}/projects/{self.test_project_id}",
                    headers=headers,
                    timeout=30
                )
                
                if delete_response.status_code == 200:
                    self.log_test("Delete Project", True, "Project archived successfully")
                else:
                    self.log_test("Delete Project", False, f"Status: {delete_response.status_code}")
            
            return {"success": True, "project_id": self.test_project_id}
            
        except Exception as e:
            self.log_test("Project Management", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_credit_system(self) -> Dict:
        """Test credit system endpoints"""
        print(f"\n💳 Testing Credit System...")
        
        if not self.demo_auth_token:
            self.log_test("Credit System", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        results = {}
        
        try:
            # 1. Credit Balance
            balance_response = requests.get(f"{BACKEND_URL}/credits/balance", headers=headers, timeout=30)
            
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                self.log_test("Credit Balance", True, f"Balance: {balance_data}")
                results["balance"] = True
            else:
                self.log_test("Credit Balance", False, f"Status: {balance_response.status_code}")
                results["balance"] = False
            
            # 2. Credit Transactions
            transactions_response = requests.get(f"{BACKEND_URL}/credits/transactions", headers=headers, timeout=30)
            
            if transactions_response.status_code == 200:
                transactions_data = transactions_response.json()
                transaction_count = len(transactions_data) if isinstance(transactions_data, list) else 0
                self.log_test("Credit Transactions", True, f"Found {transaction_count} transactions")
                results["transactions"] = True
            else:
                error_data = transactions_response.json() if transactions_response.text else {}
                self.log_test("Credit Transactions", False, f"Status: {transactions_response.status_code}", error_data)
                results["transactions"] = False
            
            # 3. Credit Summary
            summary_response = requests.get(f"{BACKEND_URL}/credits/summary", headers=headers, timeout=30)
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                self.log_test("Credit Summary", True, f"Summary: {summary_data}")
                results["summary"] = True
            else:
                self.log_test("Credit Summary", False, f"Status: {summary_response.status_code}")
                results["summary"] = False
            
            # 4. Credit Pricing
            pricing_response = requests.get(f"{BACKEND_URL}/credits/pricing", headers=headers, timeout=30)
            
            if pricing_response.status_code == 200:
                pricing_data = pricing_response.json()
                self.log_test("Credit Pricing", True, f"Pricing structure available")
                results["pricing"] = True
            else:
                self.log_test("Credit Pricing", False, f"Status: {pricing_response.status_code}")
                results["pricing"] = False
            
            overall_success = all(results.values())
            return {"success": overall_success, "results": results}
            
        except Exception as e:
            self.log_test("Credit System", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_build_with_agents_validation(self) -> Dict:
        """Test build-with-agents endpoint for credit validation"""
        print(f"\n🤖 Testing Build with Agents Credit Validation...")
        
        if not self.demo_auth_token:
            self.log_test("Build Agents Validation", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        # Create a test project first
        project_data = {
            "name": "Build Test Project",
            "description": "Test project for build validation"
        }
        
        try:
            create_response = requests.post(
                f"{BACKEND_URL}/projects/create",
                json=project_data,
                headers=headers,
                timeout=30
            )
            
            if create_response.status_code != 200:
                self.log_test("Build Agents Validation", False, "Failed to create test project")
                return {"success": False, "error": "Project creation failed"}
            
            project = create_response.json()
            project_id = project["id"]
            
            # Test build request
            build_request = {
                "project_id": project_id,
                "prompt": "Create a simple landing page",
                "uploaded_images": []
            }
            
            build_response = requests.post(
                f"{BACKEND_URL}/build-with-agents",
                json=build_request,
                headers=headers,
                timeout=60
            )
            
            if build_response.status_code == 200:
                build_data = build_response.json()
                self.log_test("Build Agents Validation", True, f"Build successful: {build_data.get('status', 'unknown')}")
                return {"success": True, "build_data": build_data}
            elif build_response.status_code == 402:
                # Insufficient credits - this is expected behavior
                error_data = build_response.json()
                self.log_test("Build Agents Credit Validation", True, f"Proper 402 response: {error_data.get('detail', 'unknown')}")
                return {"success": True, "credit_validation": True, "error_data": error_data}
            else:
                error_data = build_response.json() if build_response.text else {}
                self.log_test("Build Agents Validation", False, f"Status: {build_response.status_code}", error_data)
                return {"success": False, "status_code": build_response.status_code, "error": error_data}
            
        except Exception as e:
            self.log_test("Build Agents Validation", False, str(e))
            return {"success": False, "error": str(e)}
    
    def run_critical_tests(self) -> Dict:
        """Run all critical backend tests"""
        print(f"\n🧪 CRITICAL BACKEND TESTING AFTER SYNTAX ERROR FIX")
        print(f"=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing core authentication and project management functionality")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "health_check": {},
            "new_user_registration": {},
            "new_user_login": {},
            "auth_me_endpoint": {},
            "demo_account_access": {},
            "project_management": {},
            "credit_system": {},
            "build_validation": {},
            "overall_success": False,
            "success_rate": 0.0
        }
        
        try:
            # Test 1: Health Check (LOW priority)
            results["health_check"] = self.test_health_check()
            
            # Test 2: New User Registration (CRITICAL)
            results["new_user_registration"] = self.test_new_user_registration()
            
            # Test 3: New User Login (CRITICAL)
            results["new_user_login"] = self.test_new_user_login()
            
            # Test 4: Auth Me Endpoint (CRITICAL)
            results["auth_me_endpoint"] = self.test_auth_me_endpoint()
            
            # Test 5: Demo Account Access (HIGH)
            results["demo_account_access"] = self.test_demo_account_access()
            
            # Test 6: Project Management (HIGH)
            results["project_management"] = self.test_project_management()
            
            # Test 7: Credit System (MEDIUM)
            results["credit_system"] = self.test_credit_system()
            
            # Test 8: Build Validation (MEDIUM)
            results["build_validation"] = self.test_build_with_agents_validation()
            
            # Calculate success metrics
            test_categories = [
                "health_check", "new_user_registration", "new_user_login", 
                "auth_me_endpoint", "demo_account_access", "project_management",
                "credit_system", "build_validation"
            ]
            
            successful_tests = sum(1 for category in test_categories if results[category].get("success", False))
            results["success_rate"] = (successful_tests / len(test_categories)) * 100
            results["overall_success"] = results["success_rate"] >= 80  # 80% success threshold
            
            return results
            
        except Exception as e:
            print(f"❌ Critical test execution failed: {str(e)}")
            results["error"] = str(e)
            return results
        
        finally:
            results["test_end_time"] = datetime.now().isoformat()
            results["test_results"] = self.test_results

def main():
    """Main test execution"""
    print(f"🚀 AutoWebIQ Critical Backend Testing")
    
    tester = CriticalBackendTester()
    results = tester.run_critical_tests()
    
    # Print final summary
    print(f"\n" + "=" * 70)
    print(f"🏁 CRITICAL BACKEND TEST SUMMARY")
    print(f"=" * 70)
    
    success_rate = results.get('success_rate', 0)
    overall_success = results.get('overall_success', False)
    
    print(f"Overall Success: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📊 Test Category Results:")
    categories = [
        ("Health Check", "health_check", "LOW"),
        ("New User Registration", "new_user_registration", "CRITICAL"),
        ("New User Login", "new_user_login", "CRITICAL"),
        ("Auth Me Endpoint", "auth_me_endpoint", "CRITICAL"),
        ("Demo Account Access", "demo_account_access", "HIGH"),
        ("Project Management", "project_management", "HIGH"),
        ("Credit System", "credit_system", "MEDIUM"),
        ("Build Validation", "build_validation", "MEDIUM")
    ]
    
    for name, key, priority in categories:
        success = results.get(key, {}).get("success", False)
        status = "✅" if success else "❌"
        print(f"  {status} {name} ({priority})")
    
    # Print critical issues
    critical_failures = []
    for name, key, priority in categories:
        if priority in ["CRITICAL", "HIGH"] and not results.get(key, {}).get("success", False):
            critical_failures.append(name)
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES:")
        for failure in critical_failures:
            print(f"  ❌ {failure}")
    
    # Print detailed test results
    print(f"\n📋 Detailed Test Results:")
    for i, test in enumerate(tester.test_results, 1):
        status = "✅" if test['success'] else "❌"
        print(f"  {i:2d}. {status} {test['test']}")
        if test['details']:
            print(f"      {test['details']}")
    
    print(f"\n🔗 Backend URL: {BACKEND_URL}")
    print(f"📅 Test completed at: {results.get('test_end_time', 'unknown')}")
    
    # Return exit code based on success
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)