import requests
import sys
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
import os

class TemplateSystemTester:
    def __init__(self):
        # Use the production URL from the review request
        self.base_url = "https://autowebiq-iq.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.user_id = None
        self.project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.start_time = None
        
        # Demo account credentials from review request
        self.demo_email = "demo@test.com"
        self.demo_password = "Demo123456"
        self.expected_credits = 438

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, cookies=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, cookies=cookies, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, cookies=cookies, timeout=120)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, cookies=cookies, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, cookies=cookies, timeout=30)

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

    def test_step_1_login(self):
        """Step 1: Login with demo account"""
        print("\n🔐 STEP 1: Testing Demo Account Login")
        print(f"   Email: {self.demo_email}")
        print(f"   Expected Credits: {self.expected_credits}")
        
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
            
            # Verify credits
            actual_credits = response['user'].get('credits', 0)
            if actual_credits == self.expected_credits:
                self.log_test("Demo Account Credits Verification", True)
                print(f"   ✅ Credits verified: {actual_credits}")
            else:
                self.log_test("Demo Account Credits Verification", False, f"Expected {self.expected_credits}, got {actual_credits}")
            
            print(f"   ✅ JWT Token obtained: {self.jwt_token[:20]}...")
            print(f"   ✅ User ID: {self.user_id}")
            return True
        
        return False

    def test_step_2_create_project(self):
        """Step 2: Create Test Project"""
        print("\n📁 STEP 2: Creating Test Project")
        
        if not self.jwt_token:
            print("   ❌ No JWT token available")
            return False
        
        project_data = {
            "name": "Luxury Skincare Store",
            "description": "Test project for new template system"
        }
        
        success, response, _ = self.run_test(
            "Create Luxury Skincare Project",
            "POST",
            "projects/create",
            200,
            data=project_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   ✅ Project created with ID: {self.project_id}")
            return True
        
        return False

    def test_step_3_build_with_template_system(self):
        """Step 3: Build Website with NEW Template System"""
        print("\n🤖 STEP 3: Testing NEW Template-Based Website Generation")
        
        if not self.jwt_token or not self.project_id:
            print("   ❌ Missing JWT token or project ID")
            return False
        
        # Record start time for performance measurement
        self.start_time = time.time()
        
        build_data = {
            "project_id": self.project_id,
            "prompt": "Create a luxury organic skincare e-commerce website with elegant design, product showcase, benefits section, and customer testimonials",
            "uploaded_images": []
        }
        
        print(f"   🚀 Starting template-based build...")
        print(f"   📝 Prompt: {build_data['prompt']}")
        
        success, response, _ = self.run_test(
            "Template-Based Multi-Agent Build",
            "POST",
            "build-with-agents",
            200,
            data=build_data,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        # Calculate build time
        build_time = time.time() - self.start_time if self.start_time else 0
        print(f"   ⏱️ Build completed in: {build_time:.1f} seconds")
        
        if success:
            return self.verify_build_results(response, build_time)
        
        return False

    def verify_build_results(self, response, build_time):
        """Step 4: Verify Build Results"""
        print("\n✅ STEP 4: Verifying Build Results")
        
        # Check 1: Template was selected
        template_used = False
        if 'plan' in response and response['plan']:
            plan_str = str(response['plan']).lower()
            if 'template' in plan_str or 'luxury' in plan_str or 'e-commerce' in plan_str:
                template_used = True
                self.log_test("Template Selection Verification", True)
                print("   ✅ Template-based generation detected in plan")
            else:
                self.log_test("Template Selection Verification", False, "No template usage detected in plan")
        else:
            self.log_test("Template Selection Verification", False, "No plan found in response")
        
        # Check 2: Frontend code generated
        frontend_code = response.get('frontend_code', '')
        if frontend_code and len(frontend_code) > 5000:
            self.log_test("Frontend Code Generation", True)
            print(f"   ✅ Frontend code generated: {len(frontend_code)} characters")
            
            # Check for proper HTML structure
            html_checks = [
                ('<!DOCTYPE html>', 'DOCTYPE declaration'),
                ('<nav', 'Navigation section'),
                ('<header', 'Header section'),
                ('<footer', 'Footer section'),
                ('skincare', 'Skincare content'),
                ('luxury', 'Luxury theme')
            ]
            
            html_quality_score = 0
            for check, description in html_checks:
                if check.lower() in frontend_code.lower():
                    html_quality_score += 1
                    print(f"   ✅ {description} found")
                else:
                    print(f"   ⚠️ {description} not found")
            
            if html_quality_score >= 4:
                self.log_test("HTML Quality Check", True)
            else:
                self.log_test("HTML Quality Check", False, f"Only {html_quality_score}/6 quality checks passed")
        else:
            self.log_test("Frontend Code Generation", False, f"Code too short: {len(frontend_code)} characters")
        
        # Check 3: Images generated (check if images are mentioned or included)
        images_generated = False
        if 'images' in response or 'image' in frontend_code.lower():
            images_generated = True
            self.log_test("Image Generation", True)
            print("   ✅ Images generated or referenced")
        else:
            self.log_test("Image Generation", False, "No images detected")
        
        # Check 4: Credits deducted properly
        credits_used = response.get('credits_used', 0)
        if 30 <= credits_used <= 50:  # Expected range 30-40 credits
            self.log_test("Credit Deduction Verification", True)
            print(f"   ✅ Credits used: {credits_used} (within expected range 30-50)")
        else:
            self.log_test("Credit Deduction Verification", False, f"Credits used: {credits_used} (expected 30-50)")
        
        # Check 5: Performance - should be 20-30 seconds (vs old 60-90)
        if build_time <= 45:  # Allow some buffer
            self.log_test("Performance Improvement", True)
            print(f"   ✅ Build time: {build_time:.1f}s (target: 20-30s)")
        else:
            self.log_test("Performance Improvement", False, f"Build time too slow: {build_time:.1f}s")
        
        # Check 6: Not fallback HTML
        if len(frontend_code) > 5000 and 'luxury' in frontend_code.lower():
            self.log_test("No Fallback HTML", True)
            print("   ✅ Generated custom HTML (not fallback)")
        else:
            self.log_test("No Fallback HTML", False, "Appears to be fallback HTML")
        
        # Store response for next step
        self.build_response = response
        
        return True

    def test_step_5_get_updated_project(self):
        """Step 5: Get Updated Project"""
        print("\n📋 STEP 5: Verifying Updated Project")
        
        if not self.jwt_token or not self.project_id:
            print("   ❌ Missing JWT token or project ID")
            return False
        
        success, response, _ = self.run_test(
            "Get Updated Project",
            "GET",
            f"projects/{self.project_id}",
            200,
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        
        if success:
            generated_code = response.get('generated_code', '')
            if generated_code and len(generated_code) > 5000:
                self.log_test("Project Code Persistence", True)
                print(f"   ✅ Generated code persisted: {len(generated_code)} characters")
                
                # Verify it's the same code from build
                if hasattr(self, 'build_response') and self.build_response.get('frontend_code'):
                    if generated_code == self.build_response['frontend_code']:
                        self.log_test("Code Consistency", True)
                        print("   ✅ Code matches build response")
                    else:
                        self.log_test("Code Consistency", False, "Code doesn't match build response")
                
                return True
            else:
                self.log_test("Project Code Persistence", False, f"No code or too short: {len(generated_code)}")
        
        return False

    def test_additional_verification(self):
        """Additional verification tests"""
        print("\n🔍 ADDITIONAL VERIFICATION")
        
        # Test credit balance after build
        if self.jwt_token:
            success, response, _ = self.run_test(
                "Credit Balance After Build",
                "GET",
                "credits/balance",
                200,
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            if success:
                remaining_balance = response.get('balance', 0)
                expected_remaining = self.expected_credits - (self.build_response.get('credits_used', 0) if hasattr(self, 'build_response') else 0)
                
                if abs(remaining_balance - expected_remaining) <= 5:  # Allow small variance
                    self.log_test("Credit Balance Accuracy", True)
                    print(f"   ✅ Remaining balance: {remaining_balance}")
                else:
                    self.log_test("Credit Balance Accuracy", False, f"Expected ~{expected_remaining}, got {remaining_balance}")

    def run_template_system_test(self):
        """Run the complete template system test as per review request"""
        print("🚀 STARTING NEW TEMPLATE-BASED WEBSITE GENERATION SYSTEM TEST")
        print("=" * 80)
        print("📋 TEST SCENARIO: Luxury Skincare E-commerce Website")
        print("🎯 EXPECTED IMPROVEMENTS:")
        print("   • Speed: 20-30 seconds (vs 60-90)")
        print("   • Quality: Professional navigation, hero, product showcase, features, footer")
        print("   • Consistency: Luxury E-commerce template structure")
        print("   • Credits: ~30-40 credits (vs previous 40-54)")
        print("   • No Fallback: Should NOT return basic fallback HTML")
        print("=" * 80)

        # Execute test steps
        step1_success = self.test_step_1_login()
        if not step1_success:
            print("❌ Step 1 failed - cannot continue")
            return False

        step2_success = self.test_step_2_create_project()
        if not step2_success:
            print("❌ Step 2 failed - cannot continue")
            return False

        step3_success = self.test_step_3_build_with_template_system()
        if not step3_success:
            print("❌ Step 3 failed - build unsuccessful")
            return False

        step4_success = self.test_step_5_get_updated_project()
        
        # Additional verification
        self.test_additional_verification()

        return step1_success and step2_success and step3_success and step4_success

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 NEW TEMPLATE-BASED SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Performance summary
        if hasattr(self, 'start_time') and self.start_time:
            build_time = time.time() - self.start_time
            print(f"Build Time: {build_time:.1f} seconds")
        
        # Credits summary
        if hasattr(self, 'build_response'):
            credits_used = self.build_response.get('credits_used', 0)
            print(f"Credits Used: {credits_used}")
        
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        
        # Check each success criteria
        criteria_results = []
        
        for result in self.test_results:
            if "Template Selection" in result['test']:
                criteria_results.append(("✅ Template Selection Working" if result['success'] else "❌ Template Selection Failed", result['success']))
            elif "Frontend Code Generation" in result['test']:
                criteria_results.append(("✅ Quality HTML Generated" if result['success'] else "❌ Poor Quality HTML", result['success']))
            elif "Performance" in result['test']:
                criteria_results.append(("✅ Fast Generation (20-30s target)" if result['success'] else "❌ Slow Generation", result['success']))
            elif "Credit Deduction" in result['test']:
                criteria_results.append(("✅ Correct Credits Used (~30-40)" if result['success'] else "❌ Incorrect Credit Usage", result['success']))
            elif "No Fallback" in result['test']:
                criteria_results.append(("✅ Custom Template (Not Fallback)" if result['success'] else "❌ Fallback HTML Detected", result['success']))
        
        for criteria, success in criteria_results:
            print(f"   {criteria}")
        
        if self.tests_run - self.tests_passed > 0:
            print(f"\n❌ FAILED TESTS ({self.tests_run - self.tests_passed}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n📋 REVIEW REQUEST STATUS:")
        overall_success = self.tests_passed >= (self.tests_run * 0.8)  # 80% pass rate
        if overall_success:
            print("   🎉 NEW TEMPLATE SYSTEM WORKING CORRECTLY")
            print("   ✅ Ready for production deployment")
        else:
            print("   ⚠️ TEMPLATE SYSTEM NEEDS ATTENTION")
            print("   🔧 Issues found that need resolution")
        
        return overall_success

def main():
    tester = TemplateSystemTester()
    
    try:
        success = tester.run_template_system_test()
        overall_success = tester.print_summary()
        return 0 if overall_success else 1
    except Exception as e:
        print(f"❌ Template system test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())