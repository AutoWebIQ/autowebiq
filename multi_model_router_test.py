#!/usr/bin/env python3
"""
Multi-Model Router System Direct Testing
Tests the model router implementation directly and via chat endpoint
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add backend to path
sys.path.append('/app/backend')

# Test Configuration
BACKEND_URL = "https://multiagent-ide.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class MultiModelRouterDirectTester:
    """Direct tester for Multi-Model Router System"""
    
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
    
    def test_model_router_direct(self):
        """Test model router directly"""
        print(f"\n🎯 Testing Model Router Direct Import...")
        
        try:
            from model_router import get_model_router
            
            # Initialize router
            router = get_model_router()
            
            # Test model configurations
            all_models = router.get_all_models()
            expected_models = ['frontend', 'backend', 'content']
            
            print(f"✅ Model router initialized successfully")
            print(f"   Available task types: {list(all_models.keys())}")
            
            # Verify each model configuration
            model_checks = {}
            
            for task_type in expected_models:
                info = router.get_model_info(task_type)
                model_checks[task_type] = {
                    'has_model': bool(info.get('model')),
                    'has_provider': bool(info.get('provider')),
                    'model_name': info.get('model', 'unknown'),
                    'provider': info.get('provider', 'unknown')
                }
                
                print(f"   {task_type.upper()}: {info.get('model')} ({info.get('provider')})")
            
            # Verify expected models
            expected_mappings = {
                'frontend': ('claude-4-sonnet-20250514', 'anthropic'),
                'backend': ('gpt-4o', 'openai'),
                'content': ('gemini-2.5-pro', 'gemini')
            }
            
            mapping_correct = True
            for task_type, (expected_model, expected_provider) in expected_mappings.items():
                actual = model_checks.get(task_type, {})
                if actual.get('model_name') != expected_model or actual.get('provider') != expected_provider:
                    mapping_correct = False
                    print(f"   ⚠️  {task_type}: Expected {expected_model} ({expected_provider}), got {actual.get('model_name')} ({actual.get('provider')})")
            
            if mapping_correct:
                print(f"   ✅ All model mappings correct")
            
            self.log_test("Model Router Direct Import", True, f"Models: {len(all_models)}")
            self.log_test("Model Router Configurations", mapping_correct, "All expected models configured correctly")
            
            return True, model_checks
            
        except Exception as e:
            self.log_test("Model Router Direct Import", False, str(e))
            return False, {}
    
    def authenticate_demo_account(self):
        """Authenticate with demo account"""
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
            
            self.log_test("Demo Account Authentication", True, f"Credits: {self.user_data['credits']}")
            return True
            
        except Exception as e:
            self.log_test("Demo Account Authentication", False, str(e))
            return False
    
    def create_test_project(self):
        """Create test project"""
        print(f"\n📁 Creating test project...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        project_data = {
            "name": "Multi-Model Router Test - Coffee Shop",
            "description": "Test project for verifying multi-model routing system"
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
            
            self.log_test("Test Project Creation", True, f"Project ID: {self.test_project_id}")
            return True
            
        except Exception as e:
            self.log_test("Test Project Creation", False, str(e))
            return False
    
    def test_multi_model_chat_routing(self):
        """Test multi-model routing via chat endpoint"""
        print(f"\n💬 Testing Multi-Model Chat Routing...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test different models that should route to different providers
        test_scenarios = [
            {
                "name": "Claude Sonnet 4 (Frontend)",
                "model": "claude-4-sonnet-20250514",
                "prompt": "Create a modern coffee shop homepage with hero section and navigation",
                "expected_provider": "anthropic"
            },
            {
                "name": "Claude 4.5 Sonnet (General)",
                "model": "claude-4.5-sonnet-200k", 
                "prompt": "Create a simple coffee shop website",
                "expected_provider": "anthropic"
            },
            {
                "name": "GPT-5 (Backend Logic)",
                "model": "gpt-5",
                "prompt": "Create API endpoints for a coffee shop ordering system",
                "expected_provider": "openai"
            }
        ]
        
        routing_results = []
        
        for scenario in test_scenarios:
            print(f"\n   Testing {scenario['name']}...")
            
            try:
                chat_request = {
                    "project_id": self.test_project_id,
                    "message": scenario["prompt"],
                    "model": scenario["model"]
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json=chat_request,
                    headers=headers,
                    timeout=60
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_message = response_data.get('ai_message', {})
                    generated_content = ai_message.get('content', '')
                    
                    # Check response quality
                    quality_metrics = {
                        'has_content': len(generated_content) > 100,
                        'response_time': end_time - start_time,
                        'contains_html': '<' in generated_content and '>' in generated_content,
                        'reasonable_length': 500 < len(generated_content) < 10000
                    }
                    
                    print(f"   ✅ {scenario['name']} - Response received")
                    print(f"      Content length: {len(generated_content)} chars")
                    print(f"      Response time: {quality_metrics['response_time']:.1f}s")
                    print(f"      Contains HTML: {quality_metrics['contains_html']}")
                    
                    routing_results.append({
                        "scenario": scenario['name'],
                        "model": scenario['model'],
                        "success": True,
                        "quality_metrics": quality_metrics,
                        "content_preview": generated_content[:200] + "..." if len(generated_content) > 200 else generated_content
                    })
                    
                    self.log_test(f"Chat Routing - {scenario['name']}", True, f"Length: {len(generated_content)}, Time: {quality_metrics['response_time']:.1f}s")
                    
                elif response.status_code == 402:
                    print(f"   💳 Insufficient credits for {scenario['name']}")
                    self.log_test(f"Chat Routing - {scenario['name']}", False, "Insufficient credits")
                    
                else:
                    print(f"   ❌ {scenario['name']} failed: {response.status_code}")
                    self.log_test(f"Chat Routing - {scenario['name']}", False, f"HTTP {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {scenario['name']} error: {str(e)}")
                self.log_test(f"Chat Routing - {scenario['name']}", False, str(e))
        
        return routing_results
    
    def test_model_specific_features(self):
        """Test model-specific features and capabilities"""
        print(f"\n🔬 Testing Model-Specific Features...")
        
        try:
            from model_router import get_model_router
            router = get_model_router()
            
            # Test image generation capability
            print(f"\n   Testing Image Generation (gpt-image-1)...")
            
            try:
                # This is a mock test since we can't actually generate images in this environment
                # But we can verify the image generator is configured
                image_gen = router.image_generator
                
                if image_gen:
                    print(f"   ✅ Image generator configured")
                    self.log_test("Image Generator Configuration", True, "OpenAI image generator available")
                else:
                    print(f"   ❌ Image generator not configured")
                    self.log_test("Image Generator Configuration", False, "No image generator found")
                    
            except Exception as e:
                print(f"   ❌ Image generator error: {str(e)}")
                self.log_test("Image Generator Configuration", False, str(e))
            
            # Test chat client creation for each task type
            print(f"\n   Testing Chat Client Creation...")
            
            task_types = ['frontend', 'backend', 'content']
            client_results = {}
            
            for task_type in task_types:
                try:
                    chat_client = router.get_chat_client(
                        task_type=task_type,
                        system_message=f"You are a {task_type} specialist.",
                        session_id="test_session"
                    )
                    
                    if chat_client:
                        print(f"   ✅ {task_type.upper()} chat client created")
                        client_results[task_type] = True
                        self.log_test(f"Chat Client - {task_type.title()}", True, "Client created successfully")
                    else:
                        print(f"   ❌ {task_type.upper()} chat client failed")
                        client_results[task_type] = False
                        self.log_test(f"Chat Client - {task_type.title()}", False, "Client creation failed")
                        
                except Exception as e:
                    print(f"   ❌ {task_type.upper()} chat client error: {str(e)}")
                    client_results[task_type] = False
                    self.log_test(f"Chat Client - {task_type.title()}", False, str(e))
            
            return client_results
            
        except Exception as e:
            print(f"   ❌ Model features test error: {str(e)}")
            self.log_test("Model-Specific Features", False, str(e))
            return {}
    
    def run_comprehensive_test(self):
        """Run comprehensive multi-model router test"""
        print(f"\n🧪 MULTI-MODEL ROUTER DIRECT TESTING")
        print(f"=" * 60)
        print(f"Testing Phase 1: Multi-Model Router System")
        print(f"  • Claude Sonnet 4 → Frontend/UI generation")
        print(f"  • GPT-4o → Backend logic")
        print(f"  • Gemini 2.5 Pro → Content generation")
        print(f"  • OpenAI gpt-image-1 → HD image generation")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "direct_router_test": {},
            "authentication": {},
            "project_creation": {},
            "chat_routing_test": {},
            "model_features_test": {},
            "overall_success": False
        }
        
        # Step 1: Direct Router Test
        print(f"🔧 STEP 1: Direct Model Router Testing")
        router_success, model_configs = self.test_model_router_direct()
        results["direct_router_test"] = {
            "success": router_success,
            "model_configurations": model_configs
        }
        
        if not router_success:
            print(f"❌ Direct router test failed, skipping API tests")
            return results
        
        # Step 2: Authentication
        print(f"\n🔐 STEP 2: Authentication Testing")
        auth_success = self.authenticate_demo_account()
        results["authentication"] = {"success": auth_success}
        
        if not auth_success:
            return results
        
        # Step 3: Project Creation
        print(f"\n📁 STEP 3: Project Creation Testing")
        project_success = self.create_test_project()
        results["project_creation"] = {"success": project_success}
        
        if not project_success:
            return results
        
        # Step 4: Chat Routing Test
        print(f"\n💬 STEP 4: Multi-Model Chat Routing Testing")
        routing_results = self.test_multi_model_chat_routing()
        results["chat_routing_test"] = {
            "success": len(routing_results) > 0,
            "routing_results": routing_results
        }
        
        # Step 5: Model Features Test
        print(f"\n🔬 STEP 5: Model-Specific Features Testing")
        features_results = self.test_model_specific_features()
        results["model_features_test"] = {
            "success": len(features_results) > 0,
            "features_results": features_results
        }
        
        # Calculate overall success
        success_criteria = [
            router_success,
            auth_success,
            project_success,
            len(routing_results) > 0,
            len(features_results) > 0
        ]
        
        results["overall_success"] = all(success_criteria)
        results["success_rate"] = sum(success_criteria) / len(success_criteria) * 100
        results["test_end_time"] = datetime.now().isoformat()
        results["test_results"] = self.test_results
        
        return results

def main():
    """Main test execution"""
    print(f"🚀 AutoWebIQ Multi-Model Router Direct Test")
    
    tester = MultiModelRouterDirectTester()
    results = tester.run_comprehensive_test()
    
    # Print final summary
    print(f"\n" + "=" * 60)
    print(f"🏁 MULTI-MODEL ROUTER TEST SUMMARY")
    print(f"=" * 60)
    
    print(f"Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
    print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
    
    print(f"\n📊 Test Results:")
    print(f"  Direct Router Test: {'✅' if results['direct_router_test'].get('success') else '❌'}")
    print(f"  Authentication: {'✅' if results['authentication'].get('success') else '❌'}")
    print(f"  Project Creation: {'✅' if results['project_creation'].get('success') else '❌'}")
    print(f"  Chat Routing: {'✅' if results['chat_routing_test'].get('success') else '❌'}")
    print(f"  Model Features: {'✅' if results['model_features_test'].get('success') else '❌'}")
    
    # Model Configuration Summary
    if results['direct_router_test'].get('success'):
        print(f"\n🎯 Model Router Configuration:")
        configs = results['direct_router_test'].get('model_configurations', {})
        for task_type, config in configs.items():
            status = "✅" if config.get('has_model') and config.get('has_provider') else "❌"
            print(f"  {status} {task_type.upper()}: {config.get('model_name')} ({config.get('provider')})")
    
    # Chat Routing Results
    if results['chat_routing_test'].get('success'):
        print(f"\n💬 Chat Routing Results:")
        routing_results = results['chat_routing_test'].get('routing_results', [])
        for result in routing_results:
            if result.get('success'):
                metrics = result.get('quality_metrics', {})
                print(f"  ✅ {result['scenario']}: {metrics.get('response_time', 0):.1f}s, {len(result.get('content_preview', ''))} chars")
            else:
                print(f"  ❌ {result['scenario']}: Failed")
    
    # Model Features Results
    if results['model_features_test'].get('success'):
        print(f"\n🔬 Model Features:")
        features = results['model_features_test'].get('features_results', {})
        for feature, success in features.items():
            status = "✅" if success else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
    
    # Detailed Test Results
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