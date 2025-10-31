# Redis Cache Warming Script
# Pre-loads frequently accessed data into Redis cache

import asyncio
from redis_cache import cache
from database import mongo_db, AsyncSessionLocal, User
from sqlalchemy import select, func

async def warm_cache():
    """Warm up Redis cache with frequently accessed data"""
    
    print("🔥 Starting cache warming...")
    
    # 1. Cache all templates
    print("\n📚 Caching templates...")
    templates = await mongo_db.templates.find({}).to_list(length=None)
    cached_count = 0
    for template in templates:
        template_id = template.get('template_id')
        if template_id:
            # Remove MongoDB _id before caching
            template.pop('_id', None)
            await cache.set_template(template_id, template, ttl=7200)  # 2 hours
            cached_count += 1
    print(f"✅ Cached {cached_count} templates")
    
    # 2. Cache all components
    print("\n🧩 Caching components...")
    components = await mongo_db.components.find({}).to_list(length=None)
    cached_count = 0
    for component in components:
        component_id = component.get('component_id')
        if component_id:
            component.pop('_id', None)
            await cache.set_component(component_id, component, ttl=7200)
            cached_count += 1
    print(f"✅ Cached {cached_count} components")
    
    # 3. Cache user credits
    print("\n💳 Caching user credits...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id, User.credits))
        users = result.all()
        for user_id, credits in users:
            await cache.set_user_credits(user_id, credits, ttl=300)  # 5 minutes
    print(f"✅ Cached credits for {len(users)} users")
    
    # 4. Cache system stats
    print("\n📊 Caching system stats...")
    async with AsyncSessionLocal() as session:
        # Total users
        total_users = await session.execute(select(func.count(User.id)))
        user_count = total_users.scalar()
        await cache.set('stats:total_users', user_count, ttl=600)
        
        # Total templates
        template_count = await mongo_db.templates.count_documents({})
        await cache.set('stats:total_templates', template_count, ttl=3600)
        
        # Total components
        component_count = await mongo_db.components.count_documents({})
        await cache.set('stats:total_components', component_count, ttl=3600)
    
    print(f"✅ Cached system stats")
    
    print("\n🎉 Cache warming complete!")
    print(f"   Templates: {cached_count}")
    print(f"   Components: {len(components)}")
    print(f"   User credits: {len(users)}")

if __name__ == "__main__":
    asyncio.run(warm_cache())
