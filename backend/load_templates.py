# Template Loader - Populates MongoDB with templates and components

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from template_data import TEMPLATES, COMPONENTS

async def load_templates():
    """Load all templates into MongoDB"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'autowebiq_db')]
    
    print("🔄 Loading templates into MongoDB...")
    
    # Clear existing templates
    await db.templates.delete_many({})
    await db.components.delete_many({})
    
    # Insert templates
    if TEMPLATES:
        result = await db.templates.insert_many(TEMPLATES)
        print(f"✅ Loaded {len(result.inserted_ids)} templates")
    
    # Insert components
    if COMPONENTS:
        result = await db.components.insert_many(COMPONENTS)
        print(f"✅ Loaded {len(result.inserted_ids)} components")
    
    # Create indexes
    await db.templates.create_index("template_id", unique=True)
    await db.templates.create_index("category")
    await db.templates.create_index("tags")
    await db.components.create_index("component_id", unique=True)
    await db.components.create_index("category")
    
    print("✅ Indexes created")
    
    # List loaded templates
    print("\n📋 Loaded Templates:")
    templates = await db.templates.find({}, {"template_id": 1, "name": 1, "category": 1}).to_list(length=None)
    for t in templates:
        print(f"  - {t['template_id']}: {t['name']} ({t['category']})")
    
    client.close()
    print("\n✅ Template library ready!")

if __name__ == "__main__":
    asyncio.run(load_templates())
