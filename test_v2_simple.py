#!/usr/bin/env python3

import requests
import time
import json

def test_v2_system():
    """Simple test of V2 system as requested in review"""
    
    base_url = "https://autowebiq-1.preview.emergentagent.com/api"
    
    # Login with demo account
    print("🔐 Logging in with demo account...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "demo@test.com",
        "password": "Demo123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test V2 user endpoints
    print("\n📊 Testing V2 User Endpoints...")
    
    # Get user info
    user_response = requests.get(f"{base_url}/v2/user/me", headers=headers)
    if user_response.status_code == 200:
        print("✅ V2 User Info: Working")
    else:
        print(f"❌ V2 User Info: {user_response.status_code}")
        return False
    
    # Get credits
    credits_response = requests.get(f"{base_url}/v2/user/credits", headers=headers)
    if credits_response.status_code == 200:
        credits = credits_response.json()['credits']
        print(f"✅ V2 User Credits: {credits} available")
    else:
        print(f"❌ V2 User Credits: {credits_response.status_code}")
        return False
    
    # Create project via V2 API
    print("\n📁 Testing V2 Project Management...")
    
    project_response = requests.post(f"{base_url}/v2/projects", 
        headers=headers,
        json={
            "name": "V2 Test Project",
            "description": "Testing V2 async build system"
        }
    )
    
    if project_response.status_code == 200:
        project_id = project_response.json()['id']
        print(f"✅ V2 Project Created: {project_id}")
    else:
        print(f"❌ V2 Project Creation: {project_response.status_code}")
        return False
    
    # Start async build
    print("\n🚀 Testing V2 Async Build...")
    
    build_response = requests.post(f"{base_url}/v2/projects/{project_id}/build",
        headers=headers,
        json={
            "prompt": "Create a simple business landing page with hero section and contact form",
            "uploaded_images": []
        }
    )
    
    if build_response.status_code == 200:
        task_id = build_response.json()['task_id']
        print(f"✅ V2 Async Build Started: {task_id}")
    else:
        print(f"❌ V2 Async Build: {build_response.status_code} - {build_response.text}")
        return False
    
    # Check build status
    print("\n⏳ Checking Build Status...")
    
    max_checks = 24  # 2 minutes max (5 second intervals)
    for i in range(max_checks):
        time.sleep(5)
        
        status_response = requests.get(f"{base_url}/v2/projects/{project_id}/build/status/{task_id}",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get('status', 'UNKNOWN')
            print(f"   📊 Build Status: {status}")
            
            if status == 'SUCCESS':
                result = status_data.get('result', {})
                print("✅ Build Completed Successfully!")
                print(f"   📝 Generated HTML: {len(result.get('frontend_code', ''))} characters")
                return True
            elif status == 'FAILURE':
                error = status_data.get('error', 'Unknown error')
                print(f"❌ Build Failed: {error}")
                return False
            elif status in ['PENDING', 'PROGRESS']:
                continue
        else:
            print(f"❌ Status Check Failed: {status_response.status_code}")
            return False
    
    print("❌ Build timed out after 2 minutes")
    return False

if __name__ == "__main__":
    success = test_v2_system()
    if success:
        print("\n🎉 V2 System Test: PASSED")
    else:
        print("\n💥 V2 System Test: FAILED")