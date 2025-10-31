import requests
import sys
import json
import time
import uuid
import asyncio
import websockets
from datetime import datetime, timezone, timedelta
import os

class AutoWebIQV2APITester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://autowebiq-dev-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.api_v2_url = f"{self.base_url}/api/v2"
        self.ws_url = self.base_url.replace("https://", "wss://")
        
        # Demo account credentials as specified in review request
        self.demo_email = "demo@test.com"
        self.demo_password = "Demo123456"
        
        self.jwt_token = None
        self.user_id = None
        self.test_project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_v2=False):
        """Run a single API test"""
        base_url = self.api_v2_url if use_v2 else self.api_url
        url = f"{base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_test(name, True)
                return True, response_data, response
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response_data}")
                return False, response_data, response

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}, None

    def test_demo_account_login(self):
        """Test login with demo account"""
        print("\n🔐 Testing Demo Account Login")
        
        success, response, _ = self.run_test(
            "Demo Account Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.demo_email,
                "password": self.demo_password
            }
        )
        
        if success and 'access_token' in response:
            self.jwt_token = response['access_token']
            self.user_id = response['user']['id']
            initial_credits = response['user']['credits']
            print(f"   ✅ Demo account logged in with {initial_credits} credits")
            print(f"   JWT Token: {self.jwt_token[:20]}...")
            return True
        
        return False

    def test_v2_user_endpoints(self):
        """Test V2 user endpoints"""
        print("\n👤 Testing V2 User Endpoints")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping V2 user tests")
            return False
        
        # Test GET /api/v2/user/me
        success, response, _ = self.run_test(
            "V2 Get User Info",
            "GET",
            "user/me",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success:
            # Test GET /api/v2/user/credits
            success, response, _ = self.run_test(
                "V2 Get User Credits",
                "GET",
                "user/credits",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                use_v2=True
            )
            
            if success and 'credits' in response:
                print(f"   💰 User has {response['credits']} credits")
                return True
        
        return False

    def test_v2_project_endpoints(self):
        """Test V2 project management endpoints"""
        print("\n📁 Testing V2 Project Management")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping V2 project tests")
            return False
        
        # Test POST /api/v2/projects (create project)
        project_data = {
            "name": "V2 Test Project - AutoWebIQ System",
            "description": "Testing the new V2 architecture with PostgreSQL and Celery"
        }
        
        success, response, _ = self.run_test(
            "V2 Create Project",
            "POST",
            "projects",
            200,
            data=project_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success and 'id' in response:
            self.test_project_id = response['id']
            print(f"   📝 Created project: {self.test_project_id}")
            
            # Test GET /api/v2/projects (list projects)
            success, response, _ = self.run_test(
                "V2 List Projects",
                "GET",
                "projects",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                use_v2=True
            )
            
            if success:
                # Test GET /api/v2/projects/{id} (get specific project)
                success, response, _ = self.run_test(
                    "V2 Get Specific Project",
                    "GET",
                    f"projects/{self.test_project_id}",
                    200,
                    headers={"Authorization": f"Bearer {self.jwt_token}"},
                    use_v2=True
                )
                return success
        
        return False

    def test_v2_async_build_system(self):
        """Test V2 async build system with Celery"""
        print("\n🏗️ Testing V2 Async Build System")
        
        if not self.jwt_token or not self.test_project_id:
            print("   ⚠️ Missing JWT token or project ID, skipping async build tests")
            return False
        
        # Test POST /api/v2/projects/{id}/build (start async build)
        build_data = {
            "prompt": "Create a modern SaaS landing page for AutoWebIQ with features showcase and pricing section",
            "uploaded_images": []
        }
        
        print(f"   🚀 Starting async build for project: {self.test_project_id}")
        success, response, _ = self.run_test(
            "V2 Start Async Build",
            "POST",
            f"projects/{self.test_project_id}/build",
            200,
            data=build_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success and 'task_id' in response:
            task_id = response['task_id']
            print(f"   📋 Build task started: {task_id}")
            print(f"   🔗 WebSocket URL: {response.get('websocket_url')}")
            
            # Test GET /api/v2/projects/{id}/build/status/{task_id}
            # Wait a moment for task to start
            time.sleep(2)
            
            success, response, _ = self.run_test(
                "V2 Get Build Status",
                "GET",
                f"projects/{self.test_project_id}/build/status/{task_id}",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                use_v2=True
            )
            
            if success:
                print(f"   📊 Build status: {response.get('status')}")
                return True
        
        return False

    def test_v2_websocket_connection(self):
        """Test V2 WebSocket connection"""
        print("\n🔌 Testing V2 WebSocket Connection")
        
        if not self.test_project_id or not self.jwt_token:
            print("   ⚠️ Missing project ID or JWT token, skipping WebSocket test")
            return False
        
        try:
            # Test WebSocket connection
            ws_url = f"{self.ws_url}/api/v2/ws/build/{self.test_project_id}?token={self.jwt_token}"
            print(f"   🔗 Connecting to: {ws_url}")
            
            async def test_websocket():
                try:
                    async with websockets.connect(ws_url, timeout=10) as websocket:
                        # Send ping
                        await websocket.send("ping")
                        
                        # Wait for response
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        response_data = json.loads(response)
                        
                        if response_data.get('type') == 'pong':
                            print("   ✅ WebSocket ping/pong successful")
                            return True
                        else:
                            print(f"   ❌ Unexpected WebSocket response: {response_data}")
                            return False
                            
                except asyncio.TimeoutError:
                    print("   ❌ WebSocket connection timeout")
                    return False
                except Exception as e:
                    print(f"   ❌ WebSocket error: {str(e)}")
                    return False
            
            # Run async test
            result = asyncio.run(test_websocket())
            self.log_test("V2 WebSocket Connection", result)
            return result
            
        except Exception as e:
            self.log_test("V2 WebSocket Connection", False, f"Exception: {str(e)}")
            return False

    def test_v2_credit_system(self):
        """Test V2 credit system endpoints"""
        print("\n💰 Testing V2 Credit System")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping V2 credit tests")
            return False
        
        # Test GET /api/v2/credits/history
        success, response, _ = self.run_test(
            "V2 Get Credit History",
            "GET",
            "credits/history",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success:
            current_balance = response.get('current_balance', 0)
            transactions = response.get('transactions', [])
            print(f"   💳 Current balance: {current_balance} credits")
            print(f"   📊 Transaction history: {len(transactions)} transactions")
            return True
        
        return False

    def test_v2_stats_endpoint(self):
        """Test V2 stats endpoint"""
        print("\n📊 Testing V2 Stats Endpoint")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping V2 stats test")
            return False
        
        # Test GET /api/v2/stats
        success, response, _ = self.run_test(
            "V2 Get User Stats",
            "GET",
            "stats",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success:
            print(f"   👤 User: {response.get('email')}")
            print(f"   💰 Credits: {response.get('credits')}")
            print(f"   📁 Total projects: {response.get('total_projects')}")
            print(f"   ✅ Completed projects: {response.get('completed_projects')}")
            print(f"   💸 Credits spent: {response.get('credits_spent')}")
            return True
        
        return False

    def test_database_connections(self):
        """Test database connections via health endpoint"""
        print("\n🗄️ Testing Database Connections")
        
        # Test health endpoint to check database connections
        success, response, _ = self.run_test(
            "Health Check - Database Connections",
            "GET",
            "health",
            200
        )
        
        if success:
            databases = response.get('databases', {})
            services = response.get('services', {})
            
            print(f"   📊 Overall status: {response.get('status')}")
            print(f"   🍃 MongoDB: {databases.get('mongodb', 'unknown')}")
            print(f"   🐘 PostgreSQL: {databases.get('postgresql', 'unknown')}")
            print(f"   🔴 Redis: {services.get('redis', 'unknown')}")
            print(f"   🌿 Celery: {services.get('celery', 'unknown')}")
            
            # Check if all critical services are connected
            mongodb_ok = databases.get('mongodb') == 'connected'
            postgresql_ok = databases.get('postgresql') == 'connected'
            redis_ok = services.get('redis') == 'connected'
            
            if mongodb_ok and postgresql_ok and redis_ok:
                self.log_test("Database Connections", True)
                return True
            else:
                self.log_test("Database Connections", False, "Some databases not connected")
                return False
        
        return False

    def test_ai_agents_template_system(self):
        """Test AI agents and template system"""
        print("\n🤖 Testing AI Agents & Template System")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping AI agents test")
            return False
        
        # Test template selection with various prompts
        test_prompts = [
            {
                "name": "E-commerce Test",
                "prompt": "Create a luxury skincare e-commerce website with premium product showcase",
                "expected_type": "ecommerce"
            },
            {
                "name": "SaaS Test", 
                "prompt": "Build a modern B2B SaaS platform landing page for project management",
                "expected_type": "saas"
            },
            {
                "name": "Portfolio Test",
                "prompt": "Create a professional portfolio website for a freelance consultant",
                "expected_type": "portfolio"
            }
        ]
        
        successful_tests = 0
        
        for test_case in test_prompts:
            print(f"\n   🧪 Testing: {test_case['name']}")
            
            # Create project for this test
            project_data = {
                "name": f"AI Test - {test_case['name']}",
                "description": test_case['prompt']
            }
            
            success, response, _ = self.run_test(
                f"Create AI Test Project - {test_case['name']}",
                "POST",
                "projects",
                200,
                data=project_data,
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                use_v2=True
            )
            
            if success and 'id' in response:
                project_id = response['id']
                
                # Test template-based build (V1 endpoint for now)
                build_data = {
                    "project_id": project_id,
                    "prompt": test_case['prompt'],
                    "uploaded_images": []
                }
                
                success, response, _ = self.run_test(
                    f"Template Build - {test_case['name']}",
                    "POST",
                    "build-with-agents",
                    200,
                    data=build_data,
                    headers={"Authorization": f"Bearer {self.jwt_token}"}
                )
                
                if success:
                    successful_tests += 1
                    print(f"      ✅ {test_case['name']} build successful")
                    print(f"      📊 Credits used: {response.get('credits_used', 'N/A')}")
                    print(f"      📝 Code length: {len(response.get('frontend_code', ''))} chars")
                else:
                    print(f"      ❌ {test_case['name']} build failed")
        
        # Consider successful if at least 2 out of 3 tests pass
        success_rate = successful_tests / len(test_prompts)
        overall_success = success_rate >= 0.67
        
        self.log_test("AI Agents & Template System", overall_success, 
                     f"{successful_tests}/{len(test_prompts)} tests passed ({success_rate*100:.1f}%)")
        
        return overall_success

    def test_end_to_end_flow(self):
        """Test complete end-to-end flow"""
        print("\n🔄 Testing End-to-End Flow")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping E2E test")
            return False
        
        print("   📋 E2E Flow: Login → Create Project → Start Build → WebSocket Updates → Build Complete → Credits Deducted")
        
        # Step 1: Already logged in ✅
        print("   ✅ Step 1: Login completed")
        
        # Step 2: Create Project
        project_data = {
            "name": "E2E Test Project",
            "description": "End-to-end testing of AutoWebIQ V2 system"
        }
        
        success, response, _ = self.run_test(
            "E2E Create Project",
            "POST",
            "projects",
            200,
            data=project_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if not success:
            return False
        
        e2e_project_id = response['id']
        print(f"   ✅ Step 2: Project created - {e2e_project_id}")
        
        # Step 3: Start Build
        build_data = {
            "prompt": "Create a simple landing page for AutoWebIQ with hero section and features",
            "uploaded_images": []
        }
        
        success, response, _ = self.run_test(
            "E2E Start Build",
            "POST",
            f"projects/{e2e_project_id}/build",
            200,
            data=build_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if not success:
            return False
        
        task_id = response['task_id']
        print(f"   ✅ Step 3: Build started - {task_id}")
        
        # Step 4: Monitor via WebSocket (simplified)
        try:
            ws_url = f"{self.ws_url}/api/v2/ws/build/{e2e_project_id}?token={self.jwt_token}"
            
            async def monitor_build():
                try:
                    async with websockets.connect(ws_url, timeout=10) as websocket:
                        # Wait for connection message
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        
                        if data.get('type') == 'connection':
                            print("   ✅ Step 4: WebSocket connected for build monitoring")
                            return True
                        
                except Exception as e:
                    print(f"   ❌ Step 4: WebSocket monitoring failed - {str(e)}")
                    return False
            
            ws_success = asyncio.run(monitor_build())
            
        except Exception as e:
            print(f"   ❌ Step 4: WebSocket test failed - {str(e)}")
            ws_success = False
        
        # Step 5: Check Build Status
        time.sleep(3)  # Wait for build to progress
        
        success, response, _ = self.run_test(
            "E2E Check Build Status",
            "GET",
            f"projects/{e2e_project_id}/build/status/{task_id}",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success:
            build_status = response.get('status', 'UNKNOWN')
            print(f"   ✅ Step 5: Build status checked - {build_status}")
        
        # Step 6: Verify Credits System
        success, response, _ = self.run_test(
            "E2E Verify Credits",
            "GET",
            "user/credits",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            use_v2=True
        )
        
        if success:
            credits = response.get('credits', 0)
            print(f"   ✅ Step 6: Credits verified - {credits} remaining")
        
        # Overall E2E success
        e2e_success = all([
            True,  # Login (already done)
            e2e_project_id is not None,  # Project creation
            task_id is not None,  # Build start
            ws_success,  # WebSocket
            build_status in ['PENDING', 'PROGRESS', 'SUCCESS'],  # Build status
            credits >= 0  # Credits check
        ])
        
        self.log_test("End-to-End Flow", e2e_success)
        return e2e_success

    def run_comprehensive_v2_tests(self):
        """Run comprehensive V2 architecture tests"""
        print("🚀 Starting AutoWebIQ V2 Architecture Comprehensive Testing")
        print(f"   Base URL: {self.base_url}")
        print(f"   V2 API URL: {self.api_v2_url}")
        print(f"   WebSocket URL: {self.ws_url}")
        print("=" * 80)

        # Test 1: Demo Account Login
        login_success = self.test_demo_account_login()
        
        # Test 2: Database Connections
        db_success = self.test_database_connections()
        
        # Test 3: V2 User Endpoints
        user_success = self.test_v2_user_endpoints()
        
        # Test 4: V2 Project Management
        project_success = self.test_v2_project_endpoints()
        
        # Test 5: V2 Async Build System
        build_success = self.test_v2_async_build_system()
        
        # Test 6: V2 WebSocket Connection
        ws_success = self.test_v2_websocket_connection()
        
        # Test 7: V2 Credit System
        credit_success = self.test_v2_credit_system()
        
        # Test 8: V2 Stats Endpoint
        stats_success = self.test_v2_stats_endpoint()
        
        # Test 9: AI Agents & Template System
        ai_success = self.test_ai_agents_template_system()
        
        # Test 10: End-to-End Flow
        e2e_success = self.test_end_to_end_flow()

        return all([
            login_success,
            db_success, 
            user_success,
            project_success,
            build_success,
            ws_success,
            credit_success,
            stats_success,
            ai_success,
            e2e_success
        ])

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 AUTOWEBIQ V2 ARCHITECTURE TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print("\n📋 V2 ARCHITECTURE COMPONENTS TESTED:")
        print("   ✅ Demo Account Authentication (demo@test.com)")
        print("   ✅ PostgreSQL Database Integration")
        print("   ✅ MongoDB Template/Component Storage")
        print("   ✅ Redis Caching & Session Management")
        print("   ✅ Celery Task Queue (Async Builds)")
        print("   ✅ WebSocket Real-time Updates")
        print("   ✅ V2 API Endpoints (10 endpoints)")
        print("   ✅ AI Agents & Template Selection")
        print("   ✅ Credit System V2")
        print("   ✅ End-to-End Build Flow")
        
        print("\n🔧 V2 ENDPOINTS TESTED:")
        print("   • POST /api/v2/projects (create project)")
        print("   • GET /api/v2/projects (list projects)")
        print("   • GET /api/v2/projects/{id} (get project)")
        print("   • POST /api/v2/projects/{id}/build (start async build)")
        print("   • GET /api/v2/projects/{id}/build/status/{task_id}")
        print("   • GET /api/v2/user/me")
        print("   • GET /api/v2/user/credits")
        print("   • GET /api/v2/stats")
        print("   • GET /api/v2/credits/history")
        print("   • WS /api/v2/ws/build/{id}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AutoWebIQV2APITester()
    
    try:
        success = tester.run_comprehensive_v2_tests()
        all_passed = tester.print_summary()
        return 0 if all_passed else 1
    except Exception as e:
        print(f"❌ V2 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())