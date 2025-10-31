# Production Health Monitor
# Monitors all services and reports status

import asyncio
import subprocess
import httpx
from datetime import datetime
import redis.asyncio as redis
from database import AsyncSessionLocal, mongo_db
from sqlalchemy import text

async def check_service_health():
    """Check health of all production services"""
    
    print("="*70)
    print(f"PRODUCTION HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'overall': 'healthy'
    }
    
    # 1. Check PostgreSQL
    print("\n🐘 PostgreSQL")
    print("-"*70)
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected: {version[:50]}...")
            
            # Get table counts
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            users = result.scalar()
            result = await session.execute(text("SELECT COUNT(*) FROM projects"))
            projects = result.scalar()
            result = await session.execute(text("SELECT COUNT(*) FROM credit_transactions"))
            transactions = result.scalar()
            
            print(f"   Users: {users}")
            print(f"   Projects: {projects}")
            print(f"   Transactions: {transactions}")
            
            health_status['services']['postgresql'] = {
                'status': 'healthy',
                'users': users,
                'projects': projects,
                'transactions': transactions
            }
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['postgresql'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 2. Check MongoDB
    print("\n🍃 MongoDB")
    print("-"*70)
    try:
        await mongo_db.command('ping')
        templates = await mongo_db.templates.count_documents({})
        components = await mongo_db.components.count_documents({})
        
        print(f"✅ Connected")
        print(f"   Templates: {templates}")
        print(f"   Components: {components}")
        
        health_status['services']['mongodb'] = {
            'status': 'healthy',
            'templates': templates,
            'components': components
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['mongodb'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 3. Check Redis
    print("\n🔴 Redis")
    print("-"*70)
    try:
        redis_client = redis.from_url('redis://localhost:6379/0')
        await redis_client.ping()
        
        info = await redis_client.info()
        used_memory = info.get('used_memory_human', 'N/A')
        connected_clients = info.get('connected_clients', 0)
        
        print(f"✅ Connected")
        print(f"   Memory: {used_memory}")
        print(f"   Clients: {connected_clients}")
        
        await redis_client.close()
        
        health_status['services']['redis'] = {
            'status': 'healthy',
            'memory': used_memory,
            'clients': connected_clients
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['redis'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 4. Check Celery Workers
    print("\n🌿 Celery Workers")
    print("-"*70)
    try:
        result = subprocess.run(
            ['celery', '-A', 'celery_app', 'inspect', 'stats'],
            cwd='/app/backend',
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if 'online' in result.stdout:
            lines = result.stdout.split('\n')
            worker_count = sum(1 for line in lines if 'celery@' in line)
            print(f"✅ {worker_count} worker(s) online")
            
            health_status['services']['celery'] = {
                'status': 'healthy',
                'workers': worker_count
            }
        else:
            print(f"⚠️  No workers online")
            health_status['services']['celery'] = {'status': 'warning', 'workers': 0}
            health_status['overall'] = 'degraded'
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['celery'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 5. Check Backend API
    print("\n🚀 Backend API")
    print("-"*70)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('http://localhost:8001/api/health')
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API responding")
                print(f"   Status: {data.get('status')}")
                
                health_status['services']['backend_api'] = {
                    'status': 'healthy',
                    'response_code': 200
                }
            else:
                print(f"⚠️  API returned {response.status_code}")
                health_status['services']['backend_api'] = {
                    'status': 'warning',
                    'response_code': response.status_code
                }
                health_status['overall'] = 'degraded'
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['backend_api'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 6. Check Frontend
    print("\n⚛️  Frontend")
    print("-"*70)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('http://localhost:3000')
            
            if response.status_code == 200:
                print(f"✅ Frontend serving")
                health_status['services']['frontend'] = {
                    'status': 'healthy',
                    'response_code': 200
                }
            else:
                print(f"⚠️  Frontend returned {response.status_code}")
                health_status['services']['frontend'] = {
                    'status': 'warning',
                    'response_code': response.status_code
                }
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['frontend'] = {'status': 'error', 'error': str(e)}
        health_status['overall'] = 'degraded'
    
    # 7. Check Flower Dashboard
    print("\n🌺 Flower Dashboard")
    print("-"*70)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('http://localhost:5555/flower/')
            
            if response.status_code == 200:
                print(f"✅ Flower dashboard available at http://localhost:5555/flower/")
                health_status['services']['flower'] = {
                    'status': 'healthy',
                    'url': 'http://localhost:5555/flower/'
                }
            else:
                print(f"⚠️  Flower returned {response.status_code}")
                health_status['services']['flower'] = {
                    'status': 'warning',
                    'response_code': response.status_code
                }
    except Exception as e:
        print(f"❌ Error: {e}")
        health_status['services']['flower'] = {'status': 'error', 'error': str(e)}
    
    # Summary
    print("\n" + "="*70)
    print(f"OVERALL STATUS: {health_status['overall'].upper()}")
    print("="*70)
    
    healthy_count = sum(1 for s in health_status['services'].values() if s.get('status') == 'healthy')
    total_count = len(health_status['services'])
    
    print(f"\n✅ Healthy Services: {healthy_count}/{total_count}")
    
    if health_status['overall'] == 'healthy':
        print("\n🎉 All systems operational!")
    else:
        print("\n⚠️  Some services need attention")
    
    return health_status

if __name__ == "__main__":
    asyncio.run(check_service_health())
