#!/usr/bin/env python3
"""
Multi-Model Router System Testing for AutoWebIQ
Tests the new implementation with intelligent task routing:
- Claude Sonnet 4 for frontend/UI generation
- GPT-4o for backend logic  
- Gemini 2.5 Pro for content generation
- OpenAI gpt-image-1 for HD image generation
"""

import asyncio
import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Test Configuration
BACKEND_URL = "https://autowebiq-iq.preview.emergentagent.com/api"

# Demo Account Credentials
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class MultiModelRouterTester:
    """Comprehensive tester for Multi-Model Router System"""
    
    def __init__(self):
        self.auth_token = None
        self.user_data = None
        self.test_project_id = None
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            print(f"✅ {name}")
        else:
            print(f"❌ {name}: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })
    
    def authenticate_demo_account(self) -> Dict:
        """Authenticate with demo account and verify credits"""
        print(f"\n🔐 Authenticating demo account: {DEMO_EMAIL}")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
            
            auth_data = response.json()
            self.auth_token = auth_data["access_token"]
            self.user_data = auth_data["user"]
            
            print(f"✅ Authentication successful")
            print(f"   User ID: {self.user_data['id']}")
            print(f"   Credits: {self.user_data['credits']}")
            
            # Verify sufficient credits for testing
            if self.user_data['credits'] < 50:
                print(f"⚠️  Warning: Low credits ({self.user_data['credits']}). May need more for full testing.")
            
            self.log_test("Demo Account Authentication", True, f"Credits: {self.user_data['credits']}")
            
            return {
                "success": True,
                "user_id": self.user_data['id'],
                "credits": self.user_data['credits']
            }
            
        except Exception as e:
            self.log_test("Demo Account Authentication", False, str(e))
            return {"success": False, "error": str(e)}
    
    def create_test_project(self) -> Dict:
        """Create a new test project for multi-model testing"""
        print(f"\n📁 Creating test project...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        project_data = {
            "name": "Multi-Model Router Test - Coffee Shop",
            "description": "Test project for verifying multi-model routing system with Claude, GPT, and Gemini"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/projects/create",
                json=project_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Project creation failed: {response.status_code} - {response.text}")
            
            project = response.json()
            self.test_project_id = project["id"]
            
            print(f"✅ Test project created")
            print(f"   Project ID: {self.test_project_id}")
            print(f"   Name: {project['name']}")
            
            self.log_test("Test Project Creation", True, f"Project ID: {self.test_project_id}")
            
            return {
                "success": True,
                "project_id": self.test_project_id,
                "project_name": project['name']
            }
            
        except Exception as e:
            self.log_test("Test Project Creation", False, str(e))
            return {"success": False, "error": str(e)}
    
    def start_multi_model_build(self) -> Dict:
        """Start website build with multi-model routing"""
        print(f"\n🚀 Starting multi-model build...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test prompt for coffee shop (should trigger all models)
        build_request = {
            "project_id": self.test_project_id,
            "prompt": "Create a modern coffee shop website with menu, location, and contact form",
            "uploaded_images": []
        }
        
        try:
            print(f"📤 Sending build request...")
            print(f"   Prompt: {build_request['prompt']}")
            
            # Start the build
            response = requests.post(
                f"{BACKEND_URL}/build-with-agents",
                json=build_request,
                headers=headers,
                timeout=120  # Longer timeout for build
            )
            
            if response.status_code == 402:
                # Insufficient credits
                error_data = response.json()
                print(f"💳 Insufficient credits: {error_data.get('detail', 'Unknown error')}")
                self.log_test("Multi-Model Build Request", False, "Insufficient credits")
                return {
                    "success": False,
                    "error": "insufficient_credits",
                    "details": error_data
                }
            
            if response.status_code != 200:
                raise Exception(f"Build request failed: {response.status_code} - {response.text}")
            
            build_result = response.json()
            
            print(f"✅ Build request completed")
            print(f"   Status: {build_result.get('status', 'unknown')}")
            
            # Check for multi-model indicators in response
            model_indicators = {
                "claude_mentioned": False,
                "gpt_mentioned": False,
                "gemini_mentioned": False,
                "image_generation": False
            }
            
            response_text = json.dumps(build_result).lower()
            
            if any(term in response_text for term in ['claude', 'sonnet']):
                model_indicators["claude_mentioned"] = True
                print(f"🎯 Claude model detected in response")
            
            if any(term in response_text for term in ['gpt', 'openai']):
                model_indicators["gpt_mentioned"] = True
                print(f"🎯 GPT model detected in response")
            
            if 'gemini' in response_text:
                model_indicators["gemini_mentioned"] = True
                print(f"🎯 Gemini model detected in response")
            
            if any(term in response_text for term in ['image', 'generated', 'photo']):
                model_indicators["image_generation"] = True
                print(f"🎯 Image generation detected in response")
            
            models_detected = sum(model_indicators.values())
            
            self.log_test("Multi-Model Build Execution", True, f"Models detected: {models_detected}/4")
            
            return {
                "success": True,
                "build_result": build_result,
                "model_indicators": model_indicators,
                "models_detected": models_detected
            }
            
        except Exception as e:
            self.log_test("Multi-Model Build Execution", False, str(e))
            return {"success": False, "error": str(e)}
    
    def verify_build_completion(self) -> Dict:
        """Verify the build completed successfully and check quality"""
        print(f"\n🔍 Verifying build completion...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Get project details
            response = requests.get(
                f"{BACKEND_URL}/projects/{self.test_project_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get project: {response.status_code}")
            
            project = response.json()
            generated_code = project.get('generated_code', '')
            
            # Quality checks
            quality_metrics = {
                "has_html": bool(generated_code and len(generated_code) > 1000),
                "has_doctype": "<!DOCTYPE html>" in generated_code,
                "has_navigation": any(tag in generated_code.lower() for tag in ['<nav', '<header', 'navigation']),
                "has_menu_section": any(word in generated_code.lower() for word in ['menu', 'coffee', 'drinks']),
                "has_contact_form": any(tag in generated_code.lower() for tag in ['<form', 'contact', 'email']),
                "has_location": any(word in generated_code.lower() for word in ['location', 'address', 'map']),
                "responsive_design": 'viewport' in generated_code and ('responsive' in generated_code.lower() or '@media' in generated_code),
                "modern_css": any(feature in generated_code.lower() for feature in ['flexbox', 'grid', 'transform', 'transition'])
            }
            
            html_length = len(generated_code)
            quality_score = sum(quality_metrics.values()) / len(quality_metrics) * 100
            
            print(f"✅ Build verification complete")
            print(f"   HTML Length: {html_length:,} characters")
            print(f"   Quality Score: {quality_score:.1f}%")
            print(f"   Quality Metrics:")
            for metric, passed in quality_metrics.items():
                status = "✅" if passed else "❌"
                print(f"     {status} {metric.replace('_', ' ').title()}: {passed}")
            
            success = quality_score >= 60  # At least 60% quality
            self.log_test("Build Quality Verification", success, f"Quality: {quality_score:.1f}%, Length: {html_length}")
            
            return {
                "success": success,
                "html_length": html_length,
                "quality_score": quality_score,
                "quality_metrics": quality_metrics,
                "generated_code": generated_code[:500] + "..." if len(generated_code) > 500 else generated_code
            }
            
        except Exception as e:
            self.log_test("Build Quality Verification", False, str(e))
            return {"success": False, "error": str(e)}
    
    def verify_credit_deduction(self) -> Dict:
        """Verify accurate credit deduction"""
        print(f"\n💳 Verifying credit deduction...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Get current user data
            response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user data: {response.status_code}")
            
            current_user = response.json()
            current_credits = current_user['credits']
            initial_credits = self.user_data['credits']
            
            credits_used = initial_credits - current_credits
            
            print(f"✅ Credit verification:")
            print(f"   Initial Credits: {initial_credits}")
            print(f"   Current Credits: {current_credits}")
            print(f"   Credits Used: {credits_used}")
            
            # Expected range for multi-model build (30-60 credits)
            expected_min = 30
            expected_max = 60
            
            accurate_deduction = expected_min <= credits_used <= expected_max
            
            if accurate_deduction:
                print(f"   ✅ Credit deduction within expected range ({expected_min}-{expected_max})")
            else:
                print(f"   ⚠️  Credit deduction outside expected range ({expected_min}-{expected_max})")
            
            self.log_test("Credit Deduction Accuracy", accurate_deduction, f"Used: {credits_used} (expected: {expected_min}-{expected_max})")
            
            return {
                "success": True,
                "initial_credits": initial_credits,
                "current_credits": current_credits,
                "credits_used": credits_used,
                "accurate_deduction": accurate_deduction
            }
            
        except Exception as e:
            self.log_test("Credit Deduction Accuracy", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_model_router_endpoints(self) -> Dict:
        """Test if model router endpoints are accessible"""
        print(f"\n🎯 Testing model router system...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test health endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=30)
            health_status = response.status_code == 200
            
            if health_status:
                health_data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {health_data.get('status', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
            
            self.log_test("Health Check", health_status)
            
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            health_status = False
        
        # Test models endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/models", timeout=30)
            models_status = response.status_code == 200
            
            if models_status:
                models_data = response.json()
                print(f"✅ Models endpoint accessible")
                print(f"   Available models: {len(models_data)}")
                
                # Check for expected models
                model_names = list(models_data.keys()) if isinstance(models_data, dict) else []
                expected_models = ['claude-4.5-sonnet-200k', 'gpt-5', 'claude-4-sonnet-20250514']
                
                models_found = sum(1 for model in expected_models if any(model in name for name in model_names))
                print(f"   Expected models found: {models_found}/{len(expected_models)}")
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
            
            self.log_test("Models Endpoint", models_status)
            
        except Exception as e:
            self.log_test("Models Endpoint", False, str(e))
            models_status = False
        
        return {
            "success": health_status and models_status,
            "health_status": health_status,
            "models_status": models_status
        }
    
    def run_comprehensive_test(self) -> Dict:
        """Run complete multi-model router system test"""
        print(f"\n🧪 MULTI-MODEL ROUTER SYSTEM COMPREHENSIVE TEST")
        print(f"=" * 60)
        print(f"Testing intelligent task routing:")
        print(f"  • Claude Sonnet 4 → Frontend/UI generation")
        print(f"  • GPT-4o → Backend logic")
        print(f"  • Gemini 2.5 Pro → Content generation")
        print(f"  • OpenAI gpt-image-1 → HD image generation")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "authentication": {},
            "project_creation": {},
            "model_router_endpoints": {},
            "build_execution": {},
            "build_verification": {},
            "credit_verification": {},
            "overall_success": False
        }
        
        try:
            # Step 1: Authentication
            auth_result = self.authenticate_demo_account()
            results["authentication"] = auth_result
            
            if not auth_result["success"]:
                return results
            
            # Step 2: Project Creation
            project_result = self.create_test_project()
            results["project_creation"] = project_result
            
            if not project_result["success"]:
                return results
            
            # Step 3: Model Router Endpoints
            router_result = self.test_model_router_endpoints()
            results["model_router_endpoints"] = router_result
            
            # Step 4: Multi-Model Build Execution
            build_result = self.start_multi_model_build()
            results["build_execution"] = build_result
            
            if not build_result["success"]:
                return results
            
            # Step 5: Build Verification
            verification_result = self.verify_build_completion()
            results["build_verification"] = verification_result
            
            # Step 6: Credit Verification
            credit_result = self.verify_credit_deduction()
            results["credit_verification"] = credit_result
            
            # Calculate overall success
            success_criteria = [
                auth_result.get("success", False),
                project_result.get("success", False),
                router_result.get("success", False),
                build_result.get("success", False),
                verification_result.get("success", False),
                credit_result.get("accurate_deduction", False)
            ]
            
            results["overall_success"] = all(success_criteria)
            results["success_rate"] = sum(success_criteria) / len(success_criteria) * 100
            
            return results
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {str(e)}")
            results["error"] = str(e)
            return results
        
        finally:
            results["test_end_time"] = datetime.now().isoformat()
            results["test_results"] = self.test_results

def main():
    """Main test execution"""
    print(f"🚀 AutoWebIQ Multi-Model Router System Test")
    
    tester = MultiModelRouterTester()
    results = tester.run_comprehensive_test()
    
    # Print final summary
    print(f"\n" + "=" * 60)
    print(f"🏁 MULTI-MODEL ROUTER TEST SUMMARY")
    print(f"=" * 60)
    
    print(f"Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
    print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
    
    print(f"\n📊 Test Results:")
    print(f"  Authentication: {'✅' if results['authentication'].get('success') else '❌'}")
    print(f"  Project Creation: {'✅' if results['project_creation'].get('success') else '❌'}")
    print(f"  Model Router Endpoints: {'✅' if results['model_router_endpoints'].get('success') else '❌'}")
    print(f"  Build Execution: {'✅' if results['build_execution'].get('success') else '❌'}")
    print(f"  Build Quality: {'✅' if results['build_verification'].get('success') else '❌'}")
    print(f"  Credit Deduction: {'✅' if results['credit_verification'].get('accurate_deduction') else '❌'}")
    
    if results.get('build_execution', {}).get('success'):
        build_data = results['build_execution']
        models_detected = build_data.get('models_detected', 0)
        print(f"\n🎯 Multi-Model Detection:")
        print(f"  Models Detected in Response: {models_detected}/4")
        
        indicators = build_data.get('model_indicators', {})
        print(f"  Claude/Sonnet: {'✅' if indicators.get('claude_mentioned') else '❌'}")
        print(f"  GPT/OpenAI: {'✅' if indicators.get('gpt_mentioned') else '❌'}")
        print(f"  Gemini: {'✅' if indicators.get('gemini_mentioned') else '❌'}")
        print(f"  Image Generation: {'✅' if indicators.get('image_generation') else '❌'}")
    
    if results.get('build_verification', {}).get('success'):
        quality = results['build_verification']
        print(f"\n📈 Build Quality Metrics:")
        print(f"  HTML Length: {quality.get('html_length', 0):,} characters")
        print(f"  Quality Score: {quality.get('quality_score', 0):.1f}%")
    
    if results.get('credit_verification', {}).get('success'):
        credits = results['credit_verification']
        print(f"\n💳 Credit Usage:")
        print(f"  Credits Used: {credits.get('credits_used', 0)}")
        print(f"  Remaining: {credits.get('current_credits', 0)}")
    
    # Print detailed test results
    print(f"\n📋 Detailed Test Results:")
    for i, test in enumerate(tester.test_results, 1):
        status = "✅" if test['success'] else "❌"
        print(f"  {i:2d}. {status} {test['test']}")
        if test['details'] and not test['success']:
            print(f"      Details: {test['details']}")
    
    # Return exit code based on success
    return 0 if results['overall_success'] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)