#!/usr/bin/env python3
"""
AutoWebIQ 2.0 Backend Testing - NEW Endpoints Focus
Testing Priority: HIGH - Subscription & Deployment Endpoints

Test Approach:
1. Health check first
2. Test subscription plans (no auth needed)
3. Use demo account for authenticated endpoints
4. Test subscription status
5. Test deployment listing

Backend URL: https://multiagent-web.preview.emergentagent.com/api
Demo Account: demo@test.com / Demo123456
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://multiagent-web.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_health_check(self):
        """Test 1: Health Check - Verify backend is running"""
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Backend healthy, status: {status}",
                    data
                )
                return True
            else:
                self.log_test(
                    "Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def authenticate_demo_user(self):
        """Authenticate with demo account to get auth token"""
        try:
            login_data = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login", 
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                user_info = data.get('user', {})
                credits = user_info.get('credits', 0)
                
                self.log_test(
                    "Demo Account Authentication", 
                    True, 
                    f"Login successful, credits: {credits}",
                    {"user_id": user_info.get('id'), "credits": credits}
                )
                
                # Set auth header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                return True
            else:
                self.log_test(
                    "Demo Account Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Demo Account Authentication", False, f"Error: {str(e)}")
            return False

    def test_subscription_plans(self):
        """Test 2: NEW - Subscription Plans (No auth needed)"""
        try:
            response = self.session.get(f"{BASE_URL}/subscriptions/plans", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                plans = data.get('plans', [])
                
                # Verify we have 4 plans as expected
                expected_plans = ['Free', 'Starter', 'Pro', 'Enterprise']
                plan_names = [plan.get('name', '') for plan in plans]
                
                if len(plans) == 4:
                    self.log_test(
                        "Subscription Plans - Count", 
                        True, 
                        f"Found {len(plans)} plans: {', '.join(plan_names)}",
                        {"plans_count": len(plans), "plan_names": plan_names}
                    )
                else:
                    self.log_test(
                        "Subscription Plans - Count", 
                        False, 
                        f"Expected 4 plans, got {len(plans)}: {', '.join(plan_names)}"
                    )
                
                # Verify plan structure
                for plan in plans:
                    plan_name = plan.get('name', 'Unknown')
                    has_required_fields = all(key in plan for key in ['id', 'name', 'price', 'credits'])
                    
                    if has_required_fields:
                        self.log_test(
                            f"Subscription Plan Structure - {plan_name}", 
                            True, 
                            f"Plan has all required fields: id, name, price, credits",
                            plan
                        )
                    else:
                        missing_fields = [key for key in ['id', 'name', 'price', 'credits'] if key not in plan]
                        self.log_test(
                            f"Subscription Plan Structure - {plan_name}", 
                            False, 
                            f"Missing fields: {', '.join(missing_fields)}"
                        )
                
                return True
            else:
                self.log_test(
                    "Subscription Plans", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Subscription Plans", False, f"Error: {str(e)}")
            return False

    def test_subscription_status(self):
        """Test 3: NEW - Subscription Status (Needs auth)"""
        if not self.auth_token:
            self.log_test("Subscription Status", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/subscriptions/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                subscription = data.get('subscription', {})
                status = subscription.get('status', 'unknown')
                plan_id = subscription.get('plan_id', 'unknown')
                
                self.log_test(
                    "Subscription Status", 
                    True, 
                    f"Status: {status}, Plan: {plan_id}",
                    subscription
                )
                return True
            elif response.status_code == 401:
                self.log_test(
                    "Subscription Status", 
                    False, 
                    "Authentication failed - token may be invalid"
                )
                return False
            else:
                self.log_test(
                    "Subscription Status", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Subscription Status", False, f"Error: {str(e)}")
            return False

    def test_deployments_list(self):
        """Test 4: NEW - Deployment Endpoints (Needs auth)"""
        if not self.auth_token:
            self.log_test("Deployments List", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/deployments", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                deployments = data.get('deployments', [])
                count = data.get('count', 0)
                
                self.log_test(
                    "Deployments List", 
                    True, 
                    f"Found {count} deployments",
                    {"count": count, "deployments_sample": deployments[:2] if deployments else []}
                )
                return True
            elif response.status_code == 401:
                self.log_test(
                    "Deployments List", 
                    False, 
                    "Authentication failed - token may be invalid"
                )
                return False
            else:
                self.log_test(
                    "Deployments List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Deployments List", False, f"Error: {str(e)}")
            return False

    def test_error_handling(self):
        """Test 5: Error Handling - Test endpoints without auth where required"""
        try:
            # Test subscription status without auth
            temp_session = requests.Session()  # No auth headers
            response = temp_session.get(f"{BASE_URL}/subscriptions/status", timeout=10)
            
            if response.status_code == 401:
                self.log_test(
                    "Error Handling - Subscription Status (No Auth)", 
                    True, 
                    "Correctly returns 401 for unauthenticated request"
                )
            else:
                self.log_test(
                    "Error Handling - Subscription Status (No Auth)", 
                    False, 
                    f"Expected 401, got {response.status_code}"
                )
            
            # Test deployments without auth
            response = temp_session.get(f"{BASE_URL}/deployments", timeout=10)
            
            if response.status_code == 401:
                self.log_test(
                    "Error Handling - Deployments (No Auth)", 
                    True, 
                    "Correctly returns 401 for unauthenticated request"
                )
            else:
                self.log_test(
                    "Error Handling - Deployments (No Auth)", 
                    False, 
                    f"Expected 401, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 AutoWebIQ 2.0 Backend Testing - NEW Endpoints Focus")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Demo Account: {DEMO_EMAIL}")
        print("=" * 60)
        print()
        
        # Test 1: Health Check (Critical)
        health_ok = self.test_health_check()
        if not health_ok:
            print("❌ CRITICAL: Backend health check failed. Stopping tests.")
            return self.generate_summary()
        
        # Test 2: Subscription Plans (No auth needed)
        self.test_subscription_plans()
        
        # Test 3: Authentication
        auth_ok = self.authenticate_demo_user()
        
        if auth_ok:
            # Test 4: Subscription Status (Needs auth)
            self.test_subscription_status()
            
            # Test 5: Deployments List (Needs auth)
            self.test_deployments_list()
        else:
            print("⚠️ Authentication failed - skipping authenticated endpoint tests")
        
        # Test 6: Error Handling
        self.test_error_handling()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by status
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: All critical endpoints working correctly!")
        elif success_rate >= 75:
            print("✅ GOOD: Most endpoints working, minor issues detected")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some critical issues need attention")
        else:
            print("❌ CRITICAL: Major issues detected, immediate attention required")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "failed_tests": failed_tests,
            "passed_tests": passed_tests,
            "overall_status": "PASS" if success_rate >= 75 else "FAIL"
        }

def main():
    """Main test execution"""
    tester = BackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["overall_status"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()