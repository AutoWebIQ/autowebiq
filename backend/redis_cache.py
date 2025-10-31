# Redis Cache Manager
# Handles caching for templates, components, and user data

import redis.asyncio as redis
import json
from typing import Optional, Any, List
import os

class RedisCache:
    """Redis cache manager for AutoWebIQ"""
    
    def __init__(self):
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    # ==================== Specific Cache Methods ====================
    
    async def get_template(self, template_id: str) -> Optional[dict]:
        """Get template from cache"""
        return await self.get(f"template:{template_id}")
    
    async def set_template(self, template_id: str, template: dict, ttl: int = 7200) -> bool:
        """Cache template (2 hour TTL)"""
        return await self.set(f"template:{template_id}", template, ttl)
    
    async def get_component(self, component_id: str) -> Optional[dict]:
        """Get component from cache"""
        return await self.get(f"component:{component_id}")
    
    async def set_component(self, component_id: str, component: dict, ttl: int = 7200) -> bool:
        """Cache component (2 hour TTL)"""
        return await self.set(f"component:{component_id}", component, ttl)
    
    async def get_user_credits(self, user_id: str) -> Optional[int]:
        """Get user credits from cache"""
        return await self.get(f"user:{user_id}:credits")
    
    async def set_user_credits(self, user_id: str, credits: int, ttl: int = 300) -> bool:
        """Cache user credits (5 minute TTL)"""
        return await self.set(f"user:{user_id}:credits", credits, ttl)
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache for a user"""
        return await self.clear_pattern(f"user:{user_id}:*")
    
    async def get_build_status(self, task_id: str) -> Optional[dict]:
        """Get build task status from cache"""
        return await self.get(f"build:status:{task_id}")
    
    async def set_build_status(self, task_id: str, status: dict, ttl: int = 1800) -> bool:
        """Cache build status (30 minute TTL)"""
        return await self.set(f"build:status:{task_id}", status, ttl)
    
    # ==================== Pub/Sub for Real-time Updates ====================
    
    async def publish_message(self, channel: str, message: dict) -> int:
        """Publish message to channel"""
        try:
            return await self.redis.publish(channel, json.dumps(message))
        except Exception as e:
            print(f"Publish error: {e}")
            return 0
    
    async def subscribe_channel(self, channel: str):
        """Subscribe to channel (returns async generator)"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    
    async def publish_build_update(self, project_id: str, update: dict) -> int:
        """Publish build update for real-time WebSocket"""
        channel = f"build:{project_id}"
        return await self.publish_message(channel, update)
    
    async def close(self):
        """Close Redis connection"""
        await self.redis.close()


# Global cache instance
cache = RedisCache()
