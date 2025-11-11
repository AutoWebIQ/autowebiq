#!/usr/bin/env python3
"""
NEW USER FEATURES TESTING - Fork, Share, Download, GitHub
Tests the newly implemented Emergent-like features in AutoWebIQ:
- POST /api/projects/{project_id}/fork - Fork/clone a project
- POST /api/projects/{project_id}/share - Generate public share link
- GET /api/public/{share_token} - View public project (NO auth required)
- GET /api/projects/{project_id}/download - Download project as ZIP
- GET /api/github/user-info - GitHub integration check
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Test Configuration
BACKEND_URL = "https://aiweb-builder-2.preview.emergentagent.com/api"

# Demo Account Credentials
DEMO_EMAIL = "demo@test.com"
DEMO_PASSWORD = "Demo123456"

class NewFeaturesTester:
    """Tester for NEW user features - Fork, Share, Download, GitHub"""
    
    def __init__(self):
        self.auth_token = None
        self.user_data = None
        self.test_project_id = None
        self.share_token = None
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = "", status_code: int = None):
        """Log test result with enhanced details"""
        status_emoji = "✅" if success else "❌"
        status_text = f" ({status_code})" if status_code else ""
        
        print(f"{status_emoji} {name}{status_text}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "status_code": status_code
        })
    
    def authenticate_demo_account(self) -> Dict:
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
            
            self.log_test("Demo Account Login", True, f"User ID: {self.user_data['id']}, Credits: {self.user_data['credits']}", 200)
            
            return {"success": True, "user_id": self.user_data['id'], "credits": self.user_data['credits']}
            
        except Exception as e:
            self.log_test("Demo Account Login", False, str(e))
            return {"success": False, "error": str(e)}
    
    def get_projects_list(self) -> Dict:
        """Get list of projects to find a project_id for testing"""
        print(f"\n📁 Getting projects list...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{BACKEND_URL}/projects", headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get projects: {response.status_code} - {response.text}")
            
            projects_data = response.json()
            projects = projects_data.get('projects', [])
            
            if not projects:
                # Create a test project if none exist
                print("   No projects found, creating test project...")
                return self.create_test_project()
            
            # Use the first project
            project = projects[0]
            self.test_project_id = project['id']
            
            print(f"✅ Found {len(projects)} projects")
            print(f"   Using project: {project['name']} (ID: {self.test_project_id})")
            
            self.log_test("Get Projects List", True, f"Found {len(projects)} projects, using: {project['name']}", 200)
            
            return {
                "success": True,
                "project_id": self.test_project_id,
                "project_name": project['name'],
                "total_projects": len(projects)
            }
            
        except Exception as e:
            self.log_test("Get Projects List", False, str(e))
            return {"success": False, "error": str(e)}
    
    def create_test_project(self) -> Dict:
        """Create a test project if needed"""
        print(f"   Creating test project for fork/share testing...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        project_data = {
            "name": "Test Project for Fork/Share",
            "description": "Test project created for testing fork, share, and download features"
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
            
            print(f"   ✅ Test project created: {project['name']}")
            
            return {
                "success": True,
                "project_id": self.test_project_id,
                "project_name": project['name']
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_fork_project(self) -> Dict:
        """Test POST /api/projects/{project_id}/fork"""
        print(f"\n🍴 Testing Fork Project Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/projects/{self.test_project_id}/fork",
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                fork_data = response.json()
                new_project_id = fork_data.get('project_id')
                new_project_name = fork_data.get('project_name')
                
                print(f"✅ Fork successful")
                print(f"   New Project ID: {new_project_id}")
                print(f"   New Project Name: {new_project_name}")
                
                # Verify new project appears in projects list
                projects_response = requests.get(f"{BACKEND_URL}/projects", headers=headers, timeout=30)
                if projects_response.status_code == 200:
                    projects = projects_response.json().get('projects', [])
                    forked_project_exists = any(p['id'] == new_project_id for p in projects)
                    
                    if forked_project_exists:
                        print(f"   ✅ Forked project verified in projects list")
                    else:
                        print(f"   ⚠️  Forked project not found in projects list")
                
                self.log_test("POST /api/projects/{project_id}/fork", True, 
                             f"New project created: {new_project_name} (ID: {new_project_id})", 200)
                
                return {
                    "success": True,
                    "new_project_id": new_project_id,
                    "new_project_name": new_project_name,
                    "response_data": fork_data
                }
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_test("POST /api/projects/{project_id}/fork", False, error_msg, response.status_code)
                
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except Exception as e:
            self.log_test("POST /api/projects/{project_id}/fork", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_share_project(self) -> Dict:
        """Test POST /api/projects/{project_id}/share"""
        print(f"\n🔗 Testing Share Project Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/projects/{self.test_project_id}/share",
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                share_data = response.json()
                self.share_token = share_data.get('share_token')
                share_url = share_data.get('share_url')
                
                print(f"✅ Share successful")
                print(f"   Share URL: {share_url}")
                print(f"   Share Token: {self.share_token}")
                
                self.log_test("POST /api/projects/{project_id}/share", True, 
                             f"Share URL: {share_url}, Token: {self.share_token}", 200)
                
                return {
                    "success": True,
                    "share_url": share_url,
                    "share_token": self.share_token,
                    "response_data": share_data
                }
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_test("POST /api/projects/{project_id}/share", False, error_msg, response.status_code)
                
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except Exception as e:
            self.log_test("POST /api/projects/{project_id}/share", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_public_project_view(self) -> Dict:
        """Test GET /api/public/{share_token} - NO auth required"""
        print(f"\n🌐 Testing Public Project View (NO AUTH)...")
        
        if not self.share_token:
            error_msg = "No share token available from previous test"
            self.log_test("GET /api/public/{share_token}", False, error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # NO Authorization header - this should be public
            response = requests.get(
                f"{BACKEND_URL}/public/{self.share_token}",
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                content = response.text
                content_type = response.headers.get('content-type', '')
                
                print(f"✅ Public view successful")
                print(f"   Content Type: {content_type}")
                print(f"   Content Length: {len(content)} characters")
                
                # Check if it's HTML content
                is_html = 'text/html' in content_type or content.strip().startswith('<')
                
                if is_html:
                    print(f"   ✅ Returns HTML content")
                else:
                    print(f"   ⚠️  Content may not be HTML")
                
                self.log_test("GET /api/public/{share_token}", True, 
                             f"Content-Type: {content_type}, Length: {len(content)} chars", 200)
                
                return {
                    "success": True,
                    "content_length": len(content),
                    "content_type": content_type,
                    "is_html": is_html
                }
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_test("GET /api/public/{share_token}", False, error_msg, response.status_code)
                
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except Exception as e:
            self.log_test("GET /api/public/{share_token}", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_download_project(self) -> Dict:
        """Test GET /api/projects/{project_id}/download"""
        print(f"\n📥 Testing Download Project Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/projects/{self.test_project_id}/download",
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                content_length = len(response.content)
                
                print(f"✅ Download successful")
                print(f"   Content Type: {content_type}")
                print(f"   Content Disposition: {content_disposition}")
                print(f"   File Size: {content_length} bytes")
                
                # Verify it's a ZIP file
                is_zip = 'application/zip' in content_type
                has_filename = 'filename=' in content_disposition
                
                if is_zip:
                    print(f"   ✅ Correct ZIP content type")
                else:
                    print(f"   ⚠️  Content type may not be ZIP")
                
                if has_filename:
                    print(f"   ✅ Filename in Content-Disposition header")
                else:
                    print(f"   ⚠️  No filename in Content-Disposition header")
                
                self.log_test("GET /api/projects/{project_id}/download", True, 
                             f"ZIP file: {content_length} bytes, Content-Type: {content_type}", 200)
                
                return {
                    "success": True,
                    "content_type": content_type,
                    "content_disposition": content_disposition,
                    "file_size": content_length,
                    "is_zip": is_zip,
                    "has_filename": has_filename
                }
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_test("GET /api/projects/{project_id}/download", False, error_msg, response.status_code)
                
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except Exception as e:
            self.log_test("GET /api/projects/{project_id}/download", False, str(e))
            return {"success": False, "error": str(e)}
    
    def test_github_endpoints(self) -> Dict:
        """Test GitHub endpoints - Quick check"""
        print(f"\n🐙 Testing GitHub Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/github/user-info",
                headers=headers,
                timeout=30
            )
            
            # GitHub endpoints should return 200 (if connected) or appropriate error
            success = response.status_code in [200, 400]  # 400 is expected if not connected
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ GitHub connected")
                print(f"   User info retrieved successfully")
                
                self.log_test("GET /api/github/user-info", True, "GitHub user connected", 200)
                
                return {
                    "success": True,
                    "connected": True,
                    "user_info": user_info
                }
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                error_msg = error_data.get('detail', 'GitHub not connected')
                
                print(f"✅ GitHub endpoint working (not connected)")
                print(f"   Error: {error_msg}")
                
                self.log_test("GET /api/github/user-info", True, f"Proper error handling: {error_msg}", 400)
                
                return {
                    "success": True,
                    "connected": False,
                    "error_message": error_msg
                }
            else:
                error_msg = f"Unexpected status {response.status_code}: {response.text}"
                self.log_test("GET /api/github/user-info", False, error_msg, response.status_code)
                
                return {"success": False, "error": error_msg, "status_code": response.status_code}
            
        except Exception as e:
            self.log_test("GET /api/github/user-info", False, str(e))
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_test(self) -> Dict:
        """Run complete NEW features test"""
        print(f"\n🧪 NEW USER FEATURES COMPREHENSIVE TEST")
        print(f"=" * 60)
        print(f"Testing Emergent-like features:")
        print(f"  • Fork/Clone Projects")
        print(f"  • Share Public Links")
        print(f"  • Download Projects as ZIP")
        print(f"  • GitHub Integration")
        print(f"")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "authentication": {},
            "projects_list": {},
            "fork_test": {},
            "share_test": {},
            "public_view_test": {},
            "download_test": {},
            "github_test": {},
            "overall_success": False
        }
        
        try:
            # Step 1: Authentication
            auth_result = self.authenticate_demo_account()
            results["authentication"] = auth_result
            
            if not auth_result["success"]:
                return results
            
            # Step 2: Get Projects List
            projects_result = self.get_projects_list()
            results["projects_list"] = projects_result
            
            if not projects_result["success"]:
                return results
            
            # Step 3: Test Fork Project
            fork_result = self.test_fork_project()
            results["fork_test"] = fork_result
            
            # Step 4: Test Share Project
            share_result = self.test_share_project()
            results["share_test"] = share_result
            
            # Step 5: Test Public View (only if share worked)
            if share_result.get("success"):
                public_result = self.test_public_project_view()
                results["public_view_test"] = public_result
            else:
                results["public_view_test"] = {"success": False, "error": "Share test failed"}
            
            # Step 6: Test Download Project
            download_result = self.test_download_project()
            results["download_test"] = download_result
            
            # Step 7: Test GitHub Endpoints
            github_result = self.test_github_endpoints()
            results["github_test"] = github_result
            
            # Calculate overall success
            success_criteria = [
                auth_result.get("success", False),
                projects_result.get("success", False),
                fork_result.get("success", False),
                share_result.get("success", False),
                results["public_view_test"].get("success", False),
                download_result.get("success", False),
                github_result.get("success", False)
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
    print(f"🚀 AutoWebIQ NEW User Features Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Demo Account: {DEMO_EMAIL}")
    
    tester = NewFeaturesTester()
    results = tester.run_comprehensive_test()
    
    # Print final summary
    print(f"\n" + "=" * 60)
    print(f"🏁 NEW FEATURES TEST SUMMARY")
    print(f"=" * 60)
    
    print(f"Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
    print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
    
    print(f"\n📊 Endpoint Test Results:")
    print(f"  1. Demo Account Login: {'✅' if results['authentication'].get('success') else '❌'}")
    print(f"  2. Get Projects List: {'✅' if results['projects_list'].get('success') else '❌'}")
    print(f"  3. POST /api/projects/{{id}}/fork: {'✅' if results['fork_test'].get('success') else '❌'}")
    print(f"  4. POST /api/projects/{{id}}/share: {'✅' if results['share_test'].get('success') else '❌'}")
    print(f"  5. GET /api/public/{{token}} (NO AUTH): {'✅' if results['public_view_test'].get('success') else '❌'}")
    print(f"  6. GET /api/projects/{{id}}/download: {'✅' if results['download_test'].get('success') else '❌'}")
    print(f"  7. GET /api/github/user-info: {'✅' if results['github_test'].get('success') else '❌'}")
    
    # Print key response details
    if results.get('fork_test', {}).get('success'):
        fork_data = results['fork_test']
        print(f"\n🍴 Fork Results:")
        print(f"  New Project: {fork_data.get('new_project_name')}")
        print(f"  New ID: {fork_data.get('new_project_id')}")
    
    if results.get('share_test', {}).get('success'):
        share_data = results['share_test']
        print(f"\n🔗 Share Results:")
        print(f"  Share URL: {share_data.get('share_url')}")
        print(f"  Share Token: {share_data.get('share_token')}")
    
    if results.get('public_view_test', {}).get('success'):
        public_data = results['public_view_test']
        print(f"\n🌐 Public View Results:")
        print(f"  Content Length: {public_data.get('content_length')} characters")
        print(f"  Is HTML: {'✅' if public_data.get('is_html') else '❌'}")
    
    if results.get('download_test', {}).get('success'):
        download_data = results['download_test']
        print(f"\n📥 Download Results:")
        print(f"  File Size: {download_data.get('file_size')} bytes")
        print(f"  Is ZIP: {'✅' if download_data.get('is_zip') else '❌'}")
        print(f"  Has Filename: {'✅' if download_data.get('has_filename') else '❌'}")
    
    if results.get('github_test', {}).get('success'):
        github_data = results['github_test']
        print(f"\n🐙 GitHub Results:")
        print(f"  Connected: {'✅' if github_data.get('connected') else '❌ (Expected - no token)'}")
    
    # Print any failures
    print(f"\n📋 Detailed Test Results:")
    for i, test in enumerate(tester.test_results, 1):
        status = "✅" if test['success'] else "❌"
        status_code = f" ({test['status_code']})" if test.get('status_code') else ""
        print(f"  {i:2d}. {status} {test['test']}{status_code}")
        if test['details'] and not test['success']:
            print(f"      Error: {test['details']}")
    
    # Return exit code based on success
    return 0 if results['overall_success'] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)