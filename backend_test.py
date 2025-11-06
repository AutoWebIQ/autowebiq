#!/usr/bin/env python3
"""
AutoWebIQ Production Domain Testing - LIVE DOMAIN TESTING
Testing the ACTUAL production site at autowebiq.com (not localhost)

CRITICAL: User reports unable to login on autowebiq.com with manual signup/signin OR Google login
Focus: Test the LIVE production domain to identify backend accessibility and auth issues
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
import uuid

# LIVE PRODUCTION DOMAIN - NOT LOCALHOST
BASE_URL = "https://autowebiq.com/api"

class ProductionDomainTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.demo_token = None
        
    async def __aenter__(self):
        # Configure session with proper headers for production
        connector = aiohttp.TCPConnector(ssl=False)  # Allow SSL issues for testing
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'AutoWebIQ-Production-Tester/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str, response_data=None):
        """Log test result with timestamp"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    async def test_health_check_live_domain(self):
        """Test 1: Health Check on LIVE domain - Critical Test"""
        try:
            url = f"{BASE_URL}/health"
            print(f"\n🔍 Testing LIVE domain health check: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        self.log_result(
                            "LIVE Domain Health Check", 
                            True, 
                            f"Backend accessible on production domain (Status: {status_code})",
                            data
                        )
                        return True
                    except json.JSONDecodeError:
                        self.log_result(
                            "LIVE Domain Health Check", 
                            False, 
                            f"Backend responds but invalid JSON (Status: {status_code})",
                            response_text[:200]
                        )
                        return False
                else:
                    self.log_result(
                        "LIVE Domain Health Check", 
                        False, 
                        f"Backend not accessible on production domain (Status: {status_code})",
                        response_text[:200]
                    )
                    return False
                    
        except aiohttp.ClientError as e:
            self.log_result(
                "LIVE Domain Health Check", 
                False, 
                f"Connection failed to production domain: {str(e)}",
                None
            )
            return False
        except Exception as e:
            self.log_result(
                "LIVE Domain Health Check", 
                False, 
                f"Unexpected error: {str(e)}",
                None
            )
            return False
    
    async def test_manual_login_live_domain(self):
        """Test 2: Manual Login on LIVE domain - Critical Test"""
        try:
            url = f"{BASE_URL}/auth/login"
            login_data = {
                "email": "demo@test.com",
                "password": "Demo123456"
            }
            
            print(f"\n🔍 Testing manual login on LIVE domain: {url}")
            print(f"   Credentials: {login_data['email']} / {login_data['password']}")
            
            async with self.session.post(url, json=login_data) as response:
                status_code = response.status
                response_text = await response.text()
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        if 'access_token' in data:
                            self.demo_token = data['access_token']
                            user_info = data.get('user', {})
                            self.log_result(
                                "LIVE Domain Manual Login", 
                                True, 
                                f"Login successful - JWT token received, User: {user_info.get('email', 'N/A')}, Credits: {user_info.get('credits', 'N/A')}",
                                {'token_length': len(self.demo_token), 'user': user_info}
                            )
                            return True
                        else:
                            self.log_result(
                                "LIVE Domain Manual Login", 
                                False, 
                                "Login response missing access_token",
                                data
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_result(
                            "LIVE Domain Manual Login", 
                            False, 
                            f"Invalid JSON response (Status: {status_code})",
                            response_text[:200]
                        )
                        return False
                elif status_code == 401:
                    self.log_result(
                        "LIVE Domain Manual Login", 
                        False, 
                        "Invalid credentials - demo account may not exist on production",
                        response_text[:200]
                    )
                    return False
                else:
                    self.log_result(
                        "LIVE Domain Manual Login", 
                        False, 
                        f"Login failed (Status: {status_code})",
                        response_text[:200]
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "LIVE Domain Manual Login", 
                False, 
                f"Login request failed: {str(e)}",
                None
            )
            return False
    
    async def test_manual_registration_live_domain(self):
        """Test 3: Manual Registration on LIVE domain - Critical Test"""
        try:
            url = f"{BASE_URL}/auth/register"
            
            # Generate unique test user
            test_email = f"test_{uuid.uuid4().hex[:8]}@autowebiq.test"
            registration_data = {
                "username": f"TestUser_{uuid.uuid4().hex[:6]}",
                "email": test_email,
                "password": "TestPassword123!"
            }
            
            print(f"\n🔍 Testing manual registration on LIVE domain: {url}")
            print(f"   Test User: {registration_data['email']}")
            
            async with self.session.post(url, json=registration_data) as response:
                status_code = response.status
                response_text = await response.text()
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        if 'access_token' in data:
                            user_info = data.get('user', {})
                            self.log_result(
                                "LIVE Domain Manual Registration", 
                                True, 
                                f"Registration successful - New user created with {user_info.get('credits', 'N/A')} credits",
                                {'user': user_info}
                            )
                            return True
                        else:
                            self.log_result(
                                "LIVE Domain Manual Registration", 
                                False, 
                                "Registration response missing access_token",
                                data
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_result(
                            "LIVE Domain Manual Registration", 
                            False, 
                            f"Invalid JSON response (Status: {status_code})",
                            response_text[:200]
                        )
                        return False
                elif status_code == 400:
                    self.log_result(
                        "LIVE Domain Manual Registration", 
                        False, 
                        "Registration failed - validation error or email exists",
                        response_text[:200]
                    )
                    return False
                else:
                    self.log_result(
                        "LIVE Domain Manual Registration", 
                        False, 
                        f"Registration failed (Status: {status_code})",
                        response_text[:200]
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "LIVE Domain Manual Registration", 
                False, 
                f"Registration request failed: {str(e)}",
                None
            )
            return False
    
    async def test_cors_headers_live_domain(self):
        """Test 4: CORS Headers Check - Critical for frontend access"""
        try:
            url = f"{BASE_URL}/health"
            
            print(f"\n🔍 Testing CORS headers on LIVE domain: {url}")
            
            # Test preflight OPTIONS request
            headers = {
                'Origin': 'https://autowebiq.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            async with self.session.options(url, headers=headers) as response:
                status_code = response.status
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                    'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
                }
                
                # Check if CORS allows autowebiq.com
                allow_origin = cors_headers.get('Access-Control-Allow-Origin')
                if allow_origin == '*' or 'autowebiq.com' in str(allow_origin):
                    self.log_result(
                        "LIVE Domain CORS Headers", 
                        True, 
                        f"CORS properly configured for autowebiq.com (Status: {status_code})",
                        cors_headers
                    )
                    return True
                else:
                    self.log_result(
                        "LIVE Domain CORS Headers", 
                        False, 
                        f"CORS may not allow autowebiq.com origin (Status: {status_code})",
                        cors_headers
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "LIVE Domain CORS Headers", 
                False, 
                f"CORS test failed: {str(e)}",
                None
            )
            return False
    
    async def test_google_oauth_endpoint_live_domain(self):
        """Test 5: Google OAuth Endpoint - Critical for Google login"""
        try:
            url = f"{BASE_URL}/auth/google"
            
            print(f"\n🔍 Testing Google OAuth endpoint on LIVE domain: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                # OAuth endpoints typically redirect (302) or return specific responses
                if status_code in [200, 302, 400]:  # 400 might be expected without proper params
                    self.log_result(
                        "LIVE Domain Google OAuth", 
                        True, 
                        f"Google OAuth endpoint accessible (Status: {status_code})",
                        {'status': status_code, 'response_preview': response_text[:100]}
                    )
                    return True
                else:
                    self.log_result(
                        "LIVE Domain Google OAuth", 
                        False, 
                        f"Google OAuth endpoint not accessible (Status: {status_code})",
                        response_text[:200]
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "LIVE Domain Google OAuth", 
                False, 
                f"Google OAuth test failed: {str(e)}",
                None
            )
            return False
    
    async def test_authenticated_endpoint_live_domain(self):
        """Test 6: Test authenticated endpoint if login succeeded"""
        if not self.demo_token:
            self.log_result(
                "LIVE Domain Authenticated Access", 
                False, 
                "Skipped - no valid token from login test",
                None
            )
            return False
            
        try:
            url = f"{BASE_URL}/auth/me"
            headers = {'Authorization': f'Bearer {self.demo_token}'}
            
            print(f"\n🔍 Testing authenticated endpoint on LIVE domain: {url}")
            
            async with self.session.get(url, headers=headers) as response:
                status_code = response.status
                response_text = await response.text()
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        self.log_result(
                            "LIVE Domain Authenticated Access", 
                            True, 
                            f"Authenticated access working - User: {data.get('email', 'N/A')}, Credits: {data.get('credits', 'N/A')}",
                            data
                        )
                        return True
                    except json.JSONDecodeError:
                        self.log_result(
                            "LIVE Domain Authenticated Access", 
                            False, 
                            f"Invalid JSON in auth response (Status: {status_code})",
                            response_text[:200]
                        )
                        return False
                else:
                    self.log_result(
                        "LIVE Domain Authenticated Access", 
                        False, 
                        f"Authentication failed (Status: {status_code})",
                        response_text[:200]
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "LIVE Domain Authenticated Access", 
                False, 
                f"Authenticated request failed: {str(e)}",
                None
            )
            return False
    
    async def run_all_tests(self):
        """Run all production domain tests"""
        print("=" * 80)
        print("🚨 CRITICAL PRODUCTION TESTING - LIVE DOMAIN autowebiq.com")
        print("=" * 80)
        print(f"Testing URL: {BASE_URL}")
        print(f"User Report: Unable to login on autowebiq.com with manual OR Google login")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            self.test_health_check_live_domain,
            self.test_manual_login_live_domain,
            self.test_manual_registration_live_domain,
            self.test_cors_headers_live_domain,
            self.test_google_oauth_endpoint_live_domain,
            self.test_authenticated_endpoint_live_domain
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 PRODUCTION DOMAIN TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Critical analysis
        print("\n" + "=" * 80)
        print("🔍 ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        health_ok = self.test_results[0]['success'] if len(self.test_results) > 0 else False
        login_ok = self.test_results[1]['success'] if len(self.test_results) > 1 else False
        
        if not health_ok:
            print("🚨 CRITICAL ISSUE: Backend not accessible on autowebiq.com")
            print("   - The production backend is not responding to requests")
            print("   - This explains why users cannot login")
            print("   - IMMEDIATE ACTION: Check backend deployment on autowebiq.com")
        elif not login_ok:
            print("🚨 CRITICAL ISSUE: Backend accessible but authentication failing")
            print("   - Backend responds but login doesn't work")
            print("   - Demo account may not exist in production database")
            print("   - IMMEDIATE ACTION: Check production database and user accounts")
        else:
            print("✅ Backend and authentication working on production domain")
            print("   - Issue may be frontend-specific or intermittent")
        
        return success_rate >= 80  # 80% success rate threshold

async def main():
    """Main test execution"""
    async with ProductionDomainTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 PRODUCTION DOMAIN TESTS PASSED")
            sys.exit(0)
        else:
            print("\n🚨 PRODUCTION DOMAIN TESTS FAILED")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())