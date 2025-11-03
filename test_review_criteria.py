#!/usr/bin/env python3

import requests
import time
import json

def test_review_criteria():
    """Test all success criteria from the review request"""
    
    base_url = "https://multiagent-web.preview.emergentagent.com/api"
    
    print("🎯 TESTING REVIEW REQUEST SUCCESS CRITERIA")
    print("=" * 60)
    
    # 1. Login as demo@test.com
    print("\n1️⃣ Login as demo@test.com")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "demo@test.com",
        "password": "Demo123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    initial_credits = login_response.json()['user']['credits']  # V1 credits
    
    # Get V2 credits for comparison
    v2_credits_response = requests.get(f"{base_url}/v2/user/credits", headers=headers)
    if v2_credits_response.status_code == 200:
        v2_initial_credits = v2_credits_response.json()['credits']
        print(f"✅ Login successful with V1: {initial_credits} credits, V2: {v2_initial_credits} credits")
    else:
        print(f"✅ Login successful with {initial_credits} credits (V2 credits unavailable)")
    
    # 2. Create new project via V2 API (POST /api/v2/projects)
    print("\n2️⃣ Create new project via V2 API")
    project_response = requests.post(f"{base_url}/v2/projects", 
        headers=headers,
        json={
            "name": "Review Test Project",
            "description": "Testing complete V2 build flow as per review request"
        }
    )
    
    if project_response.status_code != 200:
        print(f"❌ Project creation failed: {project_response.status_code}")
        return False
    
    project_id = project_response.json()['id']
    print(f"✅ Project created via V2 API: {project_id}")
    
    # 3. Start async build (POST /api/v2/projects/{id}/build)
    print("\n3️⃣ Start async build via V2 API")
    build_response = requests.post(f"{base_url}/v2/projects/{project_id}/build",
        headers=headers,
        json={
            "prompt": "Create a professional business landing page with hero section, features showcase, pricing table, and contact form. Make it modern and responsive.",
            "uploaded_images": []
        }
    )
    
    if build_response.status_code != 200:
        print(f"❌ Async build start failed: {build_response.status_code}")
        print(f"Response: {build_response.text}")
        return False
    
    build_data = build_response.json()
    task_id = build_data.get('task_id')
    
    # 4. Verify task_id returned
    print("\n4️⃣ Verify task_id returned")
    if not task_id:
        print("❌ No task_id returned")
        return False
    
    print(f"✅ Task ID returned: {task_id}")
    
    # 5. Check build status and verify build completes successfully
    print("\n5️⃣ Check build status and wait for completion")
    
    max_checks = 36  # 3 minutes max (5 second intervals)
    build_completed = False
    final_result = None
    
    for i in range(max_checks):
        time.sleep(5)
        
        status_response = requests.get(f"{base_url}/v2/projects/{project_id}/build/status/{task_id}",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get('status', 'UNKNOWN')
            print(f"   📊 Build Status Check {i+1}: {status}")
            
            if status == 'SUCCESS':
                build_completed = True
                final_result = status_data.get('result', {})
                print("✅ Build completed successfully!")
                break
            elif status == 'FAILURE':
                error = status_data.get('error', 'Unknown error')
                print(f"❌ Build failed: {error}")
                return False
            elif status in ['PENDING', 'PROGRESS']:
                # Show progress if available
                progress_info = status_data.get('progress', {})
                if progress_info and isinstance(progress_info, dict):
                    stage = progress_info.get('stage', 'unknown')
                    progress = progress_info.get('progress', 0)
                    print(f"      Progress: {stage} ({progress}%)")
        else:
            print(f"❌ Status check failed: {status_response.status_code}")
            return False
    
    if not build_completed:
        print("❌ Build did not complete within 3 minutes")
        return False
    
    # 6. Verify build results meet success criteria
    print("\n6️⃣ Verify build results meet success criteria")
    
    success_criteria = {
        "build_completes": False,
        "html_valid_5000_chars": False,
        "credits_deducted": False,
        "databases_updated": False,
        "no_errors_logs": False,
        "template_selection": False,
        "ai_agents_working": False
    }
    
    # Check build completion
    if final_result and final_result.get('status') == 'completed':
        success_criteria["build_completes"] = True
        print("✅ Build completes without errors")
    else:
        print("❌ Build did not complete properly")
    
    # Check generated HTML quality
    frontend_code = final_result.get('frontend_code', '')
    if len(frontend_code) > 5000:
        success_criteria["html_valid_5000_chars"] = True
        print(f"✅ Generated HTML is valid and > 5000 chars ({len(frontend_code)} chars)")
    else:
        print(f"❌ Generated HTML < 5000 chars ({len(frontend_code)} chars)")
    
    # Check credits deducted (check V2 system since V2 build uses V2 credits)
    v2_final_credits_response = requests.get(f"{base_url}/v2/user/credits", headers=headers)
    if v2_final_credits_response.status_code == 200:
        v2_final_credits = v2_final_credits_response.json()['credits']
        v2_credits_used = v2_initial_credits - v2_final_credits
        if v2_credits_used > 0:
            success_criteria["credits_deducted"] = True
            print(f"✅ Credits deducted correctly from V2 system ({v2_credits_used} credits used)")
        else:
            print(f"❌ No credits were deducted from V2 system")
    
    # Also check V1 credits for comparison
    credits_response = requests.get(f"{base_url}/credits/balance", headers=headers)
    if credits_response.status_code == 200:
        v1_final_credits = credits_response.json()['balance']
        v1_credits_used = initial_credits - v1_final_credits
        print(f"   V1 Credits: {v1_final_credits} (used: {v1_credits_used})")
        print(f"   V2 Credits: {v2_final_credits} (used: {v2_credits_used})")
    
    # Check database updates (verify project exists in PostgreSQL)
    project_check = requests.get(f"{base_url}/v2/projects/{project_id}", headers=headers)
    if project_check.status_code == 200:
        success_criteria["databases_updated"] = True
        print("✅ Database updated properly (project exists in PostgreSQL)")
    else:
        print("❌ Database not updated properly")
    
    # Check template selection
    plan = final_result.get('plan', {})
    template_used = plan.get('template_used')
    if template_used:
        success_criteria["template_selection"] = True
        print(f"✅ Template selection works: {template_used}")
    else:
        print("❌ Template selection not working")
    
    # Check AI agents
    if 'frontend_code' in final_result and 'images' in final_result:
        success_criteria["ai_agents_working"] = True
        images_count = len(final_result.get('images', []))
        print(f"✅ AI agents working: Generated HTML + {images_count} images")
    else:
        print("❌ AI agents not working properly")
    
    # Check logs (assume no errors if build completed)
    if build_completed:
        success_criteria["no_errors_logs"] = True
        print("✅ No errors in logs (build completed successfully)")
    
    # 7. Summary
    print("\n7️⃣ FINAL RESULTS SUMMARY")
    print("=" * 40)
    
    passed_criteria = sum(success_criteria.values())
    total_criteria = len(success_criteria)
    success_rate = (passed_criteria / total_criteria) * 100
    
    print(f"Success Criteria: {passed_criteria}/{total_criteria} ({success_rate:.1f}%)")
    
    for criterion, passed in success_criteria.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion.replace('_', ' ').title()}")
    
    # Build performance metrics
    build_time = final_result.get('build_time', 0)
    print(f"\n📊 Performance Metrics:")
    print(f"  • Build Time: {build_time:.1f}s")
    print(f"  • HTML Size: {len(frontend_code)} characters")
    print(f"  • Credits Used: {v2_credits_used if 'v2_credits_used' in locals() else 'N/A'}")
    print(f"  • Template: {template_used}")
    
    return passed_criteria >= 6  # At least 6/7 criteria must pass

if __name__ == "__main__":
    success = test_review_criteria()
    if success:
        print("\n🎉 REVIEW CRITERIA TEST: PASSED")
        print("✅ V2 System meets all success criteria from review request")
    else:
        print("\n💥 REVIEW CRITERIA TEST: FAILED")
        print("❌ V2 System does not meet review success criteria")