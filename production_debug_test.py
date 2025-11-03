#!/usr/bin/env python3
"""
PRODUCTION DEBUGGING TEST - Project Creation Failing on autowebiq.com

This test specifically targets the production issue where:
- User logged in with Google OAuth successfully
- Health check shows "healthy" 
- But project creation fails with "Failed to create project" error

Test URL: https://autowebiq.com/api
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Production URL
BASE_URL = "https://autowebiq.com/api"

class ProductionDebugger:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_info = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_health_check(self):
        """Test 1: Verify health check status"""
        self.log("🔍 Testing health check endpoint...")
        
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                status_code = response.status
                data = await response.json()
                
                self.log(f"Health Check Status: {status_code}")
                self.log(f"Health Check Response: {json.dumps(data, indent=2)}")
                
                if status_code == 200:
                    self.log("✅ Health check passed", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Health check failed with status {status_code}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False
    
    async def create_test_user(self):
        """Test 2: Create a test user for authentication"""
        self.log("👤 Creating test user for authentication...")
        
        test_user = {
            "username": f"prodtest_{int(datetime.now().timestamp())}",
            "email": f"prodtest_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPassword123!"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    self.user_info = data.get('user')
                    self.log(f"✅ User created successfully: {self.user_info.get('email')}", "SUCCESS")
                    self.log(f"User Credits: {self.user_info.get('credits')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ User creation failed: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ User creation error: {str(e)}", "ERROR")
            return False
    
    async def test_auth_token_validity(self):
        """Test 3: Verify auth token works with /auth/me"""
        self.log("🔐 Testing auth token validity...")
        
        if not self.auth_token:
            self.log("❌ No auth token available", "ERROR")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log(f"✅ Auth token valid - User: {data.get('email')}", "SUCCESS")
                    self.log(f"User ID: {data.get('id')}")
                    self.log(f"Credits: {data.get('credits')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ Auth token invalid: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Auth validation error: {str(e)}", "ERROR")
            return False
    
    async def test_project_creation_without_auth(self):
        """Test 4: Try project creation without auth (should get 401)"""
        self.log("🚫 Testing project creation without auth (expecting 401)...")
        
        project_data = {
            "name": "Test Production Project",
            "description": "Testing project creation on autowebiq.com"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                error_text = await response.text()
                
                if status_code == 401:
                    self.log("✅ Correctly returned 401 for unauthenticated request", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Expected 401, got {status_code}: {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Unauth test error: {str(e)}", "ERROR")
            return False
    
    async def test_project_creation_with_invalid_token(self):
        """Test 5: Try project creation with invalid token (should get 401)"""
        self.log("🔒 Testing project creation with invalid token (expecting 401)...")
        
        project_data = {
            "name": "Test Production Project",
            "description": "Testing project creation on autowebiq.com"
        }
        
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers=headers
            ) as response:
                status_code = response.status
                error_text = await response.text()
                
                if status_code == 401:
                    self.log("✅ Correctly returned 401 for invalid token", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Expected 401, got {status_code}: {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Invalid token test error: {str(e)}", "ERROR")
            return False
    
    async def test_project_creation_with_valid_token(self):
        """Test 6: MAIN TEST - Try project creation with valid token"""
        self.log("🎯 MAIN TEST: Testing project creation with valid token...")
        
        if not self.auth_token:
            self.log("❌ No valid auth token available", "ERROR")
            return False
        
        project_data = {
            "name": "Test Production Project",
            "description": "Testing project creation on autowebiq.com"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            self.log(f"Request URL: {BASE_URL}/projects/create")
            self.log(f"Request Headers: {headers}")
            self.log(f"Request Data: {json.dumps(project_data, indent=2)}")
            
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers=headers
            ) as response:
                status_code = response.status
                
                self.log(f"Response Status: {status_code}")
                self.log(f"Response Headers: {dict(response.headers)}")
                
                try:
                    response_data = await response.json()
                    self.log(f"Response Data: {json.dumps(response_data, indent=2)}")
                except:
                    response_text = await response.text()
                    self.log(f"Response Text: {response_text}")
                    response_data = {"error": response_text}
                
                if status_code == 200:
                    self.log("✅ PROJECT CREATION SUCCESSFUL!", "SUCCESS")
                    self.log(f"Project ID: {response_data.get('id')}")
                    self.log(f"Project Name: {response_data.get('name')}")
                    return True, response_data
                else:
                    self.log(f"❌ PROJECT CREATION FAILED: Status {status_code}", "ERROR")
                    self.log(f"Error Details: {response_data}", "ERROR")
                    return False, response_data
                    
        except Exception as e:
            self.log(f"❌ Project creation exception: {str(e)}", "ERROR")
            return False, {"error": str(e)}
    
    async def test_mongodb_write_operation(self):
        """Test 7: Test if MongoDB is working for write operations"""
        self.log("💾 Testing MongoDB write operations...")
        
        if not self.auth_token:
            self.log("❌ No auth token for MongoDB test", "ERROR")
            return False
        
        # Try to get projects list (read operation)
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(f"{BASE_URL}/projects", headers=headers) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log(f"✅ MongoDB read operation successful", "SUCCESS")
                    self.log(f"Projects count: {len(data.get('projects', []))}")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ MongoDB read failed: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ MongoDB test error: {str(e)}", "ERROR")
            return False
    
    async def run_comprehensive_debug(self):
        """Run all debugging tests"""
        self.log("🚀 Starting Production Debugging for autowebiq.com", "INFO")
        self.log(f"Target URL: {BASE_URL}")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Health Check
        results['health_check'] = await self.test_health_check()
        
        # Test 2: Create Test User
        results['user_creation'] = await self.create_test_user()
        
        # Test 3: Validate Auth Token
        if results['user_creation']:
            results['auth_validation'] = await self.test_auth_token_validity()
        else:
            results['auth_validation'] = False
        
        # Test 4: Project Creation Without Auth
        results['unauth_project'] = await self.test_project_creation_without_auth()
        
        # Test 5: Project Creation With Invalid Token
        results['invalid_token_project'] = await self.test_project_creation_with_invalid_token()
        
        # Test 6: MongoDB Read Test
        if results['auth_validation']:
            results['mongodb_read'] = await self.test_mongodb_write_operation()
        else:
            results['mongodb_read'] = False
        
        # Test 7: MAIN TEST - Project Creation With Valid Token
        if results['auth_validation']:
            success, error_details = await self.test_project_creation_with_valid_token()
            results['main_project_creation'] = success
            results['project_creation_details'] = error_details
        else:
            results['main_project_creation'] = False
            results['project_creation_details'] = {"error": "No valid auth token"}
        
        # Summary
        self.log("=" * 60)
        self.log("🔍 PRODUCTION DEBUGGING SUMMARY", "INFO")
        self.log("=" * 60)
        
        for test_name, result in results.items():
            if test_name == 'project_creation_details':
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Main Issue Analysis
        self.log("\n🎯 MAIN ISSUE ANALYSIS:", "INFO")
        if results['main_project_creation']:
            self.log("✅ PROJECT CREATION IS WORKING - No issue found", "SUCCESS")
        else:
            self.log("❌ PROJECT CREATION IS FAILING", "ERROR")
            error_details = results.get('project_creation_details', {})
            
            if 'error' in error_details:
                error_msg = error_details['error']
                self.log(f"Error Message: {error_msg}", "ERROR")
                
                # Analyze error type
                if 'mongodb' in error_msg.lower() or 'database' in error_msg.lower():
                    self.log("🔍 DIAGNOSIS: Database connection issue", "ERROR")
                elif 'validation' in error_msg.lower():
                    self.log("🔍 DIAGNOSIS: Data validation error", "ERROR")
                elif 'auth' in error_msg.lower() or '401' in error_msg:
                    self.log("🔍 DIAGNOSIS: Authentication issue", "ERROR")
                elif '500' in error_msg:
                    self.log("🔍 DIAGNOSIS: Internal server error", "ERROR")
                else:
                    self.log("🔍 DIAGNOSIS: Unknown error - needs further investigation", "ERROR")
        
        return results

async def main():
    """Main function to run production debugging"""
    async with ProductionDebugger() as debugger:
        results = await debugger.run_comprehensive_debug()
        
        # Exit with error code if main test failed
        if not results.get('main_project_creation', False):
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())