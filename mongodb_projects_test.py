#!/usr/bin/env python3
"""
MongoDB Projects Endpoints Test - Quick Validation
Testing 3 critical project endpoints after MongoDB fix
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://aiweb-builder-2.preview.emergentagent.com/api"
TEST_USER = {
    "email": "demo@test.com",
    "password": "Demo123456"
}

class MongoDBProjectsTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_project_id = None
        self.results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, status, status_code, response_data=None, error=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result["response_summary"] = self._summarize_response(response_data)
        if error:
            result["error"] = str(error)
            
        self.results.append(result)
        print(f"{result['status']} {test_name} - Status: {status_code}")
        if error:
            print(f"   Error: {error}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {self._summarize_response(response_data)}")
            
    def _summarize_response(self, data):
        """Create response summary with key fields only"""
        if isinstance(data, dict):
            if "projects" in data:
                return f"projects array with {len(data['projects'])} items"
            elif "id" in data and "name" in data:
                return f"project object (id: {data['id'][:8]}..., name: {data['name']})"
            elif "access_token" in data:
                return "authentication token received"
            else:
                return f"object with keys: {list(data.keys())}"
        return str(data)[:100]
        
    async def login(self):
        """Step 1: Login with demo account"""
        print("\n=== STEP 1: LOGIN ===")
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=TEST_USER,
                timeout=10
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200 and "access_token" in response_data:
                    self.auth_token = response_data["access_token"]
                    self.log_result("Login", True, status_code, response_data)
                    return True
                else:
                    self.log_result("Login", False, status_code, response_data)
                    return False
                    
        except Exception as e:
            self.log_result("Login", False, 0, error=e)
            return False
            
    async def test_get_projects(self):
        """Step 2: GET /api/projects - List all projects"""
        print("\n=== STEP 2: GET /api/projects ===")
        
        if not self.auth_token:
            self.log_result("GET /api/projects", False, 0, error="No auth token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{BACKEND_URL}/projects",
                headers=headers,
                timeout=10
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                # Success criteria: 200 status and projects array
                success = (
                    status_code == 200 and 
                    isinstance(response_data, dict) and 
                    "projects" in response_data and
                    isinstance(response_data["projects"], list)
                )
                
                self.log_result("GET /api/projects", success, status_code, response_data)
                return success
                
        except Exception as e:
            self.log_result("GET /api/projects", False, 0, error=e)
            return False
            
    async def test_create_project(self):
        """Step 3: POST /api/projects/create - Create new project"""
        print("\n=== STEP 3: POST /api/projects/create ===")
        
        if not self.auth_token:
            self.log_result("POST /api/projects/create", False, 0, error="No auth token")
            return False
            
        project_data = {
            "name": "Test MongoDB Project",
            "description": "Testing MongoDB endpoints"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.post(
                f"{BACKEND_URL}/projects/create",
                headers=headers,
                json=project_data,
                timeout=10
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                # Success criteria: 200 status and project object with id, name, description
                success = (
                    status_code == 200 and 
                    isinstance(response_data, dict) and 
                    "id" in response_data and
                    "name" in response_data and
                    "description" in response_data and
                    response_data["name"] == project_data["name"]
                )
                
                if success:
                    self.test_project_id = response_data["id"]
                    
                self.log_result("POST /api/projects/create", success, status_code, response_data)
                return success
                
        except Exception as e:
            self.log_result("POST /api/projects/create", False, 0, error=e)
            return False
            
    async def test_get_specific_project(self):
        """Step 4: GET /api/projects/{project_id} - Get specific project"""
        print("\n=== STEP 4: GET /api/projects/{project_id} ===")
        
        if not self.auth_token:
            self.log_result("GET /api/projects/{id}", False, 0, error="No auth token")
            return False
            
        if not self.test_project_id:
            self.log_result("GET /api/projects/{id}", False, 0, error="No project_id from create test")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{BACKEND_URL}/projects/{self.test_project_id}",
                headers=headers,
                timeout=10
            ) as response:
                status_code = response.status
                response_data = await response.json()
                
                # Success criteria: 200 status and project object (not 404, not 500)
                success = (
                    status_code == 200 and 
                    isinstance(response_data, dict) and 
                    "id" in response_data and
                    response_data["id"] == self.test_project_id
                )
                
                self.log_result("GET /api/projects/{id}", success, status_code, response_data)
                return success
                
        except Exception as e:
            self.log_result("GET /api/projects/{id}", False, 0, error=e)
            return False
            
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "="*60)
        print("MONGODB PROJECTS ENDPOINTS TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r["status"])
        total = len(self.results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.results:
            print(f"{result['status']} {result['test']}")
            print(f"   Status Code: {result['status_code']}")
            if "response_summary" in result:
                print(f"   Response: {result['response_summary']}")
            if "error" in result:
                print(f"   Error: {result['error']}")
            print()
            
        # Success criteria check
        critical_tests = [
            "GET /api/projects",
            "POST /api/projects/create", 
            "GET /api/projects/{id}"
        ]
        
        critical_passed = sum(1 for r in self.results 
                            if r["test"] in critical_tests and "✅ PASS" in r["status"])
        
        print("="*60)
        if critical_passed == 3:
            print("🎉 SUCCESS: All 3 MongoDB project endpoints working!")
            print("✅ No PostgreSQL connection errors")
            print("✅ All endpoints return 200 status")
            print("✅ Response data structure is correct")
        else:
            print("❌ FAILURE: Some MongoDB endpoints not working")
            print(f"Critical tests passed: {critical_passed}/3")
            
        return critical_passed == 3
        
    async def run_all_tests(self):
        """Run all MongoDB project endpoint tests"""
        print("Starting MongoDB Projects Endpoints Test")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER['email']}")
        
        await self.setup_session()
        
        try:
            # Run tests in sequence
            login_success = await self.login()
            if not login_success:
                print("❌ Login failed - cannot continue with project tests")
                return False
                
            # Test all 3 endpoints
            await self.test_get_projects()
            await self.test_create_project()
            await self.test_get_specific_project()
            
            # Print summary
            return self.print_summary()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = MongoDBProjectsTest()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 MONGODB FIX VERIFICATION: COMPLETE ✅")
    else:
        print("\n🚨 MONGODB FIX VERIFICATION: ISSUES FOUND ❌")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())