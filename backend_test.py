import requests
import sys
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
import os

class AutoWebIQAPITester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://webbuilder-ai-3.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.jwt_token = None
        self.session_token = None
        self.user_id = None
        self.test_user_email = None
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
                response = requests.get(url, headers=default_headers, cookies=cookies)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, cookies=cookies)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, cookies=cookies)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, cookies=cookies)

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

    def test_user_registration(self):
        """Test user registration"""
        timestamp = int(time.time())
        test_username = f"testuser_{timestamp}"
        test_password = "TestPass123!"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"username": test_username, "password": test_password}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            self.username = test_username
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.username:
            return False
            
        success, response = self.run_test(
            "User Login",
            "POST", 
            "auth/login",
            200,
            data={"username": self.username, "password": "TestPass123!"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_user_profile(self):
        """Test getting user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_conversation(self):
        """Test creating a new conversation"""
        success, response = self.run_test(
            "Create Conversation",
            "POST",
            "conversations",
            200,
            data={"title": "Test Conversation"}
        )
        
        if success and 'id' in response:
            self.conversation_id = response['id']
            return True
        return False

    def test_get_conversations(self):
        """Test getting all conversations"""
        success, response = self.run_test(
            "Get Conversations",
            "GET",
            "conversations",
            200
        )
        return success

    def test_get_conversation_details(self):
        """Test getting specific conversation details"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        success, response = self.run_test(
            "Get Conversation Details",
            "GET",
            f"conversations/{self.conversation_id}",
            200
        )
        return success

    def test_update_conversation_title(self):
        """Test updating conversation title"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        success, response = self.run_test(
            "Update Conversation Title",
            "PUT",
            f"conversations/{self.conversation_id}",
            200,
            data={"title": "Updated Test Conversation"}
        )
        return success

    def test_send_message(self):
        """Test sending a message and getting AI response"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        print("   Note: AI response may take a few seconds...")
        success, response = self.run_test(
            "Send Message (AI Response)",
            "POST",
            "messages",
            200,
            data={
                "conversation_id": self.conversation_id,
                "content": "Hello, this is a test message. Please respond briefly."
            }
        )
        
        if success:
            # Check if we got both user and AI messages
            if 'user_message' in response and 'ai_message' in response:
                print("   ✅ Received both user and AI messages")
                return True
            else:
                self.log_test("Send Message - Response Format", False, "Missing user_message or ai_message in response")
                return False
        return False

    def test_image_generation(self):
        """Test image generation"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        print("   Note: Image generation may take several seconds...")
        success, response = self.run_test(
            "Generate Image",
            "POST",
            "generate-image",
            200,
            data={
                "conversation_id": self.conversation_id,
                "prompt": "A simple blue circle on white background"
            }
        )
        
        if success and 'image_base64' in response:
            print("   ✅ Image generated successfully")
            return True
        return False

    def test_file_upload(self):
        """Test file upload and analysis"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        # Create a test file
        test_content = "This is a test file for AI analysis.\nIt contains some sample text for testing purposes."
        
        print("   Note: File analysis may take a few seconds...")
        success, response = self.run_test(
            "File Upload and Analysis",
            "POST",
            f"upload-file?conversation_id={self.conversation_id}",
            200,
            files={'file': ('test.txt', test_content, 'text/plain')}
        )
        
        if success and 'analysis' in response:
            print("   ✅ File uploaded and analyzed successfully")
            return True
        return False

    def test_delete_conversation(self):
        """Test deleting a conversation"""
        if not hasattr(self, 'conversation_id'):
            return False
            
        success, response = self.run_test(
            "Delete Conversation",
            "DELETE",
            f"conversations/{self.conversation_id}",
            200
        )
        return success

    def test_invalid_auth(self):
        """Test API with invalid authentication"""
        original_token = self.token
        self.token = "invalid_token_123"
        
        success, response = self.run_test(
            "Invalid Authentication",
            "GET",
            "conversations",
            401
        )
        
        self.token = original_token
        return success

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting AI Assistant API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Authentication tests
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False

        if not self.test_user_login():
            print("❌ Login failed, stopping tests")
            return False

        self.test_get_user_profile()

        # Conversation tests
        if not self.test_create_conversation():
            print("❌ Conversation creation failed, stopping tests")
            return False

        self.test_get_conversations()
        self.test_get_conversation_details()
        self.test_update_conversation_title()

        # Message and AI tests
        self.test_send_message()
        
        # AI feature tests (may take longer)
        self.test_image_generation()
        self.test_file_upload()

        # Cleanup and security tests
        self.test_delete_conversation()
        self.test_invalid_auth()

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AIAssistantAPITester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())