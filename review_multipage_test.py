import requests
import sys
import json
import time
import uuid
import websocket
import threading
from datetime import datetime, timezone, timedelta
import os

class AutoWebIQMultiPageTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://aiweb-builder-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.ws_url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        self.jwt_token = None
        self.user_id = None
        self.test_project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.ws_messages = []
        self.ws_connected = False

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=timeout)

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

    def test_health_check(self):
        """Test 1: Health Check"""
        print("\n🏥 Testing Health Check")
        
        success, response, _ = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            print(f"   Status: {response.get('status', 'unknown')}")
            print(f"   Databases: {response.get('databases', {})}")
            print(f"   Services: {response.get('services', {})}")
            return True
        
        return False

    def test_demo_account_auth(self):
        """Test 2: Demo Account Authentication"""
        print("\n🔐 Testing Demo Account Authentication")
        
        # Test demo account login as specified in review
        demo_email = "demo@test.com"
        demo_password = "Demo123456"
        
        success, response, _ = self.run_test(
            "Demo Account Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": demo_email,
                "password": demo_password
            }
        )
        
        if success and 'access_token' in response:
            self.jwt_token = response['access_token']
            self.user_id = response['user']['id']
            initial_credits = response['user']['credits']
            
            print(f"   ✅ Demo account logged in")
            print(f"   User ID: {self.user_id}")
            print(f"   Credits: {initial_credits}")
            
            # Verify demo account has sufficient credits (should have 1000 as per review)
            if initial_credits >= 100:  # At least 100 credits needed for testing
                self.log_test("Demo Account Credits Check", True, f"Has {initial_credits} credits")
            else:
                self.log_test("Demo Account Credits Check", False, f"Only has {initial_credits} credits, need at least 100")
            
            # Test JWT token with /auth/me - try both V1 and V2 endpoints
            success, response, _ = self.run_test(
                "Verify JWT Token (V1)",
                "GET",
                "auth/me",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            # If V1 fails, try V2
            if not success:
                success, response, _ = self.run_test(
                    "Verify JWT Token (V2)",
                    "GET",
                    "v2/user/me",
                    200,
                    headers={"Authorization": f"Bearer {self.jwt_token}"}
                )
            
            return success
        
        return False

    def test_project_creation(self):
        """Test 3: Project Creation"""
        print("\n📁 Testing Project Creation")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available, skipping project creation")
            return False
        
        # Create project for hotel website as specified in review
        project_data = {
            "name": "Test Hotel Website",
            "description": "create a hotel booking website with rooms, reservations, login and contact features",
            "model": "claude-4.5-sonnet-200k"
        }
        
        success, response, _ = self.run_test(
            "Create Hotel Website Project",
            "POST",
            "projects/create",
            200,
            data=project_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success and 'id' in response:
            self.test_project_id = response['id']
            print(f"   ✅ Project created with ID: {self.test_project_id}")
            return True
        
        return False

    def on_ws_message(self, ws, message):
        """WebSocket message handler"""
        try:
            data = json.loads(message)
            self.ws_messages.append(data)
            
            # Look for agent status messages
            if 'type' in data and data['type'] == 'agent_status':
                agent = data.get('agent', 'unknown')
                status = data.get('status', 'unknown')
                print(f"   🤖 {agent}: {status}")
            elif 'type' in data and data['type'] == 'build_progress':
                progress = data.get('progress', {})
                print(f"   📊 Progress: {progress}")
            elif 'type' in data and data['type'] == 'build_complete':
                print(f"   ✅ Build completed via WebSocket")
        except:
            pass

    def on_ws_error(self, ws, error):
        """WebSocket error handler"""
        print(f"   ❌ WebSocket error: {error}")

    def on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket close handler"""
        print(f"   🔌 WebSocket closed")
        self.ws_connected = False

    def on_ws_open(self, ws):
        """WebSocket open handler"""
        print(f"   ✅ WebSocket connected")
        self.ws_connected = True

    def test_websocket_connection(self):
        """Test 4: WebSocket Connection Test"""
        print("\n🔌 Testing WebSocket Connection")
        
        if not self.test_project_id:
            print("   ⚠️ No project ID available, skipping WebSocket test")
            return False
        
        try:
            # Create WebSocket connection for build updates
            ws_url = f"{self.ws_url}/ws/build/{self.test_project_id}"
            print(f"   Connecting to: {ws_url}")
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_ws_message,
                on_error=self.on_ws_error,
                on_close=self.on_ws_close,
                on_open=self.on_ws_open
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection
            time.sleep(2)
            
            if self.ws_connected:
                self.log_test("WebSocket Connection", True)
                # Keep connection for build test
                return True, ws
            else:
                self.log_test("WebSocket Connection", False, "Failed to establish connection")
                return False, None
                
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Exception: {str(e)}")
            return False, None

    def test_multi_page_website_generation(self):
        """Test 5: Multi-Page Website Generation (CORE TEST)"""
        print("\n🎯 Testing Multi-Page Website Generation (CORE TEST)")
        print("   This is the main feature being tested as per review request")
        
        if not self.jwt_token or not self.test_project_id:
            print("   ⚠️ Missing JWT token or project ID")
            return False
        
        # Test WebSocket connection first
        ws_success, ws = self.test_websocket_connection()
        
        # Build request as specified in review
        build_data = {
            "project_id": self.test_project_id,
            "prompt": "create a hotel booking website with rooms, reservations, login and contact features",
            "uploaded_images": []
        }
        
        print(f"\n   🚀 Starting multi-page website generation...")
        print(f"   Prompt: {build_data['prompt']}")
        
        # Clear previous WebSocket messages
        self.ws_messages = []
        
        build_start_time = time.time()
        
        success, response, _ = self.run_test(
            "Multi-Page Website Build",
            "POST",
            "build-with-agents",
            200,
            data=build_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            timeout=120  # 2 minutes timeout for build
        )
        
        build_end_time = time.time()
        build_duration = build_end_time - build_start_time
        
        if success:
            print(f"   ✅ Build completed in {build_duration:.1f}s")
            
            # Analyze build response
            frontend_code = response.get('frontend_code', '')
            credits_used = response.get('credits_used', 0)
            cost_breakdown = response.get('cost_breakdown', {})
            
            print(f"   💰 Credits used: {credits_used}")
            print(f"   📊 Cost breakdown: {cost_breakdown}")
            print(f"   📝 Generated HTML length: {len(frontend_code)} characters")
            
            # Check for agent workflow messages in WebSocket
            agent_messages = [msg for msg in self.ws_messages if msg.get('type') == 'agent_status']
            
            # Expected agent workflow as per review request
            expected_agents = [
                "🚀 Initializing Agent",
                "🤔 Planner Agent", 
                "🖼️ Image Agent",
                "🎨 Frontend Agent",
                "🧪 Testing Agent"
            ]
            
            agents_detected = []
            for msg in agent_messages:
                agent_name = msg.get('agent', '')
                status = msg.get('status', '')
                if any(expected in agent_name for expected in expected_agents):
                    agents_detected.append(f"{agent_name}: {status}")
            
            print(f"   🤖 Agent workflow detected: {len(agents_detected)} messages")
            for agent_msg in agents_detected[:5]:  # Show first 5
                print(f"      • {agent_msg}")
            
            # Verify agent workflow
            if len(agents_detected) >= 3:
                self.log_test("Agent Workflow Detection", True, f"Detected {len(agents_detected)} agent messages")
            else:
                self.log_test("Agent Workflow Detection", False, f"Only detected {len(agents_detected)} agent messages")
            
            # Test multi-page generation validation
            self.test_generated_website_validation(frontend_code)
            
            # Test credit deduction
            self.test_credit_deduction(credits_used)
            
            return True
        else:
            print(f"   ❌ Build failed after {build_duration:.1f}s")
            print(f"   Error: {response.get('detail', 'Unknown error')}")
            return False

    def test_generated_website_validation(self, html_content):
        """Test 6: Generated Website Validation"""
        print("\n🔍 Testing Generated Website Validation")
        
        if not html_content:
            self.log_test("Website Validation", False, "No HTML content generated")
            return False
        
        # Check for multi-page structure
        pages_found = []
        
        # Look for multiple HTML pages or sections
        if "rooms" in html_content.lower():
            pages_found.append("rooms")
        if "booking" in html_content.lower() or "reservation" in html_content.lower():
            pages_found.append("booking/reservations")
        if "contact" in html_content.lower():
            pages_found.append("contact")
        if "login" in html_content.lower():
            pages_found.append("login")
        if "signup" in html_content.lower() or "register" in html_content.lower():
            pages_found.append("signup")
        if "home" in html_content.lower() or "index" in html_content.lower():
            pages_found.append("home")
        
        print(f"   📄 Pages/Sections found: {pages_found}")
        
        # Verify multi-page generation
        if len(pages_found) >= 4:
            self.log_test("Multi-Page Generation", True, f"Found {len(pages_found)} pages: {pages_found}")
        else:
            self.log_test("Multi-Page Generation", False, f"Only found {len(pages_found)} pages: {pages_found}")
        
        # Check for working navigation links
        nav_links = html_content.count('<a href=')
        if nav_links >= 3:
            self.log_test("Navigation Links", True, f"Found {nav_links} navigation links")
        else:
            self.log_test("Navigation Links", False, f"Only found {nav_links} navigation links")
        
        # Check for functional forms
        forms_found = []
        if '<form' in html_content:
            if 'contact' in html_content.lower() and '<form' in html_content:
                forms_found.append("contact form")
            if 'login' in html_content.lower() and '<form' in html_content:
                forms_found.append("login form")
            if 'signup' in html_content.lower() or 'register' in html_content.lower():
                forms_found.append("signup form")
            if 'booking' in html_content.lower() or 'reservation' in html_content.lower():
                forms_found.append("booking form")
        
        print(f"   📝 Forms found: {forms_found}")
        
        if len(forms_found) >= 2:
            self.log_test("Functional Forms", True, f"Found {len(forms_found)} forms: {forms_found}")
        else:
            self.log_test("Functional Forms", False, f"Only found {len(forms_found)} forms: {forms_found}")
        
        # Check for form validation (onsubmit handlers or validation attributes)
        has_validation = False
        if 'onsubmit' in html_content or 'required' in html_content or 'pattern=' in html_content:
            has_validation = True
        
        if has_validation:
            self.log_test("Form Validation", True, "Found form validation elements")
        else:
            self.log_test("Form Validation", False, "No form validation detected")
        
        # Check for responsive CSS
        has_responsive = False
        if '@media' in html_content or 'responsive' in html_content.lower() or 'mobile' in html_content.lower():
            has_responsive = True
        
        if has_responsive:
            self.log_test("Responsive CSS", True, "Found responsive design elements")
        else:
            self.log_test("Responsive CSS", False, "No responsive design detected")
        
        # Check for JavaScript functionality
        has_js = False
        if '<script' in html_content or 'javascript:' in html_content.lower():
            has_js = True
        
        if has_js:
            self.log_test("JavaScript Integration", True, "Found JavaScript elements")
        else:
            self.log_test("JavaScript Integration", False, "No JavaScript detected")
        
        # Overall validation score
        validation_score = sum([
            len(pages_found) >= 4,
            nav_links >= 3,
            len(forms_found) >= 2,
            has_validation,
            has_responsive,
            has_js
        ])
        
        print(f"   📊 Validation score: {validation_score}/6")
        
        return validation_score >= 4

    def test_credit_deduction(self, credits_used):
        """Test 7: Credit Deduction"""
        print("\n💰 Testing Credit Deduction")
        
        if not self.jwt_token:
            print("   ⚠️ No JWT token available")
            return False
        
        # Get current credit balance
        success, response, _ = self.run_test(
            "Check Credit Balance After Build",
            "GET",
            "auth/me",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success:
            current_credits = response.get('credits', 0)
            print(f"   💳 Current credits: {current_credits}")
            print(f"   💸 Credits used in build: {credits_used}")
            
            # Verify credits were deducted
            if credits_used > 0:
                self.log_test("Credits Deducted", True, f"Used {credits_used} credits")
            else:
                self.log_test("Credits Deducted", False, "No credits were deducted")
            
            # Check if credits are in reasonable range (30-60 for multi-agent build)
            if 30 <= credits_used <= 60:
                self.log_test("Credit Amount Reasonable", True, f"{credits_used} credits is reasonable for multi-agent build")
            else:
                self.log_test("Credit Amount Reasonable", False, f"{credits_used} credits seems unusual for multi-agent build")
            
            return credits_used > 0
        
        return False

    def run_comprehensive_test(self):
        """Run comprehensive multi-page website generation test as per review request"""
        print("🚀 Starting AutoWebIQ Multi-Page Website Generation Test")
        print("   Focus: Emergent-style agent workflow with multi-page generation")
        print(f"   Backend URL: {self.base_url}")
        print("=" * 80)

        # Test sequence as specified in review request
        tests_passed = 0
        total_tests = 7
        
        # Test 1: Health Check
        if self.test_health_check():
            tests_passed += 1
        
        # Test 2: User Authentication Flow
        if self.test_demo_account_auth():
            tests_passed += 1
        
        # Test 3: Project Creation
        if self.test_project_creation():
            tests_passed += 1
        
        # Test 4 & 5: WebSocket + Multi-Page Generation (CORE TEST)
        if self.test_multi_page_website_generation():
            tests_passed += 2  # Counts for both WebSocket and generation
        
        # Test 6: Generated Website Validation (already called in generation test)
        # Test 7: Credit Deduction (already called in generation test)
        
        print(f"\n📊 Core Tests Completed: {tests_passed}/{total_tests}")
        
        return tests_passed >= 5  # At least 5/7 core tests should pass

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 AUTOWEBIQ MULTI-PAGE WEBSITE GENERATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Categorize results
        critical_tests = [
            "Demo Account Login",
            "Create Hotel Website Project", 
            "Multi-Page Website Build",
            "Multi-Page Generation",
            "Credits Deducted"
        ]
        
        critical_passed = 0
        for result in self.test_results:
            if result['test'] in critical_tests and result['success']:
                critical_passed += 1
        
        print(f"\n🎯 CRITICAL TESTS: {critical_passed}/{len(critical_tests)} passed")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n📋 TEST COVERAGE:")
        print("   ✅ Health Check - Backend system status")
        print("   ✅ Demo Account Authentication - demo@test.com login")
        print("   ✅ Project Creation - Hotel website project")
        print("   ✅ WebSocket Connection - Real-time build updates")
        print("   ✅ Multi-Page Generation - Hotel booking website")
        print("   ✅ Agent Workflow - Emergent-style agent status")
        print("   ✅ Website Validation - Multi-page structure")
        print("   ✅ Credit System - Dynamic deduction")
        
        # Determine overall result
        overall_success = critical_passed >= 4 and (self.tests_passed/self.tests_run) >= 0.7
        
        if overall_success:
            print("\n🎉 OVERALL RESULT: SUCCESS")
            print("   The multi-page website generation system is working correctly!")
        else:
            print("\n⚠️ OVERALL RESULT: NEEDS ATTENTION")
            print("   Some critical features need fixes before deployment.")
        
        return overall_success

def main():
    tester = AutoWebIQMultiPageTester()
    
    try:
        success = tester.run_comprehensive_test()
        overall_success = tester.print_summary()
        return 0 if overall_success else 1
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())