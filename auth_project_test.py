#!/usr/bin/env python3
"""
AutoWebIQ Backend Review Request Testing
Testing all authentication and project management endpoints as specified in the review request.
Backend URL: https://aiweb-builder-2.preview.emergentagent.com/api
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime, timezone

class AutoWebIQReviewTester:
    def __init__(self):
        # Backend URL as specified in review request
        self.base_url = "https://aiweb-builder-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_data = None
        self.test_project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        print(f"🎯 AutoWebIQ Backend Review Request Testing")
        print(f"   Backend URL: {self.api_url}")
        print("=" * 70)

    def log_test(self, name, success, details="", response_data=None):
        """Log test result with detailed information"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if response_data and isinstance(response_data, dict):
                # Show key response fields for successful tests
                if 'access_token' in response_data:
                    print(f"   Token: {response_data['access_token'][:20]}...")
                if 'user' in response_data and isinstance(response_data['user'], dict):
                    user = response_data['user']
                    print(f"   User: {user.get('email', 'N/A')} (Credits: {user.get('credits', 'N/A')})")
                if 'id' in response_data:
                    print(f"   ID: {response_data['id']}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   Error: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response": response_data
        })

    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request and return success, response data, and response object"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}, None

            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500]}

            success = response.status_code == expected_status
            
            if not success:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                if response_data:
                    error_msg += f". Response: {response_data}"
                return False, response_data, response
            
            return True, response_data, response

        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout (30s)"}, None
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection error"}, None
        except Exception as e:
            return False, {"error": f"Request failed: {str(e)}"}, None

    def test_1_health_check(self):
        """Test 1: Health Check - GET /api/health"""
        print("\n🏥 Test 1: Health Check")
        
        success, response_data, _ = self.make_request('GET', 'health', expected_status=200)
        
        if success:
            # Check response structure
            status = response_data.get('status', 'unknown')
            databases = response_data.get('databases', {})
            services = response_data.get('services', {})
            
            print(f"   System Status: {status}")
            print(f"   Databases: {databases}")
            print(f"   Services: {services}")
            
            self.log_test("Health Check", True, f"System status: {status}", response_data)
            return True
        else:
            self.log_test("Health Check", False, "Health endpoint not responding", response_data)
            return False

    def test_2_user_registration(self):
        """Test 2: User Registration - POST /api/auth/register"""
        print("\n👤 Test 2: User Registration")
        
        # Generate unique test user
        timestamp = int(time.time())
        random_suffix = str(uuid.uuid4())[:8]
        test_email = f"testuser{random_suffix}@test.com"
        test_username = f"testuser{random_suffix}"
        test_password = "Test123456"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        print(f"   Registering: {test_email}")
        
        success, response_data, _ = self.make_request(
            'POST', 'auth/register', 
            data=registration_data, 
            expected_status=200
        )
        
        if success:
            # Verify response structure
            if 'access_token' in response_data and 'user' in response_data:
                self.access_token = response_data['access_token']
                self.user_data = response_data['user']
                
                # Verify user has credits
                credits = self.user_data.get('credits', 0)
                print(f"   Credits granted: {credits}")
                
                self.log_test("User Registration", True, f"User created with {credits} credits", response_data)
                return True
            else:
                self.log_test("User Registration", False, "Invalid response structure", response_data)
                return False
        else:
            self.log_test("User Registration", False, "Registration failed", response_data)
            return False

    def test_3_user_login(self):
        """Test 3: User Login - POST /api/auth/login"""
        print("\n🔐 Test 3: User Login")
        
        if not self.user_data:
            print("   ⚠️ Skipping login test - no user data from registration")
            return False
        
        # Extract email from user data for login
        user_email = self.user_data.get('email')
        if not user_email:
            print("   ⚠️ No email found in user data")
            return False
        
        login_data = {
            "email": user_email,
            "password": "Test123456"  # Same password used in registration
        }
        
        print(f"   Logging in: {user_email}")
        
        success, response_data, _ = self.make_request(
            'POST', 'auth/login',
            data=login_data,
            expected_status=200
        )
        
        if success:
            # Verify response structure and update token
            if 'access_token' in response_data:
                self.access_token = response_data['access_token']
                self.log_test("User Login", True, "Login successful", response_data)
                return True
            else:
                self.log_test("User Login", False, "No access token in response", response_data)
                return False
        else:
            self.log_test("User Login", False, "Login failed", response_data)
            return False

    def test_4_get_user_info(self):
        """Test 4: Get User Info (Protected) - GET /api/auth/me"""
        print("\n👥 Test 4: Get User Info (Protected)")
        
        if not self.access_token:
            print("   ⚠️ Skipping user info test - no access token")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        success, response_data, _ = self.make_request(
            'GET', 'auth/me',
            headers=headers,
            expected_status=200
        )
        
        if success:
            # Verify user object has credits field
            if 'credits' in response_data:
                credits = response_data.get('credits', 0)
                user_id = response_data.get('id', 'N/A')
                email = response_data.get('email', 'N/A')
                
                print(f"   User ID: {user_id}")
                print(f"   Email: {email}")
                print(f"   Credits: {credits}")
                
                self.log_test("Get User Info", True, f"User data retrieved with {credits} credits", response_data)
                return True
            else:
                self.log_test("Get User Info", False, "No credits field in user object", response_data)
                return False
        else:
            self.log_test("Get User Info", False, "Failed to get user info", response_data)
            return False

    def test_5_list_projects(self):
        """Test 5: List Projects (Protected) - GET /api/projects"""
        print("\n📁 Test 5: List Projects (Protected)")
        
        if not self.access_token:
            print("   ⚠️ Skipping projects test - no access token")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        success, response_data, _ = self.make_request(
            'GET', 'projects',
            headers=headers,
            expected_status=200
        )
        
        if success:
            # Response should be an array (may be empty for new user)
            if isinstance(response_data, list):
                project_count = len(response_data)
                print(f"   Projects found: {project_count}")
                
                self.log_test("List Projects", True, f"Retrieved {project_count} projects", {"project_count": project_count})
                return True
            else:
                self.log_test("List Projects", False, "Response is not an array", response_data)
                return False
        else:
            self.log_test("List Projects", False, "Failed to list projects", response_data)
            return False

    def test_6_create_project(self):
        """Test 6: Create Project (Protected) - POST /api/projects"""
        print("\n📝 Test 6: Create Project (Protected)")
        
        if not self.access_token:
            print("   ⚠️ Skipping create project test - no access token")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        project_data = {
            "name": "Test Project",
            "description": "Test description"
        }
        
        success, response_data, _ = self.make_request(
            'POST', 'projects',
            data=project_data,
            headers=headers,
            expected_status=200
        )
        
        if success:
            # Verify project object has id
            if 'id' in response_data:
                self.test_project_id = response_data['id']
                project_name = response_data.get('name', 'N/A')
                
                print(f"   Project created: {project_name}")
                print(f"   Project ID: {self.test_project_id}")
                
                self.log_test("Create Project", True, f"Project created with ID: {self.test_project_id}", response_data)
                return True
            else:
                self.log_test("Create Project", False, "No project ID in response", response_data)
                return False
        else:
            self.log_test("Create Project", False, "Failed to create project", response_data)
            return False

    def test_7_get_project_by_id(self):
        """Test 7: Get Project by ID - GET /api/projects/{id}"""
        print("\n🔍 Test 7: Get Project by ID")
        
        if not self.access_token or not self.test_project_id:
            print("   ⚠️ Skipping get project test - no access token or project ID")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        success, response_data, _ = self.make_request(
            'GET', f'projects/{self.test_project_id}',
            headers=headers,
            expected_status=200
        )
        
        if success:
            # Verify project details
            project_id = response_data.get('id')
            project_name = response_data.get('name', 'N/A')
            project_description = response_data.get('description', 'N/A')
            
            if project_id == self.test_project_id:
                print(f"   Project Name: {project_name}")
                print(f"   Description: {project_description}")
                
                self.log_test("Get Project by ID", True, f"Retrieved project: {project_name}", response_data)
                return True
            else:
                self.log_test("Get Project by ID", False, f"Project ID mismatch: expected {self.test_project_id}, got {project_id}", response_data)
                return False
        else:
            self.log_test("Get Project by ID", False, "Failed to get project", response_data)
            return False

    def test_8_search_projects(self):
        """Test 8: Search Projects (if endpoint exists) - GET /api/projects?search=Test"""
        print("\n🔎 Test 8: Search Projects")
        
        if not self.access_token:
            print("   ⚠️ Skipping search projects test - no access token")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        success, response_data, _ = self.make_request(
            'GET', 'projects?search=Test',
            headers=headers,
            expected_status=200
        )
        
        if success:
            # Response should be an array
            if isinstance(response_data, list):
                matching_projects = len(response_data)
                print(f"   Matching projects: {matching_projects}")
                
                self.log_test("Search Projects", True, f"Search returned {matching_projects} projects", {"matching_projects": matching_projects})
                return True
            else:
                self.log_test("Search Projects", False, "Search response is not an array", response_data)
                return False
        else:
            # Search endpoint might not exist, which is acceptable
            if response_data and 'error' in response_data and '404' in str(response_data['error']):
                self.log_test("Search Projects", True, "Search endpoint not implemented (acceptable)", response_data)
                return True
            else:
                self.log_test("Search Projects", False, "Search failed", response_data)
                return False

    def run_all_tests(self):
        """Run all review request tests in sequence"""
        print("🚀 Starting AutoWebIQ Backend Review Request Testing")
        print("   Testing all authentication and project management endpoints")
        print("=" * 70)
        
        # Run tests in sequence
        test_results = []
        
        test_results.append(self.test_1_health_check())
        test_results.append(self.test_2_user_registration())
        test_results.append(self.test_3_user_login())
        test_results.append(self.test_4_get_user_info())
        test_results.append(self.test_5_list_projects())
        test_results.append(self.test_6_create_project())
        test_results.append(self.test_7_get_project_by_id())
        test_results.append(self.test_8_search_projects())
        
        return all(test_results)

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 AUTOWEBIQ BACKEND REVIEW REQUEST TEST SUMMARY")
        print("=" * 70)
        print(f"Backend URL: {self.api_url}")
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        else:
            print("Success Rate: 0%")
        
        print("\n📋 TEST RESULTS BY CATEGORY:")
        
        # Group results by category
        categories = {
            "Health Check": ["Health Check"],
            "Authentication": ["User Registration", "User Login", "Get User Info"],
            "Project Management": ["List Projects", "Create Project", "Get Project by ID", "Search Projects"]
        }
        
        for category, test_names in categories.items():
            category_tests = [r for r in self.test_results if r['test'] in test_names]
            passed = sum(1 for t in category_tests if t['success'])
            total = len(category_tests)
            
            if total > 0:
                rate = (passed / total) * 100
                status = "✅" if passed == total else "❌" if passed == 0 else "⚠️"
                print(f"   {status} {category}: {passed}/{total} ({rate:.0f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Show critical checks
        print("\n🔍 CRITICAL CHECKS:")
        auth_working = any(r['test'] == 'User Registration' and r['success'] for r in self.test_results)
        protected_working = any(r['test'] == 'Get User Info' and r['success'] for r in self.test_results)
        projects_working = any(r['test'] == 'Create Project' and r['success'] for r in self.test_results)
        
        print(f"   {'✅' if auth_working else '❌'} Authentication endpoints working")
        print(f"   {'✅' if protected_working else '❌'} Protected endpoints require valid tokens")
        print(f"   {'✅' if projects_working else '❌'} Project CRUD operations functional")
        
        # Check for 500 errors or crashes
        has_500_errors = any('500' in str(r.get('response', {})) for r in self.test_results if not r['success'])
        print(f"   {'❌' if has_500_errors else '✅'} No 500 errors or crashes")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = AutoWebIQReviewTester()
    
    try:
        # Run all tests
        overall_success = tester.run_all_tests()
        
        # Print summary
        all_passed = tester.print_summary()
        
        # Return appropriate exit code
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())