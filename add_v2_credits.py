#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('/app/backend')

from database import AsyncSessionLocal, User
from sqlalchemy import select, update
from datetime import datetime, timezone

async def add_credits_to_demo_user():
    """Add credits to demo user in V2 (PostgreSQL) system"""
    
    async with AsyncSessionLocal() as session:
        # Find demo user
        result = await session.execute(
            select(User).where(User.email == "demo@test.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Demo user not found in V2 system")
            return False
        
        print(f"📊 Current V2 credits: {user.credits}")
        
        # Add 100 credits
        new_credits = user.credits + 100
        await session.execute(
            update(User)
            .where(User.email == "demo@test.com")
            .values(credits=new_credits, updated_at=datetime.now(timezone.utc))
        )
        
        await session.commit()
        print(f"✅ Added 100 credits. New balance: {new_credits}")
        return True

if __name__ == "__main__":
    success = asyncio.run(add_credits_to_demo_user())
    if success:
        print("🎉 Credits added successfully")
    else:
        print("💥 Failed to add credits")