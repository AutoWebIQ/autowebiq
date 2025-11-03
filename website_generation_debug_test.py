#!/usr/bin/env python3
"""
WEBSITE GENERATION DEBUGGING TEST

Based on backend logs analysis, the issue is NOT with project creation,
but with website generation (sending messages to projects) which fails due to PostgreSQL connection errors.

The user workflow that fails:
1. Login with Google OAuth ✅ 
2. Create project ✅ 
3. Send message to generate website ❌ (PostgreSQL error)

This test will verify this diagnosis.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Production URL
BASE_URL = "https://autowebiq.com/api"

class WebsiteGenerationDebugger:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.project_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def setup_test_user_and_project(self):
        """Setup: Create user and project for testing"""
        self.log("🔧 Setting up test user and project...")
        
        # Create user
        test_user = {
            "username": f"gentest_{int(datetime.now().timestamp())}",
            "email": f"gentest_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPassword123!"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log("❌ Failed to create test user", "ERROR")
                    return False
                
                user_data = await response.json()
                self.auth_token = user_data.get('access_token')
                self.log(f"✅ User created: {user_data.get('user', {}).get('email')}")
                self.log(f"Credits: {user_data.get('user', {}).get('credits')}")
        
            # Create project
            project_data = {
                "name": "Website Generation Test Project",
                "description": "Testing website generation functionality"
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{BASE_URL}/projects/create",
                json=project_data,
                headers=headers
            ) as response:
                if response.status != 200:
                    self.log("❌ Failed to create test project", "ERROR")
                    return False
                
                project_response = await response.json()
                self.project_id = project_response.get('id')
                self.log(f"✅ Project created: {project_response.get('name')}")
                self.log(f"Project ID: {self.project_id}")
                
                return True
                
        except Exception as e:
            self.log(f"❌ Setup error: {str(e)}", "ERROR")
            return False
    
    async def test_project_messages_endpoint(self):
        """Test getting messages for a project (should work)"""
        self.log("📝 Testing project messages endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{BASE_URL}/projects/{self.project_id}/messages",
                headers=headers
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log(f"✅ Messages endpoint works - {len(data.get('messages', []))} messages")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ Messages endpoint failed: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Messages endpoint error: {str(e)}", "ERROR")
            return False
    
    async def test_website_generation_via_messages(self):
        """Test website generation by sending a message (this should fail with PostgreSQL error)"""
        self.log("🎯 MAIN TEST: Testing website generation via messages...")
        
        message_data = {
            "message": "Create a simple landing page for a coffee shop with a hero section and menu",
            "uploaded_images": []
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            self.log(f"Sending message to project: {self.project_id}")
            self.log(f"Message: {message_data['message']}")
            
            async with self.session.post(
                f"{BASE_URL}/projects/{self.project_id}/messages",
                json=message_data,
                headers=headers
            ) as response:
                status_code = response.status
                
                self.log(f"Response Status: {status_code}")
                
                try:
                    response_data = await response.json()
                    self.log(f"Response Data: {json.dumps(response_data, indent=2)}")
                except:
                    response_text = await response.text()
                    self.log(f"Response Text: {response_text}")
                    response_data = {"error": response_text}
                
                if status_code == 200:
                    # Check if the response contains an error message
                    message_content = response_data.get('message', {}).get('content', '')
                    
                    if 'error' in message_content.lower() or '❌' in message_content:
                        self.log("❌ WEBSITE GENERATION FAILED (as expected)", "ERROR")
                        self.log(f"Error in response: {message_content}", "ERROR")
                        return False, response_data
                    else:
                        self.log("✅ WEBSITE GENERATION SUCCESSFUL", "SUCCESS")
                        return True, response_data
                else:
                    self.log(f"❌ WEBSITE GENERATION REQUEST FAILED: Status {status_code}", "ERROR")
                    return False, response_data
                    
        except Exception as e:
            self.log(f"❌ Website generation error: {str(e)}", "ERROR")
            return False, {"error": str(e)}
    
    async def test_chat_endpoint_alternative(self):
        """Test the /chat endpoint as an alternative to messages"""
        self.log("💬 Testing /chat endpoint as alternative...")
        
        chat_data = {
            "project_id": self.project_id,
            "message": "Create a simple HTML page for a restaurant",
            "model": "claude-4.5-sonnet-200k"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{BASE_URL}/chat",
                json=chat_data,
                headers=headers
            ) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    self.log("✅ Chat endpoint works (uses different generation path)")
                    self.log(f"Generated code length: {len(data.get('code', ''))}")
                    return True
                else:
                    error_text = await response.text()
                    self.log(f"❌ Chat endpoint failed: {status_code} - {error_text}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Chat endpoint error: {str(e)}", "ERROR")
            return False
    
    async def test_build_with_agents_endpoint(self):
        """Test the /build-with-agents endpoint"""
        self.log("🤖 Testing /build-with-agents endpoint...")
        
        build_data = {
            "project_id": self.project_id,
            "prompt": "Create a modern landing page for a tech startup",
            "uploaded_images": []
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{BASE_URL}/build-with-agents",
                json=build_data,
                headers=headers
            ) as response:
                status_code = response.status
                response_text = await response.text()
                
                self.log(f"Build-with-agents Status: {status_code}")
                self.log(f"Response: {response_text[:500]}...")
                
                if status_code == 200:
                    self.log("✅ Build-with-agents endpoint accessible")
                    return True
                elif status_code == 402:
                    self.log("✅ Build-with-agents endpoint works (insufficient credits expected)")
                    return True
                else:
                    self.log(f"❌ Build-with-agents failed: {status_code}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Build-with-agents error: {str(e)}", "ERROR")
            return False
    
    async def run_website_generation_debug(self):
        """Run all website generation debugging tests"""
        self.log("🚀 Starting Website Generation Debugging", "INFO")
        self.log(f"Target URL: {BASE_URL}")
        self.log("=" * 60)
        
        # Setup
        if not await self.setup_test_user_and_project():
            self.log("❌ Failed to setup test environment", "ERROR")
            return {"setup": False}
        
        results = {}
        
        # Test 1: Project messages endpoint (should work)
        results['messages_endpoint'] = await self.test_project_messages_endpoint()
        
        # Test 2: Website generation via messages (main test - should fail)
        success, details = await self.test_website_generation_via_messages()
        results['website_generation'] = success
        results['generation_details'] = details
        
        # Test 3: Chat endpoint alternative
        results['chat_endpoint'] = await self.test_chat_endpoint_alternative()
        
        # Test 4: Build-with-agents endpoint
        results['build_agents'] = await self.test_build_with_agents_endpoint()
        
        # Summary
        self.log("=" * 60)
        self.log("🔍 WEBSITE GENERATION DEBUGGING SUMMARY", "INFO")
        self.log("=" * 60)
        
        for test_name, result in results.items():
            if test_name == 'generation_details':
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Analysis
        self.log("\n🎯 ROOT CAUSE ANALYSIS:", "INFO")
        
        if not results.get('website_generation', False):
            self.log("❌ CONFIRMED: Website generation is failing", "ERROR")
            
            # Analyze the error details
            details = results.get('generation_details', {})
            if details:
                error_msg = str(details)
                if 'postgresql' in error_msg.lower() or 'connect call failed' in error_msg.lower():
                    self.log("🔍 ROOT CAUSE: PostgreSQL connection failure", "ERROR")
                    self.log("💡 SOLUTION: The template system requires PostgreSQL but it's not available", "ERROR")
                    self.log("🔧 FIX NEEDED: Either setup PostgreSQL or fallback to MongoDB-only generation", "ERROR")
                else:
                    self.log(f"🔍 ERROR DETAILS: {error_msg}", "ERROR")
        else:
            self.log("✅ Website generation is working", "SUCCESS")
        
        # Check if alternatives work
        if results.get('chat_endpoint', False):
            self.log("✅ WORKAROUND: /chat endpoint works as alternative", "SUCCESS")
        
        return results

async def main():
    """Main function to run website generation debugging"""
    async with WebsiteGenerationDebugger() as debugger:
        results = await debugger.run_website_generation_debug()
        
        # Exit with error code if website generation failed
        if not results.get('website_generation', False):
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())