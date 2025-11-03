#!/usr/bin/env python3
"""
AutoWebIQ Production Verification Test
Quick production verification test for AutoWebIQ on autowebiq.com domain

Test Configuration:
- Backend URL: http://localhost:8001
- Host header: api.autowebiq.com
- Demo account: demo@test.com / Demo123456
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

class ProductionVerificationTest:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.host_header = "api.autowebiq.com"
        self.demo_email = "demo@test.com"
        self.demo_password = "Demo123456"
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    async def make_request(self, method, endpoint, headers=None, data=None, auth=True):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        request_headers = {
            "Host": self.host_header,
            "Content-Type": "application/json",
            "User-Agent": "AutoWebIQ-ProductionTest/1.0"
        }
        
        # Add auth header if needed and available
        if auth and self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
        # Merge with provided headers
        if headers:
            request_headers.update(headers)
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, 
                    url, 
                    headers=request_headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "raw_text": response_text
                    }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "data": {}
            }

    async def test_health_check(self):
        """Test 1: Health Check - GET /api/health"""
        print("🔍 Testing Health Check...")
        
        response = await self.make_request("GET", "/api/health", auth=False)
        
        if response["status"] == 200:
            data = response["data"]
            if data.get("status") == "healthy":
                self.log_result(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, MongoDB: {data.get('mongodb', 'unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"Unexpected status: {data.get('status')}"
                )
                return False
        else:
            self.log_result(
                "Health Check", 
                False, 
                error=f"HTTP {response['status']}: {response.get('error', 'Unknown error')}"
            )
            return False

    async def test_subscription_plans(self):
        """Test 2: Subscription Plans - GET /api/subscriptions/plans"""
        print("🔍 Testing Subscription Plans...")
        
        response = await self.make_request("GET", "/api/subscriptions/plans", auth=False)
        
        if response["status"] == 200:
            data = response["data"]
            plans = data.get("plans", [])
            
            if len(plans) == 4:
                plan_names = [plan.get("name", "") for plan in plans]
                expected_plans = ["Free", "Starter", "Pro", "Enterprise"]
                
                if all(name in plan_names for name in expected_plans):
                    self.log_result(
                        "Subscription Plans", 
                        True, 
                        f"Found all 4 plans: {', '.join(plan_names)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Subscription Plans", 
                        False, 
                        f"Plan names mismatch. Found: {plan_names}, Expected: {expected_plans}"
                    )
                    return False
            else:
                self.log_result(
                    "Subscription Plans", 
                    False, 
                    f"Expected 4 plans, found {len(plans)}"
                )
                return False
        else:
            self.log_result(
                "Subscription Plans", 
                False, 
                error=f"HTTP {response['status']}: {response.get('error', 'Unknown error')}"
            )
            return False

    async def test_demo_login(self):
        """Test 3: Demo Account Login"""
        print("🔍 Testing Demo Account Login...")
        
        login_data = {
            "email": self.demo_email,
            "password": self.demo_password
        }
        
        response = await self.make_request("POST", "/api/auth/login", data=login_data, auth=False)
        
        if response["status"] == 200:
            data = response["data"]
            access_token = data.get("access_token")
            user_data = data.get("user", {})
            
            if access_token and user_data.get("email") == self.demo_email:
                self.auth_token = access_token
                credits = user_data.get("credits", 0)
                self.log_result(
                    "Demo Account Login", 
                    True, 
                    f"Login successful, Credits: {credits}, User ID: {user_data.get('id', 'unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Demo Account Login", 
                    False, 
                    "Missing access token or user data"
                )
                return False
        else:
            self.log_result(
                "Demo Account Login", 
                False, 
                error=f"HTTP {response['status']}: {response.get('error', 'Login failed')}"
            )
            return False

    async def test_projects_list(self):
        """Test 4: Projects List - GET /api/projects (with auth)"""
        print("🔍 Testing Projects List...")
        
        if not self.auth_token:
            self.log_result(
                "Projects List", 
                False, 
                error="No auth token available (login failed)"
            )
            return False
        
        response = await self.make_request("GET", "/api/projects", auth=True)
        
        if response["status"] == 200:
            data = response["data"]
            projects = data.get("projects", [])
            
            self.log_result(
                "Projects List", 
                True, 
                f"Retrieved {len(projects)} projects successfully"
            )
            return True
        elif response["status"] == 401:
            self.log_result(
                "Projects List", 
                False, 
                error="Authentication failed - invalid token"
            )
            return False
        else:
            self.log_result(
                "Projects List", 
                False, 
                error=f"HTTP {response['status']}: {response.get('error', 'Unknown error')}"
            )
            return False

    async def run_all_tests(self):
        """Run all production verification tests"""
        print("🚀 AutoWebIQ Production Verification Test")
        print("=" * 50)
        print(f"Backend URL: {self.base_url}")
        print(f"Host Header: {self.host_header}")
        print(f"Demo Account: {self.demo_email}")
        print("=" * 50)
        print()
        
        # Run tests in sequence
        test_functions = [
            self.test_health_check,
            self.test_subscription_plans,
            self.test_demo_login,
            self.test_projects_list
        ]
        
        passed = 0
        total = len(test_functions)
        
        for test_func in test_functions:
            try:
                success = await test_func()
                if success:
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test_func.__name__}")
                print(f"    Exception: {str(e)}")
                print()
        
        # Summary
        print("=" * 50)
        print("📊 PRODUCTION VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - PRODUCTION READY")
            print("✅ AutoWebIQ is ready for production deployment")
        else:
            print("⚠️  SOME TESTS FAILED - NEEDS ATTENTION")
            print("❌ Production deployment not recommended")
        
        print("=" * 50)
        
        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        return passed == total

async def main():
    """Main test execution"""
    tester = ProductionVerificationTest()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())