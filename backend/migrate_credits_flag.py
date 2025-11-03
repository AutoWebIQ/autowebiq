"""
Database Migration Script
Adds initial_credits_granted flag to existing users to prevent double crediting
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def migrate_existing_users():
    """Add initial_credits_granted flag to all existing users"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'autowebiq')]
    
    print("Starting migration: Adding initial_credits_granted flag to existing users...")
    
    # Update all users that don't have the flag
    result = await db.users.update_many(
        {"initial_credits_granted": {"$exists": False}},  # Find users without the flag
        {"$set": {"initial_credits_granted": True}}  # Set flag to True (assume they already got credits)
    )
    
    print(f"✅ Migration complete!")
    print(f"   - Matched: {result.matched_count} users")
    print(f"   - Modified: {result.modified_count} users")
    print(f"   - All existing users now have initial_credits_granted = True")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_existing_users())
