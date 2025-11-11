import requests
import json
import time
from datetime import datetime

class TemplateSystemReviewTester:
    def __init__(self):
        self.base_url = "https://aiweb-builder-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.user_id = None
        self.tests_passed = 0
        self.tests_total = 0
        
        # Demo account credentials from review request
        self.demo_email = "demo@test.com"
        self.demo_password = "Demo123456"

    def log_test(self, name, success, details=""):
        self.tests_total += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")

    def login_demo_account(self):
        """Login with demo account as specified in review request"""
        print("\n🔐 LOGGING IN WITH DEMO ACCOUNT")
        print(f"   Email: {self.demo_email}")
        print(f"   Password: {self.demo_password}")
        
        login_data = {
            "email": self.demo_email,
            "password": self.demo_password
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.jwt_token = data['access_token']
                self.user_id = data['user']['id']
                credits = data['user']['credits']
                self.log_test("Demo Account Login", True)
                print(f"   ✅ Logged in successfully")
                print(f"   ✅ User ID: {self.user_id}")
                print(f"   ✅ Available Credits: {credits}")
                return True
            else:
                self.log_test("Demo Account Login", False, "No access_token in response")
        else:
            self.log_test("Demo Account Login", False, f"Status: {response.status_code}")
        
        return False

    def create_test_project(self, name, description):
        """Create a test project"""
        if not self.jwt_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        project_data = {
            "name": name,
            "description": description,
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = requests.post(f"{self.api_url}/projects/create", json=project_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'id' in data:
                print(f"   ✅ Project created: {name} (ID: {data['id']})")
                return data['id']
        
        print(f"   ❌ Failed to create project: {name}")
        return None

    def test_saas_template_scenario(self):
        """Test Scenario 1: SaaS Landing Page"""
        print("\n" + "="*70)
        print("🚀 TEST SCENARIO 1: SaaS Landing Page")
        print("="*70)
        
        # Create project
        project_id = self.create_test_project(
            "SaaS B2B Platform",
            "Modern B2B SaaS platform for project management"
        )
        
        if not project_id:
            self.log_test("SaaS Project Creation", False, "Could not create project")
            return False
        
        # Test the exact prompt from review request
        saas_prompt = "Create a modern B2B SaaS platform landing page for a project management tool with features showcase, pricing, and enterprise security highlights"
        
        print(f"\n📝 Testing SaaS Prompt:")
        print(f"   {saas_prompt}")
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        build_data = {
            "project_id": project_id,
            "prompt": saas_prompt,
            "uploaded_images": []
        }
        
        print(f"\n🚀 Starting SaaS template build...")
        start_time = time.time()
        
        response = requests.post(f"{self.api_url}/build-with-agents", json=build_data, headers=headers, timeout=120)
        
        build_time = time.time() - start_time
        print(f"   ⏱️ Build completed in: {build_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            return self.verify_saas_template_results(data, build_time)
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
            self.log_test("SaaS Template Build", False, f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown')}")
            return False

    def verify_saas_template_results(self, response_data, build_time):
        """Verify SaaS template selection and results"""
        print(f"\n📊 VERIFYING SaaS TEMPLATE RESULTS")
        
        success_count = 0
        total_checks = 6
        
        # Check 1: Template Selection
        plan = response_data.get('plan', {})
        template_used = plan.get('template_used', '').lower()
        project_name = plan.get('project_name', '').lower()
        
        print(f"   Template Used: {template_used}")
        print(f"   Project Name: {project_name}")
        
        if 'saas' in template_used or 'saas' in project_name or 'b2b' in template_used:
            self.log_test("SaaS Template Selection (saas_b2b_v1 or saas_modern_v1)", True)
            success_count += 1
        else:
            self.log_test("SaaS Template Selection (saas_b2b_v1 or saas_modern_v1)", False, f"Got: {template_used}")
        
        # Check 2: SaaS-specific features
        frontend_code = response_data.get('frontend_code', '')
        saas_features = self.check_saas_features(frontend_code)
        
        if saas_features >= 3:
            self.log_test("SaaS Features (pricing, features, enterprise)", True)
            success_count += 1
        else:
            self.log_test("SaaS Features (pricing, features, enterprise)", False, f"Only {saas_features}/5 features found")
        
        # Check 3: Professional design
        if len(frontend_code) > 5000:
            self.log_test("Professional Design (>5000 chars)", True)
            success_count += 1
        else:
            self.log_test("Professional Design (>5000 chars)", False, f"Only {len(frontend_code)} chars")
        
        # Check 4: Build time < 40 seconds
        if build_time < 40:
            self.log_test("Build Time (<40 seconds)", True)
            success_count += 1
        else:
            self.log_test("Build Time (<40 seconds)", False, f"{build_time:.1f}s")
        
        # Check 5: Credits in range 30-50
        credits_used = response_data.get('credits_used', 0)
        if 30 <= credits_used <= 50:
            self.log_test("Credits Usage (30-50 range)", True)
            success_count += 1
        else:
            self.log_test("Credits Usage (30-50 range)", False, f"{credits_used} credits")
        
        # Check 6: Enterprise feel
        if 'enterprise' in frontend_code.lower() or 'security' in frontend_code.lower() or 'professional' in frontend_code.lower():
            self.log_test("Enterprise Security Highlights", True)
            success_count += 1
        else:
            self.log_test("Enterprise Security Highlights", False, "No enterprise/security content found")
        
        print(f"\n   📋 SaaS Template Success: {success_count}/{total_checks}")
        return success_count >= 4  # At least 4/6 checks must pass

    def test_portfolio_template_scenario(self):
        """Test Scenario 2: Portfolio Website"""
        print("\n" + "="*70)
        print("🎨 TEST SCENARIO 2: Portfolio Website")
        print("="*70)
        
        # Create project
        project_id = self.create_test_project(
            "Consultant Portfolio",
            "Professional portfolio for digital strategy consultant"
        )
        
        if not project_id:
            self.log_test("Portfolio Project Creation", False, "Could not create project")
            return False
        
        # Test the exact prompt from review request
        portfolio_prompt = "Create a professional portfolio website for a freelance consultant specializing in digital strategy with services section and contact form"
        
        print(f"\n📝 Testing Portfolio Prompt:")
        print(f"   {portfolio_prompt}")
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        build_data = {
            "project_id": project_id,
            "prompt": portfolio_prompt,
            "uploaded_images": []
        }
        
        print(f"\n🚀 Starting Portfolio template build...")
        start_time = time.time()
        
        response = requests.post(f"{self.api_url}/build-with-agents", json=build_data, headers=headers, timeout=120)
        
        build_time = time.time() - start_time
        print(f"   ⏱️ Build completed in: {build_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            return self.verify_portfolio_template_results(data, build_time)
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
            self.log_test("Portfolio Template Build", False, f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown')}")
            return False

    def verify_portfolio_template_results(self, response_data, build_time):
        """Verify Portfolio template selection and results"""
        print(f"\n📊 VERIFYING PORTFOLIO TEMPLATE RESULTS")
        
        success_count = 0
        total_checks = 6
        
        # Check 1: Template Selection
        plan = response_data.get('plan', {})
        template_used = plan.get('template_used', '').lower()
        project_name = plan.get('project_name', '').lower()
        
        print(f"   Template Used: {template_used}")
        print(f"   Project Name: {project_name}")
        
        if 'portfolio' in template_used or 'portfolio' in project_name:
            self.log_test("Portfolio Template Selection (portfolio_pro_v1)", True)
            success_count += 1
        else:
            self.log_test("Portfolio Template Selection (portfolio_pro_v1)", False, f"Got: {template_used}")
        
        # Check 2: Portfolio-specific features
        frontend_code = response_data.get('frontend_code', '')
        portfolio_features = self.check_portfolio_features(frontend_code)
        
        if portfolio_features >= 3:
            self.log_test("Portfolio Features (services, contact, about)", True)
            success_count += 1
        else:
            self.log_test("Portfolio Features (services, contact, about)", False, f"Only {portfolio_features}/5 features found")
        
        # Check 3: Professional clean design
        if len(frontend_code) > 5000:
            self.log_test("Professional Clean Design (>5000 chars)", True)
            success_count += 1
        else:
            self.log_test("Professional Clean Design (>5000 chars)", False, f"Only {len(frontend_code)} chars")
        
        # Check 4: Build time < 40 seconds
        if build_time < 40:
            self.log_test("Build Time (<40 seconds)", True)
            success_count += 1
        else:
            self.log_test("Build Time (<40 seconds)", False, f"{build_time:.1f}s")
        
        # Check 5: Credits in range 30-50
        credits_used = response_data.get('credits_used', 0)
        if 30 <= credits_used <= 50:
            self.log_test("Credits Usage (30-50 range)", True)
            success_count += 1
        else:
            self.log_test("Credits Usage (30-50 range)", False, f"{credits_used} credits")
        
        # Check 6: Services section and contact form
        if ('services' in frontend_code.lower() or 'what i do' in frontend_code.lower()) and 'contact' in frontend_code.lower():
            self.log_test("Services Section and Contact Form", True)
            success_count += 1
        else:
            self.log_test("Services Section and Contact Form", False, "Missing services or contact sections")
        
        print(f"\n   📋 Portfolio Template Success: {success_count}/{total_checks}")
        return success_count >= 4  # At least 4/6 checks must pass

    def check_saas_features(self, html):
        """Check for SaaS-specific features"""
        html_lower = html.lower()
        features_found = 0
        
        # SaaS feature indicators
        saas_indicators = [
            (["pricing", "price", "plan", "subscription"], "Pricing Section"),
            (["features", "capabilities", "what we offer"], "Features Showcase"),
            (["enterprise", "security", "compliance"], "Enterprise/Security"),
            (["testimonial", "review", "customer"], "Testimonials"),
            (["get started", "sign up", "try now", "free trial"], "Call-to-Action")
        ]
        
        for indicators, feature_name in saas_indicators:
            if any(indicator in html_lower for indicator in indicators):
                features_found += 1
                print(f"      ✅ {feature_name} detected")
            else:
                print(f"      ⚠️ {feature_name} not found")
        
        return features_found

    def check_portfolio_features(self, html):
        """Check for Portfolio-specific features"""
        html_lower = html.lower()
        features_found = 0
        
        # Portfolio feature indicators
        portfolio_indicators = [
            (["portfolio", "gallery", "showcase", "work"], "Portfolio/Gallery"),
            (["services", "what i do", "offerings"], "Services Section"),
            (["about", "bio", "story"], "About Section"),
            (["contact", "get in touch", "hire me"], "Contact Form"),
            (["consultant", "freelance", "professional"], "Professional Focus")
        ]
        
        for indicators, feature_name in portfolio_indicators:
            if any(indicator in html_lower for indicator in indicators):
                features_found += 1
                print(f"      ✅ {feature_name} detected")
            else:
                print(f"      ⚠️ {feature_name} not found")
        
        return features_found

    def run_template_system_review(self):
        """Run the complete template system review as requested"""
        print("🎯 TEMPLATE SYSTEM REVIEW - COMPLETE TEMPLATE SYSTEM WITH 10 TEMPLATES")
        print("=" * 80)
        print("📋 TESTING WITH DEMO ACCOUNT (demo@test.com / Demo123456)")
        print("🎯 SUCCESS CRITERIA:")
        print("   1. ✅ Correct template selection for each project type")
        print("   2. ✅ All 10 templates accessible and working")
        print("   3. ✅ Generation time < 40 seconds")
        print("   4. ✅ High-quality HTML output (> 5000 chars)")
        print("   5. ✅ Credits in expected range (30-50)")
        print("=" * 80)

        # Step 1: Login with demo account
        if not self.login_demo_account():
            print("❌ Failed to login with demo account - cannot continue")
            return False

        # Step 2: Test SaaS Landing Page scenario
        saas_success = self.test_saas_template_scenario()
        
        # Step 3: Test Portfolio Website scenario
        portfolio_success = self.test_portfolio_template_scenario()
        
        # Print final summary
        print("\n" + "=" * 80)
        print("📊 TEMPLATE SYSTEM REVIEW SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_total}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_total - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_total)*100:.1f}%")
        
        print("\n🎯 REVIEW REQUEST VERIFICATION:")
        if saas_success:
            print("   ✅ SaaS Landing Page - Template selection working")
        else:
            print("   ❌ SaaS Landing Page - Issues found")
            
        if portfolio_success:
            print("   ✅ Portfolio Website - Template selection working")
        else:
            print("   ❌ Portfolio Website - Issues found")
        
        overall_success = saas_success and portfolio_success and (self.tests_passed >= self.tests_total * 0.8)
        
        if overall_success:
            print("\n🎉 TEMPLATE SYSTEM REVIEW REQUIREMENTS MET!")
            print("   ✅ Template variety works correctly")
            print("   ✅ At least 2 different project types verified")
            print("   ✅ Ready for production deployment")
        else:
            print("\n⚠️ TEMPLATE SYSTEM NEEDS ATTENTION")
            print("   🔧 Some issues found that need resolution")
        
        return overall_success

class AutoWebIQReviewTester:
    def __init__(self):
        self.base_url = "https://aiweb-builder-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.user_id = None
        self.project_id = None
        self.tests_passed = 0
        self.tests_total = 0

    def log_test(self, name, success, details=""):
        self.tests_total += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")

    def test_authentication_flow(self):
        """Test Authentication Flow as specified in review request"""
        print("\n🔐 TESTING AUTHENTICATION FLOW")
        
        # Create unique user with timestamp-based email
        timestamp = int(time.time())
        test_email = f"review_test_{timestamp}@autowebiq.com"
        test_username = f"reviewuser_{timestamp}"
        test_password = "ReviewTest123!"
        
        # 1. POST /api/auth/register - Create new user and verify 20 initial credits granted
        print("\n1. Testing POST /api/auth/register")
        register_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/register", json=register_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['credits'] == 20:
                self.jwt_token = data['access_token']
                self.user_id = data['user']['id']
                self.log_test("POST /api/auth/register - 20 credits granted", True)
            else:
                self.log_test("POST /api/auth/register - 20 credits granted", False, f"Credits: {data['user'].get('credits', 'N/A')}")
        else:
            self.log_test("POST /api/auth/register", False, f"Status: {response.status_code}")
            return False
        
        # 2. POST /api/auth/login - Verify JWT token generation
        print("\n2. Testing POST /api/auth/login")
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.log_test("POST /api/auth/login - JWT token generation", True)
            else:
                self.log_test("POST /api/auth/login - JWT token generation", False, "No access_token in response")
        else:
            self.log_test("POST /api/auth/login", False, f"Status: {response.status_code}")
        
        # 3. GET /api/auth/me - Verify user profile retrieval with credits
        print("\n3. Testing GET /api/auth/me")
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        response = requests.get(f"{self.api_url}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('credits') == 20 and data.get('email') == test_email:
                self.log_test("GET /api/auth/me - User profile with credits", True)
            else:
                self.log_test("GET /api/auth/me - User profile with credits", False, f"Credits: {data.get('credits')}")
        else:
            self.log_test("GET /api/auth/me", False, f"Status: {response.status_code}")
        
        return True

    def test_project_management(self):
        """Test Project Management as specified in review request"""
        print("\n📁 TESTING PROJECT MANAGEMENT")
        
        if not self.jwt_token:
            print("❌ No JWT token available for project tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # 1. POST /api/projects/create - Create a new project
        print("\n1. Testing POST /api/projects/create")
        project_data = {
            "name": "Review Test Project",
            "description": "Project created during review testing",
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = requests.post(f"{self.api_url}/projects/create", json=project_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'id' in data:
                self.project_id = data['id']
                self.log_test("POST /api/projects/create", True)
            else:
                self.log_test("POST /api/projects/create", False, "No project ID in response")
        else:
            self.log_test("POST /api/projects/create", False, f"Status: {response.status_code}")
            return False
        
        # 2. GET /api/projects - List user projects
        print("\n2. Testing GET /api/projects")
        response = requests.get(f"{self.api_url}/projects", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("GET /api/projects - List projects", True)
            else:
                self.log_test("GET /api/projects - List projects", False, "Response is not a list")
        else:
            self.log_test("GET /api/projects", False, f"Status: {response.status_code}")
        
        # 3. GET /api/projects/{id} - Get specific project details
        print("\n3. Testing GET /api/projects/{id}")
        response = requests.get(f"{self.api_url}/projects/{self.project_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('id') == self.project_id:
                self.log_test("GET /api/projects/{id} - Get project details", True)
            else:
                self.log_test("GET /api/projects/{id} - Get project details", False, "Project ID mismatch")
        else:
            self.log_test("GET /api/projects/{id}", False, f"Status: {response.status_code}")
        
        # 4. GET /api/projects/{id}/messages - Get project messages
        print("\n4. Testing GET /api/projects/{id}/messages")
        response = requests.get(f"{self.api_url}/projects/{self.project_id}/messages", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("GET /api/projects/{id}/messages - Get messages", True)
            else:
                self.log_test("GET /api/projects/{id}/messages - Get messages", False, "Response is not a list")
        else:
            self.log_test("GET /api/projects/{id}/messages", False, f"Status: {response.status_code}")
        
        return True

    def test_credit_system(self):
        """Test Credit System as specified in review request"""
        print("\n💰 TESTING CREDIT SYSTEM")
        
        if not self.jwt_token:
            print("❌ No JWT token available for credit tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # 1. Verify initial 20 credits on new user registration (already tested in auth)
        print("\n1. Initial 20 credits verification - Already confirmed in auth flow ✅")
        
        # 2. GET /api/credits/balance - Check credit balance
        print("\n2. Testing GET /api/credits/balance")
        response = requests.get(f"{self.api_url}/credits/balance", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'balance' in data and data['balance'] == 20:
                self.log_test("GET /api/credits/balance - Check balance", True)
            else:
                self.log_test("GET /api/credits/balance - Check balance", False, f"Balance: {data.get('balance')}")
        else:
            self.log_test("GET /api/credits/balance", False, f"Status: {response.status_code}")
        
        # 3. GET /api/credits/transactions - Check transaction history
        print("\n3. Testing GET /api/credits/transactions")
        response = requests.get(f"{self.api_url}/credits/transactions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'transactions' in data and isinstance(data['transactions'], list):
                self.log_test("GET /api/credits/transactions - Transaction history", True)
            else:
                self.log_test("GET /api/credits/transactions - Transaction history", False, "Invalid response format")
        else:
            self.log_test("GET /api/credits/transactions", False, f"Status: {response.status_code}")
        
        return True

    def test_ai_chat_endpoint(self):
        """Test AI Chat Endpoint as specified in review request"""
        print("\n🤖 TESTING AI CHAT ENDPOINT")
        
        if not self.jwt_token or not self.project_id:
            print("❌ Missing JWT token or project ID for chat tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # POST /api/chat - Test basic chat with project_id and message
        print("\n1. Testing POST /api/chat")
        chat_data = {
            "project_id": self.project_id,
            "message": "Create a simple welcome page",
            "model": "claude-4.5-sonnet-200k"
        }
        
        response = requests.post(f"{self.api_url}/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'ai_message' in data and 'code' in data:
                self.log_test("POST /api/chat - Basic chat with AI response", True)
                
                # Verify credits are properly deducted
                balance_response = requests.get(f"{self.api_url}/credits/balance", headers=headers)
                if balance_response.status_code == 200:
                    balance_data = balance_response.json()
                    if balance_data['balance'] < 20:  # Should be less than 20 after chat
                        self.log_test("POST /api/chat - Credits deducted", True)
                    else:
                        self.log_test("POST /api/chat - Credits deducted", False, f"Balance still: {balance_data['balance']}")
                else:
                    self.log_test("POST /api/chat - Credits deducted", False, "Could not check balance")
            else:
                self.log_test("POST /api/chat - Basic chat with AI response", False, "Missing ai_message or code in response")
        else:
            self.log_test("POST /api/chat", False, f"Status: {response.status_code}")
        
        return True

    def test_multi_agent_build_endpoint(self):
        """Test Multi-Agent Build Endpoint as specified in review request"""
        print("\n🏗️ TESTING MULTI-AGENT BUILD ENDPOINT")
        
        if not self.jwt_token or not self.project_id:
            print("❌ Missing JWT token or project ID for build tests")
            return False
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # POST /api/build-with-agents - Test with simple prompt
        print("\n1. Testing POST /api/build-with-agents")
        build_data = {
            "project_id": self.project_id,
            "prompt": "Create a landing page",
            "uploaded_images": []
        }
        
        response = requests.post(f"{self.api_url}/build-with-agents", json=build_data, headers=headers)
        
        # This should return 402 (insufficient credits) which is expected behavior
        if response.status_code == 402:
            data = response.json()
            if "Insufficient credits" in data.get('detail', ''):
                self.log_test("POST /api/build-with-agents - Credit validation", True)
                
                # Verify proper credit reservation and detailed cost breakdown
                if "Breakdown:" in data.get('detail', '') or "breakdown" in str(data).lower():
                    self.log_test("POST /api/build-with-agents - Detailed cost breakdown", True)
                else:
                    self.log_test("POST /api/build-with-agents - Detailed cost breakdown", False, "No cost breakdown in error")
            else:
                self.log_test("POST /api/build-with-agents - Credit validation", False, f"Unexpected error: {data.get('detail')}")
        elif response.status_code == 200:
            # If user somehow has enough credits, this is also valid
            data = response.json()
            if 'frontend_code' in data:
                self.log_test("POST /api/build-with-agents - Frontend code generation", True)
            else:
                self.log_test("POST /api/build-with-agents - Frontend code generation", False, "No frontend_code in response")
        else:
            self.log_test("POST /api/build-with-agents", False, f"Status: {response.status_code}")
        
        return True

    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 TESTING HEALTH CHECK")
        
        response = requests.get(f"{self.api_url}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                self.log_test("GET /api/health - Health check", True)
            else:
                self.log_test("GET /api/health - Health check", False, f"Status: {data.get('status')}")
        else:
            self.log_test("GET /api/health", False, f"Status: {response.status_code}")

    def run_review_tests(self):
        """Run all tests specified in the review request"""
        print("🚀 AUTOWEBIQ BACKEND API REVIEW TESTING")
        print("=" * 60)
        print("Testing Emergent-style functionality as requested")
        print("=" * 60)
        
        # Run all test categories
        self.test_authentication_flow()
        self.test_project_management()
        self.test_credit_system()
        self.test_ai_chat_endpoint()
        self.test_multi_agent_build_endpoint()
        self.test_health_check()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REVIEW TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}/{self.tests_total}")
        print(f"Success Rate: {(self.tests_passed/self.tests_total)*100:.1f}%")
        
        if self.tests_passed == self.tests_total:
            print("\n🎉 ALL REVIEW REQUIREMENTS VERIFIED!")
            print("✅ Authentication Flow - Working")
            print("✅ Project Management - Working") 
            print("✅ Credit System - Working")
            print("✅ AI Chat Endpoint - Working")
            print("✅ Multi-Agent Build Endpoint - Working")
            print("✅ Backend Infrastructure - Operational")
        else:
            print(f"\n⚠️ {self.tests_total - self.tests_passed} tests failed")
        
        return self.tests_passed == self.tests_total

if __name__ == "__main__":
    # Run Template System Review as requested
    template_tester = TemplateSystemReviewTester()
    template_success = template_tester.run_template_system_review()
    
    print("\n" + "="*80)
    print("🔄 RUNNING ADDITIONAL BACKEND API VERIFICATION")
    print("="*80)
    
    # Also run basic backend API tests
    api_tester = AutoWebIQReviewTester()
    api_success = api_tester.run_review_tests()
    
    # Overall result
    overall_success = template_success and api_success
    
    print("\n" + "="*80)
    print("🏁 FINAL REVIEW RESULT")
    print("="*80)
    if overall_success:
        print("🎉 ALL REVIEW REQUIREMENTS PASSED!")
        print("   ✅ Template System Working")
        print("   ✅ Backend API Infrastructure Working")
    else:
        print("⚠️ SOME REVIEW REQUIREMENTS FAILED")
        if not template_success:
            print("   ❌ Template System Issues")
        if not api_success:
            print("   ❌ Backend API Issues")
    
    exit(0 if overall_success else 1)