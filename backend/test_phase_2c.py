# Test Script for Phase 2C Integration
# Tests PostgreSQL, Celery, and WebSocket integration

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

async def test_phase_2c():
    """Test Phase 2C integration"""
    
    print("="*60)
    print("PHASE 2C INTEGRATION TEST")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health Check (existing endpoint)
        print("\n1️⃣  Testing existing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 2: PostgreSQL Connection (v2 endpoints)
        print("\n2️⃣  Testing PostgreSQL v2 endpoints availability...")
        try:
            # This will fail with 401 but confirms endpoint exists
            response = await client.get(f"{BASE_URL}/api/v2/user/me")
            if response.status_code in [401, 403]:
                print("✅ V2 endpoints are accessible (auth required)")
            else:
                print(f"✅ V2 endpoint responded: {response.status_code}")
        except Exception as e:
            print(f"❌ V2 endpoint error: {e}")
        
        # Test 3: Login and get token (existing auth)
        print("\n3️⃣  Testing authentication...")
        try:
            login_data = {
                "email": "demo@test.com",
                "password": "Demo123456"
            }
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    print("✅ Authentication successful")
                    print(f"   User: {data.get('user', {}).get('email')}")
                    print(f"   Credits: {data.get('user', {}).get('credits')}")
                    
                    # Test 4: Get user info from v2 endpoint
                    print("\n4️⃣  Testing v2 user endpoint with auth...")
                    headers = {"Authorization": f"Bearer {token}"}
                    user_response = await client.get(f"{BASE_URL}/api/v2/user/me", headers=headers)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        print("✅ V2 user endpoint working")
                        print(f"   Email: {user_data.get('email')}")
                        print(f"   Credits: {user_data.get('credits')}")
                    else:
                        print(f"❌ V2 user endpoint failed: {user_response.status_code}")
                    
                    # Test 5: List projects from v2
                    print("\n5️⃣  Testing v2 projects endpoint...")
                    projects_response = await client.get(f"{BASE_URL}/api/v2/projects", headers=headers)
                    
                    if projects_response.status_code == 200:
                        projects = projects_response.json()
                        print(f"✅ V2 projects endpoint working")
                        print(f"   Total projects: {len(projects)}")
                    else:
                        print(f"❌ V2 projects endpoint failed: {projects_response.status_code}")
                    
                    # Test 6: Get user stats
                    print("\n6️⃣  Testing v2 stats endpoint...")
                    stats_response = await client.get(f"{BASE_URL}/api/v2/stats", headers=headers)
                    
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        print(f"✅ V2 stats endpoint working")
                        print(f"   Total projects: {stats.get('total_projects')}")
                        print(f"   Completed: {stats.get('completed_projects')}")
                        print(f"   Credits spent: {stats.get('credits_spent')}")
                    else:
                        print(f"❌ V2 stats endpoint failed: {stats_response.status_code}")
                    
                else:
                    print("❌ No token received")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
        
        # Test 7: Celery Health Check
        print("\n7️⃣  Testing Celery worker...")
        try:
            from celery_tasks import health_check
            result = health_check.delay()
            output = result.get(timeout=10)
            print("✅ Celery worker is operational")
            print(f"   Status: {output.get('status')}")
        except Exception as e:
            print(f"❌ Celery test failed: {e}")
        
        # Test 8: Redis Connection
        print("\n8️⃣  Testing Redis connection...")
        try:
            from redis_cache import cache
            test_key = f"test_{datetime.now().timestamp()}"
            await cache.set(test_key, {"test": "data"}, ttl=60)
            retrieved = await cache.get(test_key)
            if retrieved and retrieved.get('test') == 'data':
                print("✅ Redis is operational")
                await cache.delete(test_key)
            else:
                print("❌ Redis test failed")
        except Exception as e:
            print(f"❌ Redis error: {e}")
        
        # Test 9: PostgreSQL Direct Query
        print("\n9️⃣  Testing PostgreSQL direct query...")
        try:
            from database import AsyncSessionLocal, User
            from sqlalchemy import select, func
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(func.count(User.id)))
                count = result.scalar()
                print(f"✅ PostgreSQL is operational")
                print(f"   Total users in database: {count}")
        except Exception as e:
            print(f"❌ PostgreSQL error: {e}")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_phase_2c())
