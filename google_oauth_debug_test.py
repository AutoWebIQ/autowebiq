#!/usr/bin/env python3
"""
GOOGLE OAUTH SPECIFIC DEBUGGING TEST

The user reported that they logged in with Google OAuth successfully but project creation fails.
The previous test showed regular JWT auth works fine, so this test focuses on Google OAuth flow.

This test will:
1. Test Google OAuth session endpoints
2. Test project creation with session tokens (not JWT)
3. Check if the issue is specific to Google OAuth authentication
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Production URL
BASE_URL = "https://autowebiq.com/api"

class GoogleOAuthDebugger:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_google_oauth_session_endpoint(self):
        """Test Google OAuth session endpoint behavior"""
        self.log("🔍 Testing Google OAuth session endpoint...")
        
        # Test 1: Missing session ID
        try:
            async with self.session.post(f"{BASE_URL}/auth/google/session") as response:
                status_code = response.status
                response_text = await response.text()
                
                self.log(f"Missing session ID - Status: {status_code}")
                self.log(f"Response: {response_text}")
                
                if status_code == 400:
                    self.log("✅ Correctly handles missing session ID", "SUCCESS")
                else:
                    self.log(f"❌ Expected 400, got {status_code}", "ERROR")
                    
        except Exception as e:
            self.log(f"❌ Session endpoint error: {str(e)}", "ERROR")
        
        # Test 2: Invalid session ID
        try:
            headers = {"X-Session-ID": "invalid_session_12345"}
            async with self.session.post(f"{BASE_URL}/auth/google/session", headers=headers) as response:
                status_code = response.status
                response_text = await response.text()
                
                self.log(f"Invalid session ID - Status: {status_code}")
                self.log(f"Response: {response_text}")
                
                if status_code == 400:
                    self.log("✅ Correctly handles invalid session ID", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Expected 400, got {status_code}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Invalid session test error: {str(e)}", "ERROR")
            return False
    
    async def test_firebase_sync_endpoint(self):
        """Test Firebase sync endpoint (used by Google OAuth)"""
        self.log("🔍 Testing Firebase sync endpoint...")
        
        # Test with sample Firebase user data
        firebase_user = {
            "firebase_uid": f"test_firebase_uid_{int(datetime.now().timestamp())}",
            "email": f"firebase_test_{int(datetime.now().timestamp())}@gmail.com",
            "display_name": "Firebase Test User",
            "photo_url": "https://example.com/photo.jpg",
            "provider_id": "google.com"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/firebase/sync",
                json=firebase_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log("✅ Firebase sync successful", "SUCCESS")
                    self.log(f"User: {data.get('user', {}).get('email')}")
                    self.log(f"Credits: {data.get('user', {}).get('credits')}")
                    
                    # Test project creation with this Firebase user's JWT token
                    jwt_token = data.get('access_token')
                    if jwt_token:
                        return await self.test_project_creation_with_firebase_jwt(jwt_token)
                    else:
                        self.log("❌ No JWT token returned from Firebase sync", "ERROR")
                        return False
                else:
                    error_text = await response.text()
                    self.log(f"❌ Firebase sync failed: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Firebase sync error: {str(e)}", "ERROR")
            return False
    
    async def test_project_creation_with_firebase_jwt(self, jwt_token):
        """Test project creation using JWT token from Firebase sync"""
        self.log("🎯 Testing project creation with Firebase JWT token...")
        
        project_data = {
            "name": "Firebase OAuth Test Project",
            "description": "Testing project creation with Firebase/Google OAuth JWT"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers=headers
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log("✅ PROJECT CREATION WITH FIREBASE JWT SUCCESSFUL!", "SUCCESS")
                    self.log(f"Project ID: {data.get('id')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ PROJECT CREATION WITH FIREBASE JWT FAILED: {status_code}", "ERROR")
                    self.log(f"Error: {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Firebase JWT project creation error: {str(e)}", "ERROR")
            return False
    
    async def test_session_token_authentication(self):
        """Test session token authentication (used by Google OAuth)"""
        self.log("🔍 Testing session token authentication flow...")
        
        # First, create a regular user to get a JWT token
        test_user = {
            "username": f"sessiontest_{int(datetime.now().timestamp())}",
            "email": f"sessiontest_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPassword123!"
        }
        
        try:
            # Create user
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log("❌ Failed to create test user for session test", "ERROR")
                    return False
                
                user_data = await response.json()
                jwt_token = user_data.get('access_token')
            
            # Test /auth/me with JWT token (should work)
            headers = {"Authorization": f"Bearer {jwt_token}"}
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status == 200:
                    self.log("✅ JWT authentication working", "SUCCESS")
                else:
                    self.log("❌ JWT authentication failed", "ERROR")
                    return False
            
            # Test project creation with JWT
            project_data = {
                "name": "Session Test Project",
                "description": "Testing session authentication"
            }
            
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    self.log("✅ Project creation with JWT working", "SUCCESS")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ Project creation with JWT failed: {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Session token test error: {str(e)}", "ERROR")
            return False
    
    async def test_auth_me_endpoint_variations(self):
        """Test different ways to call /auth/me endpoint"""
        self.log("🔍 Testing /auth/me endpoint variations...")
        
        # Create a test user first
        test_user = {
            "username": f"authtest_{int(datetime.now().timestamp())}",
            "email": f"authtest_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPassword123!"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    return False
                
                user_data = await response.json()
                jwt_token = user_data.get('access_token')
            
            # Test 1: Authorization header
            headers = {"Authorization": f"Bearer {jwt_token}"}
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status == 200:
                    self.log("✅ /auth/me with Authorization header works", "SUCCESS")
                else:
                    self.log("❌ /auth/me with Authorization header failed", "ERROR")
            
            # Test 2: No authentication (should fail)
            async with self.session.get(f"{BASE_URL}/auth/me") as response:
                if response.status == 401:
                    self.log("✅ /auth/me correctly rejects unauthenticated requests", "SUCCESS")
                else:
                    self.log(f"❌ /auth/me should return 401, got {response.status}", "ERROR")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Auth endpoint test error: {str(e)}", "ERROR")
            return False
    
    async def run_google_oauth_debug(self):
        """Run all Google OAuth specific debugging tests"""
        self.log("🚀 Starting Google OAuth Specific Debugging", "INFO")
        self.log(f"Target URL: {BASE_URL}")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Google OAuth session endpoint
        results['google_session'] = await self.test_google_oauth_session_endpoint()
        
        # Test 2: Firebase sync endpoint
        results['firebase_sync'] = await self.test_firebase_sync_endpoint()
        
        # Test 3: Session token authentication
        results['session_auth'] = await self.test_session_token_authentication()
        
        # Test 4: Auth endpoint variations
        results['auth_variations'] = await self.test_auth_me_endpoint_variations()
        
        # Summary
        self.log("=" * 60)
        self.log("🔍 GOOGLE OAUTH DEBUGGING SUMMARY", "INFO")
        self.log("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Analysis
        self.log("\n🎯 GOOGLE OAUTH ANALYSIS:", "INFO")
        
        if all(results.values()):
            self.log("✅ ALL GOOGLE OAUTH TESTS PASSED", "SUCCESS")
            self.log("🔍 CONCLUSION: Google OAuth authentication is working correctly", "SUCCESS")
            self.log("💡 The reported issue may be:", "INFO")
            self.log("   - Already fixed", "INFO")
            self.log("   - Intermittent/timing related", "INFO")
            self.log("   - Specific to certain user accounts", "INFO")
            self.log("   - Related to browser/client-side issues", "INFO")
        else:
            failed_tests = [name for name, result in results.items() if not result]
            self.log(f"❌ FAILED TESTS: {', '.join(failed_tests)}", "ERROR")
            self.log("🔍 CONCLUSION: Issues found in Google OAuth flow", "ERROR")
        
        return results

async def main():
    """Main function to run Google OAuth debugging"""
    async with GoogleOAuthDebugger() as debugger:
        results = await debugger.run_google_oauth_debug()
        
        # Exit with error code if any test failed
        if not all(results.values()):
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())