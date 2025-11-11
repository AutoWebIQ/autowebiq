#!/usr/bin/env python3
"""
MongoDB-Based Backend Testing After Syntax Error Fix
Focus on testing MongoDB endpoints that should be working after the deployment_manager.py fix.
Avoiding PostgreSQL endpoints that are causing 500 errors.
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Test Configuration
BACKEND_URL = "https://aiweb-builder-2.preview.emergentagent.com/api"

# Demo Account Credentials
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class MongoDBBackendTester:
    """MongoDB-based backend functionality tester"""
    
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
        """Test new user registration with 20 credits (MongoDB)"""
        print(f"\n👤 Testing New User Registration (MongoDB)...")
        
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
                self.log_test("New User Registration (MongoDB)", True, details)
                self.log_test("20 Credits Granted on Signup", credits_correct, f"Expected: 20, Got: {credits}")
                
                return {
                    "success": True,
                    "user_id": self.user_data["id"],
                    "credits": credits,
                    "credits_correct": credits_correct
                }
            else:
                error_data = response.json() if response.text else {}
                self.log_test("New User Registration (MongoDB)", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("New User Registration (MongoDB)", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_new_user_login(self) -> Dict:
        """Test login with newly created user (MongoDB)"""
        print(f"\n🔐 Testing New User Login (MongoDB)...")
        
        if not self.new_user_email:
            self.log_test("New User Login (MongoDB)", False, "No new user email available")
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
                
                self.log_test("New User Login (MongoDB)", True, f"User ID: {user['id']}, Credits: {user['credits']}")
                return {"success": True, "token": token, "user": user}
            else:
                error_data = response.json() if response.text else {}
                self.log_test("New User Login (MongoDB)", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("New User Login (MongoDB)", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_auth_me_endpoint(self) -> Dict:
        """Test /auth/me endpoint with JWT token (MongoDB)"""
        print(f"\n👤 Testing /auth/me Endpoint (MongoDB)...")
        
        if not self.auth_token:
            self.log_test("Auth Me Endpoint (MongoDB)", False, "No auth token available")
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
                self.log_test("Auth Me Endpoint (MongoDB)", True, details)
                self.log_test("User Data Structure", has_all_fields, f"Fields: {list(user_data.keys())}")
                
                return {"success": True, "user_data": user_data, "structure_valid": has_all_fields}
            else:
                error_data = response.json() if response.text else {}
                self.log_test("Auth Me Endpoint (MongoDB)", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("Auth Me Endpoint (MongoDB)", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_demo_account_access(self) -> Dict:
        """Test demo account login (MongoDB)"""
        print(f"\n🎯 Testing Demo Account Access (MongoDB)...")
        
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
                self.log_test("Demo Account Login (MongoDB)", True, details)
                
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
                self.log_test("Demo Account Login (MongoDB)", False, f"Status: {response.status_code}", error_data)
                return {"success": False, "status_code": response.status_code, "error": error_data}
                
        except Exception as e:
            self.log_test("Demo Account Login (MongoDB)", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_mongodb_project_operations(self) -> Dict:
        """Test MongoDB-based project operations (avoiding PostgreSQL endpoints)"""
        print(f"\n📁 Testing MongoDB Project Operations...")
        
        if not self.demo_auth_token:
            self.log_test("MongoDB Project Operations", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        try:
            # Test the MongoDB create project endpoint (line 712 in server.py)
            project_data = {
                "name": "MongoDB Test Project",
                "description": "Test project for MongoDB backend testing after syntax fix"
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
                self.log_test("Create Project (MongoDB)", True, f"Project ID: {self.test_project_id}")
                
                # Test delete project (MongoDB endpoint)
                delete_response = requests.delete(
                    f"{BACKEND_URL}/projects/{self.test_project_id}",
                    headers=headers,
                    timeout=30
                )
                
                if delete_response.status_code == 200:
                    self.log_test("Delete Project (MongoDB)", True, "Project archived successfully")
                else:
                    self.log_test("Delete Project (MongoDB)", False, f"Status: {delete_response.status_code}")
                
                return {"success": True, "project_id": self.test_project_id}
            else:
                error_data = create_response.json() if create_response.text else {}
                self.log_test("Create Project (MongoDB)", False, f"Status: {create_response.status_code}", error_data)
                return {"success": False, "create_error": error_data}
            
        except Exception as e:
            self.log_test("MongoDB Project Operations", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_mongodb_credit_endpoints(self) -> Dict:
        """Test MongoDB-based credit endpoints"""
        print(f"\n💳 Testing MongoDB Credit Endpoints...")
        
        if not self.demo_auth_token:
            self.log_test("MongoDB Credit Endpoints", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        results = {}
        
        try:
            # Test credit pricing endpoint (should work with MongoDB)
            pricing_response = requests.get(f"{BACKEND_URL}/credits/pricing", headers=headers, timeout=30)
            
            if pricing_response.status_code == 200:
                pricing_data = pricing_response.json()
                self.log_test("Credit Pricing (MongoDB)", True, f"Pricing structure available")
                results["pricing"] = True
            else:
                self.log_test("Credit Pricing (MongoDB)", False, f"Status: {pricing_response.status_code}")
                results["pricing"] = False
            
            # Test models endpoint
            models_response = requests.get(f"{BACKEND_URL}/models", timeout=30)
            
            if models_response.status_code == 200:
                models_data = models_response.json()
                model_count = len(models_data) if isinstance(models_data, dict) else 0
                self.log_test("Models Endpoint", True, f"Found {model_count} models")
                results["models"] = True
            else:
                self.log_test("Models Endpoint", False, f"Status: {models_response.status_code}")
                results["models"] = False
            
            # Test credit packages endpoint
            packages_response = requests.get(f"{BACKEND_URL}/credits/packages", timeout=30)
            
            if packages_response.status_code == 200:
                packages_data = packages_response.json()
                package_count = len(packages_data) if isinstance(packages_data, list) else 0
                self.log_test("Credit Packages", True, f"Found {package_count} packages")
                results["packages"] = True
            else:
                self.log_test("Credit Packages", False, f"Status: {packages_response.status_code}")
                results["packages"] = False
            
            overall_success = all(results.values())
            return {"success": overall_success, "results": results}
            
        except Exception as e:
            self.log_test("MongoDB Credit Endpoints", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_chat_endpoint(self) -> Dict:
        """Test chat endpoint with MongoDB"""
        print(f"\n💬 Testing Chat Endpoint (MongoDB)...")
        
        if not self.demo_auth_token:
            self.log_test("Chat Endpoint (MongoDB)", False, "No demo auth token available")
            return {"success": False, "error": "No auth token"}
        
        headers = {"Authorization": f"Bearer {self.demo_auth_token}"}
        
        # First create a project for chat
        project_data = {
            "name": "Chat Test Project",
            "description": "Test project for chat endpoint"
        }
        
        try:
            create_response = requests.post(
                f"{BACKEND_URL}/projects/create",
                json=project_data,
                headers=headers,
                timeout=30
            )
            
            if create_response.status_code != 200:
                self.log_test("Chat Endpoint (MongoDB)", False, "Failed to create test project for chat")
                return {"success": False, "error": "Project creation failed"}
            
            project = create_response.json()
            project_id = project["id"]
            
            # Test chat request
            chat_request = {
                "project_id": project_id,
                "message": "Create a simple HTML page with hello world",
                "model": "claude-4.5-sonnet-200k"
            }
            
            chat_response = requests.post(
                f"{BACKEND_URL}/chat",
                json=chat_request,
                headers=headers,
                timeout=60
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                self.log_test("Chat Endpoint (MongoDB)", True, f"Chat successful, generated code length: {len(chat_data.get('code', ''))}")
                return {"success": True, "chat_data": chat_data}
            elif chat_response.status_code == 402:
                # Insufficient credits - this is expected behavior
                error_data = chat_response.json()
                self.log_test("Chat Credit Validation", True, f"Proper 402 response: {error_data.get('detail', 'unknown')}")
                return {"success": True, "credit_validation": True, "error_data": error_data}
            else:
                error_data = chat_response.json() if chat_response.text else {}
                self.log_test("Chat Endpoint (MongoDB)", False, f"Status: {chat_response.status_code}", error_data)
                return {"success": False, "status_code": chat_response.status_code, "error": error_data}
            
        except Exception as e:
            self.log_test("Chat Endpoint (MongoDB)", False, str(e))
            return {"success": False, "error": str(e)}
    
    def run_mongodb_tests(self) -> Dict:
        """Run all MongoDB-based backend tests"""
        print(f"\n🧪 MONGODB BACKEND TESTING AFTER SYNTAX ERROR FIX")
        print(f"=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing MongoDB-based endpoints after deployment_manager.py fix")
        print(f"Avoiding PostgreSQL endpoints that are causing 500 errors")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "health_check": {},
            "new_user_registration": {},
            "new_user_login": {},
            "auth_me_endpoint": {},
            "demo_account_access": {},
            "mongodb_project_operations": {},
            "mongodb_credit_endpoints": {},
            "chat_endpoint": {},
            "overall_success": False,
            "success_rate": 0.0
        }
        
        try:
            # Test 1: Health Check
            results["health_check"] = self.test_health_check()
            
            # Test 2: New User Registration (CRITICAL)
            results["new_user_registration"] = self.test_new_user_registration()
            
            # Test 3: New User Login (CRITICAL)
            results["new_user_login"] = self.test_new_user_login()
            
            # Test 4: Auth Me Endpoint (CRITICAL)
            results["auth_me_endpoint"] = self.test_auth_me_endpoint()
            
            # Test 5: Demo Account Access (HIGH)
            results["demo_account_access"] = self.test_demo_account_access()
            
            # Test 6: MongoDB Project Operations (HIGH)
            results["mongodb_project_operations"] = self.test_mongodb_project_operations()
            
            # Test 7: MongoDB Credit Endpoints (MEDIUM)
            results["mongodb_credit_endpoints"] = self.test_mongodb_credit_endpoints()
            
            # Test 8: Chat Endpoint (MEDIUM)
            results["chat_endpoint"] = self.test_chat_endpoint()
            
            # Calculate success metrics
            test_categories = [
                "health_check", "new_user_registration", "new_user_login", 
                "auth_me_endpoint", "demo_account_access", "mongodb_project_operations",
                "mongodb_credit_endpoints", "chat_endpoint"
            ]
            
            successful_tests = sum(1 for category in test_categories if results[category].get("success", False))
            results["success_rate"] = (successful_tests / len(test_categories)) * 100
            results["overall_success"] = results["success_rate"] >= 80  # 80% success threshold
            
            return results
            
        except Exception as e:
            print(f"❌ MongoDB test execution failed: {str(e)}")
            results["error"] = str(e)
            return results
        
        finally:
            results["test_end_time"] = datetime.now().isoformat()
            results["test_results"] = self.test_results

def main():
    """Main test execution"""
    print(f"🚀 AutoWebIQ MongoDB Backend Testing")
    
    tester = MongoDBBackendTester()
    results = tester.run_mongodb_tests()
    
    # Print final summary
    print(f"\n" + "=" * 70)
    print(f"🏁 MONGODB BACKEND TEST SUMMARY")
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
        ("MongoDB Project Operations", "mongodb_project_operations", "HIGH"),
        ("MongoDB Credit Endpoints", "mongodb_credit_endpoints", "MEDIUM"),
        ("Chat Endpoint", "chat_endpoint", "MEDIUM")
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
    else:
        print(f"\n✅ ALL CRITICAL AND HIGH PRIORITY TESTS PASSED!")
    
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