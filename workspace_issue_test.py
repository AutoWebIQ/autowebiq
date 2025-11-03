#!/usr/bin/env python3
"""
URGENT: Workspace Blank Page Issue Testing
User reports blank workspace page after clicking "Create Project"

Test Configuration:
- Backend: https://autowebiq.com/api
- Test with demo user: demo@test.com / Demo123456

Critical Test Cases:
1. Test Project Creation Flow
2. Test Get Project Endpoint  
3. Test Projects List
4. Test WebSocket Connection
"""

import requests
import json
import sys
import websocket
import threading
import time
from datetime import datetime

# Test Configuration
BASE_URL = "https://multiagent-web.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

# Headers
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class WorkspaceIssueTester:
    def __init__(self):
        self.test_results = []
        self.critical_failures = []
        self.jwt_token = None
        self.demo_user_data = None
        self.created_project_id = None
        
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
            
    def make_request(self, method, endpoint, data=None, auth_token=None, timeout=10):
        """Make HTTP request"""
        url = f"{BASE_URL}{endpoint}"
        headers = HEADERS.copy()
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"   Request error: {str(e)}")
            return None
            
    def test_demo_login(self):
        """CRITICAL: Login as demo user"""
        print("\n🔍 CRITICAL TEST: Demo User Login")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if not response:
            self.log_test("Demo Login - Connection", "FAIL", "Failed to connect to backend", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Demo Login - Status Code", "FAIL", f"Expected 200, got {response.status_code}: {response.text}", "CRITICAL")
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
            self.log_test("Demo Login - JSON", "FAIL", f"Invalid JSON response: {response.text}", "CRITICAL")
            return False
            
    def test_project_creation_flow(self):
        """CRITICAL: Test Project Creation Flow"""
        print("\n🔍 CRITICAL TEST: Project Creation Flow")
        
        if not self.jwt_token:
            self.log_test("Project Creation - No Token", "FAIL", "No JWT token available", "CRITICAL")
            return False
            
        # Test data as specified in review request
        project_data = {
            "name": "Test Project",
            "description": "Test description", 
            "type": "website"
        }
        
        response = self.make_request("POST", "/projects/create", project_data, auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Project Creation - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Project Creation - Status Code", "FAIL", f"Expected 200, got {response.status_code}: {response.text}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check if project_id is returned
            project_id = data.get("id")
            if not project_id:
                self.log_test("Project Creation - Project ID", "FAIL", "No project ID returned", "CRITICAL")
                return False
                
            # Store project ID for later tests
            self.created_project_id = project_id
            
            # Check required fields
            required_fields = ["name", "description", "user_id", "created_at"]
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                    
            if missing_fields:
                self.log_test("Project Creation - Missing Fields", "FAIL", f"Missing fields: {missing_fields}", "CRITICAL")
                return False
                
            self.log_test("Project Creation", "PASS", f"Project created with ID: {project_id[:8]}...", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Project Creation - JSON", "FAIL", f"Invalid JSON response: {response.text}", "CRITICAL")
            return False
            
    def test_get_project_endpoint(self):
        """CRITICAL: Test Get Project Endpoint"""
        print("\n🔍 CRITICAL TEST: Get Project Endpoint")
        
        if not self.jwt_token:
            self.log_test("Get Project - No Token", "FAIL", "No JWT token available", "CRITICAL")
            return False
            
        if not self.created_project_id:
            self.log_test("Get Project - No Project ID", "FAIL", "No project ID available", "CRITICAL")
            return False
            
        response = self.make_request("GET", f"/projects/{self.created_project_id}", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Get Project - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Get Project - Status Code", "FAIL", f"Expected 200, got {response.status_code}: {response.text}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check if all required fields are present
            required_fields = ["id", "name", "description", "user_id", "status", "created_at"]
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                    
            if missing_fields:
                self.log_test("Get Project - Missing Fields", "FAIL", f"Missing fields: {missing_fields}", "CRITICAL")
                return False
                
            # Check if project ID matches
            if data.get("id") != self.created_project_id:
                self.log_test("Get Project - ID Mismatch", "FAIL", f"Expected {self.created_project_id}, got {data.get('id')}", "CRITICAL")
                return False
                
            # Log all returned fields for debugging
            returned_fields = list(data.keys())
            self.log_test("Get Project", "PASS", f"Project data retrieved with fields: {returned_fields}", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Get Project - JSON", "FAIL", f"Invalid JSON response: {response.text}", "CRITICAL")
            return False
            
    def test_projects_list(self):
        """CRITICAL: Test Projects List"""
        print("\n🔍 CRITICAL TEST: Projects List")
        
        if not self.jwt_token:
            self.log_test("Projects List - No Token", "FAIL", "No JWT token available", "CRITICAL")
            return False
            
        response = self.make_request("GET", "/projects", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Projects List - Connection", "FAIL", "Failed to connect", "CRITICAL")
            return False
            
        if response.status_code != 200:
            self.log_test("Projects List - Status Code", "FAIL", f"Expected 200, got {response.status_code}: {response.text}", "CRITICAL")
            return False
            
        try:
            data = response.json()
            
            # Check if projects array exists
            if "projects" not in data:
                self.log_test("Projects List - Structure", "FAIL", "No 'projects' key in response", "CRITICAL")
                return False
                
            projects = data["projects"]
            if not isinstance(projects, list):
                self.log_test("Projects List - Type", "FAIL", "Projects is not a list", "CRITICAL")
                return False
                
            # Check if our created project is in the list
            project_found = False
            if self.created_project_id:
                for project in projects:
                    if project.get("id") == self.created_project_id:
                        project_found = True
                        break
                        
            if self.created_project_id and not project_found:
                self.log_test("Projects List - Created Project Missing", "FAIL", "Created project not found in list", "CRITICAL")
                return False
                
            self.log_test("Projects List", "PASS", f"Retrieved {len(projects)} projects, created project found: {project_found}", "CRITICAL")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Projects List - JSON", "FAIL", f"Invalid JSON response: {response.text}", "CRITICAL")
            return False
            
    def test_project_messages_endpoint(self):
        """HIGH: Test Project Messages Endpoint"""
        print("\n🔍 HIGH PRIORITY TEST: Project Messages")
        
        if not self.jwt_token:
            self.log_test("Project Messages - No Token", "FAIL", "No JWT token available", "HIGH")
            return False
            
        if not self.created_project_id:
            self.log_test("Project Messages - No Project ID", "FAIL", "No project ID available", "HIGH")
            return False
            
        response = self.make_request("GET", f"/projects/{self.created_project_id}/messages", auth_token=self.jwt_token)
        
        if not response:
            self.log_test("Project Messages - Connection", "FAIL", "Failed to connect", "HIGH")
            return False
            
        if response.status_code != 200:
            self.log_test("Project Messages - Status Code", "FAIL", f"Expected 200, got {response.status_code}: {response.text}", "HIGH")
            return False
            
        try:
            data = response.json()
            
            # Check if messages array exists
            if "messages" not in data:
                self.log_test("Project Messages - Structure", "FAIL", "No 'messages' key in response", "HIGH")
                return False
                
            messages = data["messages"]
            if not isinstance(messages, list):
                self.log_test("Project Messages - Type", "FAIL", "Messages is not a list", "HIGH")
                return False
                
            self.log_test("Project Messages", "PASS", f"Retrieved {len(messages)} messages", "HIGH")
            return True
            
        except json.JSONDecodeError:
            self.log_test("Project Messages - JSON", "FAIL", f"Invalid JSON response: {response.text}", "HIGH")
            return False
            
    def test_websocket_connection(self):
        """HIGH: Test WebSocket Connection"""
        print("\n🔍 HIGH PRIORITY TEST: WebSocket Connection")
        
        if not self.created_project_id:
            self.log_test("WebSocket - No Project ID", "FAIL", "No project ID available", "HIGH")
            return False
            
        # Convert HTTP/HTTPS URL to WS/WSS URL for WebSocket
        if BASE_URL.startswith("https://"):
            ws_url = BASE_URL.replace("https://", "wss://").replace("/api", "") + f"/ws/{self.created_project_id}"
        else:
            ws_url = BASE_URL.replace("http://", "ws://").replace("/api", "") + f"/ws/{self.created_project_id}"
        
        connection_successful = False
        error_message = ""
        
        def on_open(ws):
            nonlocal connection_successful
            connection_successful = True
            print(f"   WebSocket connected to: {ws_url}")
            ws.close()
            
        def on_error(ws, error):
            nonlocal error_message
            error_message = str(error)
            print(f"   WebSocket error: {error}")
            
        def on_close(ws, close_status_code, close_msg):
            print(f"   WebSocket closed")
            
        try:
            # Create WebSocket connection with auth header if possible
            headers = []
            if self.jwt_token:
                headers.append(f"Authorization: Bearer {self.jwt_token}")
                
            ws = websocket.WebSocketApp(
                ws_url,
                header=headers,
                on_open=on_open,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread with timeout
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection attempt
            time.sleep(3)
            
            if connection_successful:
                self.log_test("WebSocket Connection", "PASS", f"Successfully connected to {ws_url}", "HIGH")
                return True
            else:
                self.log_test("WebSocket Connection", "FAIL", f"Failed to connect: {error_message}", "HIGH")
                return False
                
        except Exception as e:
            self.log_test("WebSocket Connection", "FAIL", f"Exception: {str(e)}", "HIGH")
            return False
            
    def run_workspace_issue_tests(self):
        """Run all tests to diagnose workspace blank page issue"""
        print("🚨 URGENT: WORKSPACE BLANK PAGE ISSUE TESTING")
        print(f"Backend URL: {BASE_URL}")
        print(f"Demo Account: {DEMO_EMAIL}")
        print("=" * 60)
        
        # Test sequence to identify the root cause
        tests = [
            ("Demo Login", self.test_demo_login),
            ("Project Creation Flow", self.test_project_creation_flow),
            ("Get Project Endpoint", self.test_get_project_endpoint),
            ("Projects List", self.test_projects_list),
            ("Project Messages", self.test_project_messages_endpoint),
            ("WebSocket Connection", self.test_websocket_connection)
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Running {test_name} ---")
            success = test_func()
            if not success and test_name in ["Demo Login", "Project Creation Flow"]:
                print(f"\n🚨 CRITICAL TEST FAILED: {test_name} - STOPPING EXECUTION")
                break
                
        # Generate diagnostic summary
        self.generate_diagnostic_summary()
        
    def generate_diagnostic_summary(self):
        """Generate diagnostic summary for workspace issue"""
        print("\n" + "=" * 60)
        print("🔍 WORKSPACE ISSUE DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        
        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS (Likely Root Cause):")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   ❌ {result['test']}: {result['details']}")
                    
        print(f"\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["status"] == "PASS":
                print(f"   ✅ {result['test']}: {result['details']}")
                
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        login_success = any(t["test"].startswith("Demo Login") and t["status"] == "PASS" for t in self.test_results)
        project_creation_success = any(t["test"].startswith("Project Creation") and t["status"] == "PASS" for t in self.test_results)
        get_project_success = any(t["test"].startswith("Get Project") and t["status"] == "PASS" for t in self.test_results)
        
        if not login_success:
            print("   🚨 CRITICAL: Authentication is failing - users cannot login")
        elif not project_creation_success:
            print("   🚨 CRITICAL: Project creation is failing - no project ID returned")
        elif not get_project_success:
            print("   🚨 CRITICAL: Project retrieval is failing - workspace cannot load project data")
        else:
            print("   ✅ Basic flow working - issue may be in frontend or WebSocket connection")
            
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not login_success:
            print("   1. Check authentication endpoints and demo user credentials")
            print("   2. Verify JWT token generation and validation")
        elif not project_creation_success:
            print("   1. Check project creation endpoint implementation")
            print("   2. Verify database connection and project storage")
        elif not get_project_success:
            print("   1. Check project retrieval endpoint")
            print("   2. Verify project data structure and required fields")
        else:
            print("   1. Check frontend workspace component for data handling")
            print("   2. Verify WebSocket connection for real-time updates")
            print("   3. Check browser console for JavaScript errors")
            
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = WorkspaceIssueTester()
    success = tester.run_workspace_issue_tests()
    sys.exit(0 if success else 1)