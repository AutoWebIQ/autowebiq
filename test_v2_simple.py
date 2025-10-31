import requests
import time
import json

def test_v2_simple():
    """Simple test of V2 system functionality"""
    
    base_url = "https://autowebiq-dev-1.preview.emergentagent.com"
    api_v2_url = f"{base_url}/api/v2"
    
    # Login with demo account
    print("🔐 Logging in with demo account...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "demo@test.com",
        "password": "Demo123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Login successful, credits: {login_response.json()['user']['credits']}")
    
    # Test V2 endpoints
    print("\n📊 Testing V2 endpoints...")
    
    # 1. Get user info
    user_response = requests.get(f"{api_v2_url}/user/me", headers=headers)
    print(f"GET /user/me: {user_response.status_code}")
    
    # 2. Get credits
    credits_response = requests.get(f"{api_v2_url}/user/credits", headers=headers)
    print(f"GET /user/credits: {credits_response.status_code}")
    if credits_response.status_code == 200:
        print(f"   Credits: {credits_response.json()['credits']}")
    
    # 3. Create project
    project_response = requests.post(f"{api_v2_url}/projects", 
        headers=headers,
        json={
            "name": "V2 Simple Test",
            "description": "Testing V2 system"
        }
    )
    print(f"POST /projects: {project_response.status_code}")
    
    if project_response.status_code != 200:
        print(f"❌ Project creation failed")
        return False
    
    project_id = project_response.json()['id']
    print(f"   Project ID: {project_id}")
    
    # 4. List projects
    list_response = requests.get(f"{api_v2_url}/projects", headers=headers)
    print(f"GET /projects: {list_response.status_code}")
    
    # 5. Get specific project
    get_project_response = requests.get(f"{api_v2_url}/projects/{project_id}", headers=headers)
    print(f"GET /projects/{project_id}: {get_project_response.status_code}")
    
    # 6. Start build
    build_response = requests.post(f"{api_v2_url}/projects/{project_id}/build",
        headers=headers,
        json={
            "prompt": "Create a simple landing page",
            "uploaded_images": []
        }
    )
    print(f"POST /projects/{project_id}/build: {build_response.status_code}")
    
    if build_response.status_code == 200:
        task_id = build_response.json()['task_id']
        print(f"   Task ID: {task_id}")
        
        # 7. Check build status
        time.sleep(2)
        status_response = requests.get(f"{api_v2_url}/projects/{project_id}/build/status/{task_id}", headers=headers)
        print(f"GET /projects/{project_id}/build/status/{task_id}: {status_response.status_code}")
        if status_response.status_code == 200:
            print(f"   Build status: {status_response.json().get('status')}")
    elif build_response.status_code == 402:
        print(f"   ⚠️ Insufficient credits (expected)")
    else:
        print(f"   ❌ Build failed: {build_response.json()}")
    
    # 8. Get stats
    stats_response = requests.get(f"{api_v2_url}/stats", headers=headers)
    print(f"GET /stats: {stats_response.status_code}")
    
    # 9. Get credit history
    history_response = requests.get(f"{api_v2_url}/credits/history", headers=headers)
    print(f"GET /credits/history: {history_response.status_code}")
    
    print("\n✅ V2 Simple Test Complete")
    return True

if __name__ == "__main__":
    test_v2_simple()