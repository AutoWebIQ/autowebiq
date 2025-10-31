#!/usr/bin/env python3

import requests
import time
import json

def test_v2_detailed():
    """Detailed test of V2 system to check result structure"""
    
    base_url = "https://autowebiq-dev-1.preview.emergentagent.com/api"
    
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
    
    # Create project via V2 API
    project_response = requests.post(f"{base_url}/v2/projects", 
        headers=headers,
        json={
            "name": "V2 Detailed Test",
            "description": "Testing V2 result structure"
        }
    )
    
    if project_response.status_code != 200:
        print(f"❌ Project creation failed: {project_response.status_code}")
        return False
    
    project_id = project_response.json()['id']
    print(f"✅ Project created: {project_id}")
    
    # Start async build
    build_response = requests.post(f"{base_url}/v2/projects/{project_id}/build",
        headers=headers,
        json={
            "prompt": "Create a modern SaaS landing page with pricing and features",
            "uploaded_images": []
        }
    )
    
    if build_response.status_code != 200:
        print(f"❌ Build start failed: {build_response.status_code}")
        return False
    
    task_id = build_response.json()['task_id']
    print(f"✅ Build started: {task_id}")
    
    # Wait for completion and get detailed result
    max_checks = 30
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
                print("\n🎉 Build Completed Successfully!")
                print(f"📋 Result Keys: {list(result.keys())}")
                
                # Check each component
                if 'plan' in result:
                    plan = result['plan']
                    print(f"📝 Plan: {plan.get('project_name', 'N/A')} using template {plan.get('template_used', 'N/A')}")
                
                if 'frontend_code' in result:
                    frontend_code = result['frontend_code']
                    print(f"🎨 Frontend Code: {len(frontend_code)} characters")
                    if len(frontend_code) > 5000:
                        print("✅ HTML Quality: High (>5000 chars)")
                    else:
                        print("⚠️ HTML Quality: Moderate")
                
                if 'images' in result:
                    images = result['images']
                    print(f"🖼️ Images Generated: {len(images)}")
                
                if 'build_time' in result:
                    build_time = result['build_time']
                    print(f"⏱️ Build Time: {build_time:.1f}s")
                
                # Check credits deducted
                credits_response = requests.get(f"{base_url}/v2/user/credits", headers=headers)
                if credits_response.status_code == 200:
                    final_credits = credits_response.json()['credits']
                    print(f"💰 Credits Remaining: {final_credits}")
                
                return True
                
            elif status == 'FAILURE':
                error = status_data.get('error', 'Unknown error')
                print(f"❌ Build Failed: {error}")
                return False
                
        else:
            print(f"❌ Status check failed: {status_response.status_code}")
            return False
    
    print("❌ Build timed out")
    return False

if __name__ == "__main__":
    success = test_v2_detailed()
    if success:
        print("\n🎉 V2 Detailed Test: PASSED")
    else:
        print("\n💥 V2 Detailed Test: FAILED")