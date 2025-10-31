# End-to-End Integration Test
# Tests the complete flow: Login → Create Project → Start Build → WebSocket Updates → Completion

import asyncio
import httpx
import websockets
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001"

async def test_complete_flow():
    """Test complete user flow with V2 API and WebSocket"""
    
    print("="*70)
    print("END-TO-END INTEGRATION TEST")
    print("="*70)
    
    # Step 1: Login
    print("\n🔐 Step 1: User Authentication")
    print("-"*70)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        login_data = {
            "email": "demo@test.com",
            "password": "Demo123456"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_id = data.get('user', {}).get('id')
                print(f"✅ Login successful")
                print(f"   User: {data.get('user', {}).get('email')}")
                print(f"   Credits: {data.get('user', {}).get('credits')}")
                print(f"   Token: {token[:20]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # Step 2: Get User Info from V2
        print("\n👤 Step 2: Get User Info (V2 API)")
        print("-"*70)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.get(f"{BASE_URL}/api/v2/user/me", headers=headers)
            if response.status_code == 200:
                user = response.json()
                print(f"✅ User info retrieved")
                print(f"   ID: {user.get('id')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Credits: {user.get('credits')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 3: Get User Stats
        print("\n📊 Step 3: Get User Statistics (V2 API)")
        print("-"*70)
        
        try:
            response = await client.get(f"{BASE_URL}/api/v2/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Stats retrieved")
                print(f"   Total Projects: {stats.get('total_projects')}")
                print(f"   Completed: {stats.get('completed_projects')}")
                print(f"   Credits Spent: {stats.get('credits_spent')}")
                print(f"   Member Since: {stats.get('member_since')[:10]}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 4: Create a Test Project
        print("\n📁 Step 4: Create Test Project")
        print("-"*70)
        
        try:
            project_data = {
                "name": f"E2E Test Project {datetime.now().strftime('%H:%M:%S')}",
                "description": "End-to-end integration test project"
            }
            response = await client.post(
                f"{BASE_URL}/api/projects/create",
                json=project_data,
                headers=headers
            )
            
            if response.status_code == 200:
                project = response.json()
                project_id = project.get('id')
                print(f"✅ Project created")
                print(f"   ID: {project_id}")
                print(f"   Name: {project.get('name')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Step 5: Start Async Build (V2 API)
        print("\n🏗️  Step 5: Start Async Build (V2 API)")
        print("-"*70)
        
        try:
            build_data = {
                "prompt": "Create a minimal landing page for a tech startup with a hero section and contact form",
                "uploaded_images": []
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v2/projects/{project_id}/build",
                json=build_data,
                headers=headers
            )
            
            if response.status_code == 200:
                build_result = response.json()
                task_id = build_result.get('task_id')
                print(f"✅ Build started (async)")
                print(f"   Task ID: {task_id}")
                print(f"   Status: {build_result.get('status')}")
                print(f"   Message: {build_result.get('message')}")
                print(f"   WebSocket URL: {build_result.get('websocket_url')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Step 6: Connect to WebSocket
        print("\n🔌 Step 6: Connect to WebSocket for Real-time Updates")
        print("-"*70)
        
        ws_url = f"{WS_URL}/api/v2/ws/build/{project_id}?token={token}"
        
        try:
            print(f"Connecting to: {ws_url[:60]}...")
            
            async with websockets.connect(ws_url) as websocket:
                print("✅ WebSocket connected")
                
                # Listen for messages for up to 60 seconds
                message_count = 0
                start_time = datetime.now()
                
                while (datetime.now() - start_time).seconds < 60:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0
                        )
                        
                        data = json.loads(message)
                        message_count += 1
                        
                        msg_type = data.get('type')
                        
                        if msg_type == 'connection':
                            print(f"\n📡 Connection: {data.get('message')}")
                        
                        elif msg_type == 'agent_message':
                            agent = data.get('agent_type', 'unknown')
                            progress = data.get('progress', 0)
                            msg = data.get('message', '')
                            status = data.get('status', '')
                            
                            emoji = {
                                'planner': '🧠',
                                'frontend': '🎨',
                                'backend': '⚙️',
                                'image': '🖼️',
                                'testing': '🧪',
                                'initializing': '🚀',
                                'building': '🏗️'
                            }.get(agent, '💬')
                            
                            print(f"{emoji} [{progress:3d}%] {agent}: {msg}")
                        
                        elif msg_type == 'build_progress':
                            progress = data.get('data', {}).get('progress', 0)
                            stage = data.get('data', {}).get('stage', 'unknown')
                            print(f"📊 Progress: {progress}% - {stage}")
                        
                        elif msg_type == 'build_complete':
                            result = data.get('result', {})
                            build_time = result.get('build_time', 0)
                            print(f"\n✅ BUILD COMPLETE!")
                            print(f"   Build Time: {build_time:.1f}s")
                            print(f"   Status: {result.get('status')}")
                            break
                        
                        elif msg_type == 'build_error':
                            error = data.get('error', 'Unknown error')
                            print(f"\n❌ BUILD FAILED!")
                            print(f"   Error: {error}")
                            break
                        
                        elif msg_type == 'heartbeat':
                            # Silent heartbeat
                            pass
                        
                        else:
                            print(f"📨 Other message: {msg_type}")
                    
                    except asyncio.TimeoutError:
                        # No message received, continue waiting
                        continue
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON decode error: {e}")
                        continue
                
                print(f"\n📊 Total messages received: {message_count}")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        
        # Step 7: Check Build Status
        print("\n🔍 Step 7: Check Build Status (V2 API)")
        print("-"*70)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/v2/projects/{project_id}/build/status/{task_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Build status retrieved")
                print(f"   Task ID: {status.get('task_id')}")
                print(f"   Status: {status.get('status')}")
                print(f"   Message: {status.get('message', 'N/A')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 8: Get Updated Project
        print("\n📄 Step 8: Get Updated Project (V2 API)")
        print("-"*70)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/v2/projects/{project_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                project = response.json()
                print(f"✅ Project retrieved")
                print(f"   Name: {project.get('name')}")
                print(f"   Status: {project.get('status')}")
                print(f"   Build Time: {project.get('build_time', 0):.1f}s")
                print(f"   Code Length: {len(project.get('generated_code', ''))} chars")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 9: Get Updated Credits
        print("\n💳 Step 9: Check Updated Credits (V2 API)")
        print("-"*70)
        
        try:
            response = await client.get(f"{BASE_URL}/api/v2/user/credits", headers=headers)
            if response.status_code == 200:
                credits = response.json()
                print(f"✅ Credits retrieved")
                print(f"   Balance: {credits.get('credits')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ END-TO-END TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
