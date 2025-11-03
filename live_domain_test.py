#!/usr/bin/env python3
"""
CRITICAL LIVE DOMAIN DIAGNOSTIC - autowebiq.com
Testing authentication flow on production domain as reported by user
"""

import asyncio
import aiohttp
import json
import ssl
import socket
from datetime import datetime
import sys

# Production domain configuration
DOMAIN = "autowebiq.com"
API_DOMAIN = "api.autowebiq.com"
BASE_URL = f"https://{API_DOMAIN}/api"

# Test credentials
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class LiveDomainTester:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def log_result(self, test_name, success, details, error=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
    
    async def test_dns_resolution(self):
        """Test DNS resolution for api.autowebiq.com"""
        try:
            # Test DNS resolution
            ip_address = socket.gethostbyname(API_DOMAIN)
            await self.log_result(
                "DNS Resolution", 
                True, 
                f"api.autowebiq.com resolves to {ip_address}"
            )
            return True
        except Exception as e:
            await self.log_result(
                "DNS Resolution", 
                False, 
                "Failed to resolve api.autowebiq.com", 
                e
            )
            return False
    
    async def test_ssl_certificate(self):
        """Test SSL certificate validity"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Test SSL connection
            with socket.create_connection((API_DOMAIN, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=API_DOMAIN) as ssock:
                    cert = ssock.getpeercert()
                    
            await self.log_result(
                "SSL Certificate", 
                True, 
                f"Valid SSL certificate for {API_DOMAIN}"
            )
            return True
        except Exception as e:
            await self.log_result(
                "SSL Certificate", 
                False, 
                "SSL certificate validation failed", 
                e
            )
            return False
    
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                data = await response.json()
                
                if response.status == 200:
                    await self.log_result(
                        "Health Check", 
                        True, 
                        f"Health endpoint accessible, status: {data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    await self.log_result(
                        "Health Check", 
                        False, 
                        f"Health endpoint returned {response.status}"
                    )
                    return False
        except Exception as e:
            await self.log_result(
                "Health Check", 
                False, 
                "Health endpoint not accessible", 
                e
            )
            return False
    
    async def test_cors_headers(self):
        """Test CORS headers for autowebiq.com origin"""
        try:
            headers = {
                "Origin": f"https://{DOMAIN}",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            async with self.session.options(f"{BASE_URL}/auth/login", headers=headers) as response:
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                cors_methods = response.headers.get('Access-Control-Allow-Methods')
                cors_headers = response.headers.get('Access-Control-Allow-Headers')
                
                if cors_origin and (cors_origin == '*' or DOMAIN in cors_origin):
                    await self.log_result(
                        "CORS Headers", 
                        True, 
                        f"CORS properly configured. Origin: {cors_origin}"
                    )
                    return True
                else:
                    await self.log_result(
                        "CORS Headers", 
                        False, 
                        f"CORS may be misconfigured. Origin header: {cors_origin}"
                    )
                    return False
        except Exception as e:
            await self.log_result(
                "CORS Headers", 
                False, 
                "Failed to test CORS headers", 
                e
            )
            return False
    
    async def test_demo_login(self):
        """Test demo account login"""
        try:
            login_data = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            async with self.session.post(
                f"{BASE_URL}/auth/login", 
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get('access_token'):
                            await self.log_result(
                                "Demo Login", 
                                True, 
                                f"Demo login successful, token received, credits: {data.get('user', {}).get('credits', 'unknown')}"
                            )
                            return data.get('access_token')
                        else:
                            await self.log_result(
                                "Demo Login", 
                                False, 
                                "Login response missing access_token"
                            )
                            return None
                    except json.JSONDecodeError:
                        await self.log_result(
                            "Demo Login", 
                            False, 
                            f"Invalid JSON response: {response_text[:200]}"
                        )
                        return None
                else:
                    await self.log_result(
                        "Demo Login", 
                        False, 
                        f"Login failed with status {response.status}: {response_text[:200]}"
                    )
                    return None
        except Exception as e:
            await self.log_result(
                "Demo Login", 
                False, 
                "Login request failed", 
                e
            )
            return None
    
    async def test_registration(self):
        """Test user registration"""
        try:
            # Generate unique test user
            timestamp = int(datetime.now().timestamp())
            test_email = f"test{timestamp}@test.com"
            
            register_data = {
                "username": f"testuser{timestamp}",
                "email": test_email,
                "password": "Test123456"
            }
            
            async with self.session.post(
                f"{BASE_URL}/auth/register", 
                json=register_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get('access_token'):
                            await self.log_result(
                                "User Registration", 
                                True, 
                                f"Registration successful for {test_email}, credits: {data.get('user', {}).get('credits', 'unknown')}"
                            )
                            return True
                        else:
                            await self.log_result(
                                "User Registration", 
                                False, 
                                "Registration response missing access_token"
                            )
                            return False
                    except json.JSONDecodeError:
                        await self.log_result(
                            "User Registration", 
                            False, 
                            f"Invalid JSON response: {response_text[:200]}"
                        )
                        return False
                else:
                    await self.log_result(
                        "User Registration", 
                        False, 
                        f"Registration failed with status {response.status}: {response_text[:200]}"
                    )
                    return False
        except Exception as e:
            await self.log_result(
                "User Registration", 
                False, 
                "Registration request failed", 
                e
            )
            return False
    
    async def test_authenticated_endpoint(self, token):
        """Test authenticated endpoint with token"""
        if not token:
            await self.log_result(
                "Authenticated Endpoint", 
                False, 
                "No token available for testing"
            )
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        await self.log_result(
                            "Authenticated Endpoint", 
                            True, 
                            f"Auth verification successful for user: {data.get('email', 'unknown')}"
                        )
                        return True
                    except json.JSONDecodeError:
                        await self.log_result(
                            "Authenticated Endpoint", 
                            False, 
                            f"Invalid JSON response: {response_text[:200]}"
                        )
                        return False
                else:
                    await self.log_result(
                        "Authenticated Endpoint", 
                        False, 
                        f"Auth verification failed with status {response.status}: {response_text[:200]}"
                    )
                    return False
        except Exception as e:
            await self.log_result(
                "Authenticated Endpoint", 
                False, 
                "Auth verification request failed", 
                e
            )
            return False
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print(f"🚨 CRITICAL LIVE DOMAIN DIAGNOSTIC - {DOMAIN}")
        print(f"Testing API endpoint: {BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Create aiohttp session with proper SSL context
        connector = aiohttp.TCPConnector(ssl=False)  # Allow testing SSL issues
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            
            # Test 1: DNS Resolution
            dns_ok = await self.test_dns_resolution()
            
            # Test 2: SSL Certificate
            ssl_ok = await self.test_ssl_certificate()
            
            # Test 3: Health Check
            health_ok = await self.test_health_endpoint()
            
            # Test 4: CORS Headers
            cors_ok = await self.test_cors_headers()
            
            # Test 5: Demo Login (CRITICAL)
            token = await self.test_demo_login()
            
            # Test 6: User Registration
            register_ok = await self.test_registration()
            
            # Test 7: Authenticated Endpoint
            auth_ok = await self.test_authenticated_endpoint(token)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical issues
        critical_failures = []
        for result in self.results:
            if not result['success'] and result['test'] in ['DNS Resolution', 'Health Check', 'Demo Login']:
                critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['error']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not dns_ok:
            print("   • Check DNS configuration for api.autowebiq.com")
        if not ssl_ok:
            print("   • Verify SSL certificate installation")
        if not health_ok:
            print("   • Check backend server status and deployment")
        if not cors_ok:
            print("   • Review CORS configuration for autowebiq.com origin")
        if not token:
            print("   • CRITICAL: Login endpoint not working - investigate authentication system")
        
        # Final assessment
        if success_rate >= 85 and token:
            print(f"\n✅ ASSESSMENT: Authentication system is WORKING")
        else:
            print(f"\n❌ ASSESSMENT: Authentication system has CRITICAL ISSUES")
        
        return success_rate >= 85 and token is not None

async def main():
    """Main test execution"""
    tester = LiveDomainTester()
    success = await tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())