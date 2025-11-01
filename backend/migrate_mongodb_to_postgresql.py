#!/usr/bin/env python3
"""
MongoDB to PostgreSQL Migration Script
Migrates all data from MongoDB (autowebiq_db) to PostgreSQL
Preserves all relationships and data integrity
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from database import (
    Base, User, Project, ProjectMessage, CreditTransaction, 
    UserSession, Template, Component
)

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql+asyncpg://autowebiq:autowebiq_secure_pass@localhost/autowebiq_db'
)

def parse_datetime(value):
    """Convert MongoDB datetime string to Python datetime object"""
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        try:
            # Try parsing ISO format
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            # Fallback to current time if parsing fails
            return datetime.now(timezone.utc)
    else:
        return datetime.now(timezone.utc)

class MongoToPostgreSQLMigrator:
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        self.mongo_db = self.mongo_client.autowebiq_db
        
        self.pg_engine = create_async_engine(DATABASE_URL, echo=False)
        self.AsyncSessionLocal = async_sessionmaker(
            self.pg_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.stats = {
            'users': 0,
            'projects': 0,
            'messages': 0,
            'transactions': 0,
            'sessions': 0,
            'templates': 0,
            'components': 0
        }
    
    async def init_postgresql(self):
        """Initialize PostgreSQL tables"""
        print("🔧 Initializing PostgreSQL tables...")
        async with self.pg_engine.begin() as conn:
            # Drop all tables first (clean slate)
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✅ PostgreSQL tables ready\n")
    
    async def migrate_users(self):
        """Migrate users from MongoDB to PostgreSQL"""
        print("👤 Migrating users...")
        
        async with self.AsyncSessionLocal() as session:
            async for user_doc in self.mongo_db.users.find():
                user = User(
                    id=user_doc.get('id') or user_doc.get('user_id') or str(user_doc.get('_id')),
                    email=user_doc.get('email'),
                    password_hash=user_doc.get('password_hash') or user_doc.get('password'),
                    name=user_doc.get('name') or user_doc.get('username', ''),
                    credits=user_doc.get('credits', 20),
                    firebase_uid=user_doc.get('firebase_uid'),
                    github_token=user_doc.get('github_token'),
                    created_at=parse_datetime(user_doc.get('created_at')),
                    updated_at=parse_datetime(user_doc.get('updated_at'))
                )
                session.add(user)
                self.stats['users'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['users']} users\n")
    
    async def migrate_projects(self):
        """Migrate projects from MongoDB to PostgreSQL"""
        print("📁 Migrating projects...")
        
        # Get all valid user IDs first
        valid_user_ids = set()
        async for user_doc in self.mongo_db.users.find({}, {'id': 1, 'user_id': 1}):
            user_id = user_doc.get('id') or user_doc.get('user_id') or str(user_doc.get('_id'))
            valid_user_ids.add(user_id)
        
        skipped = 0
        async with self.AsyncSessionLocal() as session:
            async for project_doc in self.mongo_db.projects.find():
                user_id = project_doc.get('user_id')
                
                # Skip projects with invalid user_id
                if user_id not in valid_user_ids:
                    skipped += 1
                    continue
                
                project = Project(
                    id=project_doc.get('id') or project_doc.get('project_id') or str(project_doc.get('_id')),
                    user_id=user_id,
                    name=project_doc.get('name', 'Untitled Project'),
                    description=project_doc.get('description', ''),
                    generated_code=project_doc.get('generated_code') or project_doc.get('code'),
                    status=project_doc.get('status', 'completed'),
                    template_id=project_doc.get('template_id'),
                    build_time=project_doc.get('build_time'),
                    created_at=parse_datetime(project_doc.get('created_at')),
                    updated_at=parse_datetime(project_doc.get('updated_at'))
                )
                session.add(project)
                self.stats['projects'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['projects']} projects ({skipped} skipped due to missing users)\n")
    
    async def migrate_messages(self):
        """Migrate project messages from MongoDB to PostgreSQL"""
        print("💬 Migrating messages...")
        
        async with self.AsyncSessionLocal() as session:
            async for msg_doc in self.mongo_db.messages.find():
                message = ProjectMessage(
                    id=msg_doc.get('id') or msg_doc.get('message_id') or str(msg_doc.get('_id')),
                    project_id=msg_doc.get('project_id'),
                    role=msg_doc.get('role', 'user'),
                    content=msg_doc.get('content', ''),
                    agent_type=msg_doc.get('agent_type'),
                    agent_status=msg_doc.get('agent_status'),
                    progress=msg_doc.get('progress', 0),
                    created_at=parse_datetime(msg_doc.get('created_at'))
                )
                session.add(message)
                self.stats['messages'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['messages']} messages\n")
    
    async def migrate_transactions(self):
        """Migrate credit transactions from MongoDB to PostgreSQL"""
        print("💳 Migrating credit transactions...")
        
        async with self.AsyncSessionLocal() as session:
            async for txn_doc in self.mongo_db.credit_transactions.find():
                transaction = CreditTransaction(
                    id=txn_doc.get('id') or txn_doc.get('transaction_id') or str(txn_doc.get('_id')),
                    user_id=txn_doc.get('user_id'),
                    transaction_type=txn_doc.get('transaction_type') or txn_doc.get('type', 'deduction'),
                    amount=txn_doc.get('amount', 0),
                    balance_before=txn_doc.get('balance_before', 0),
                    balance_after=txn_doc.get('balance_after', 0),
                    status=txn_doc.get('status', 'completed'),
                    description=txn_doc.get('description', ''),
                    extra_data=txn_doc.get('extra_data') or txn_doc.get('metadata'),
                    created_at=parse_datetime(txn_doc.get('created_at'))
                )
                session.add(transaction)
                self.stats['transactions'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['transactions']} transactions\n")
    
    async def migrate_sessions(self):
        """Migrate user sessions from MongoDB to PostgreSQL"""
        print("🔑 Migrating user sessions...")
        
        async with self.AsyncSessionLocal() as session:
            async for session_doc in self.mongo_db.user_sessions.find():
                user_session = UserSession(
                    id=session_doc.get('id') or session_doc.get('session_id') or str(session_doc.get('_id')),
                    user_id=session_doc.get('user_id'),
                    session_token=session_doc.get('session_token') or session_doc.get('token', ''),
                    expires_at=parse_datetime(session_doc.get('expires_at')),
                    created_at=parse_datetime(session_doc.get('created_at'))
                )
                session.add(user_session)
                self.stats['sessions'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['sessions']} sessions\n")
    
    async def migrate_templates(self):
        """Migrate templates from MongoDB to PostgreSQL"""
        print("📄 Migrating templates...")
        
        async with self.AsyncSessionLocal() as session:
            async for template_doc in self.mongo_db.templates.find():
                template = Template(
                    id=template_doc.get('template_id') or template_doc.get('id') or str(template_doc.get('_id')),
                    name=template_doc.get('name', 'Untitled Template'),
                    description=template_doc.get('description', ''),
                    category=template_doc.get('category', 'general'),
                    tags=template_doc.get('tags', []),
                    html_structure=template_doc.get('html_structure') or template_doc.get('html', ''),
                    customization_zones=template_doc.get('customization_zones', []),
                    preview_image=template_doc.get('preview_image'),
                    features=template_doc.get('features', []),
                    color_schemes=template_doc.get('color_schemes', []),
                    seo_score=template_doc.get('seo_score', 90),
                    lighthouse_score=template_doc.get('lighthouse_score', 92),
                    responsive=template_doc.get('responsive', True),
                    created_at=parse_datetime(template_doc.get('created_at')),
                    updated_at=parse_datetime(template_doc.get('updated_at'))
                )
                session.add(template)
                self.stats['templates'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['templates']} templates\n")
    
    async def migrate_components(self):
        """Migrate components from MongoDB to PostgreSQL"""
        print("🧩 Migrating components...")
        
        async with self.AsyncSessionLocal() as session:
            async for component_doc in self.mongo_db.components.find():
                component = Component(
                    id=component_doc.get('component_id') or component_doc.get('id') or str(component_doc.get('_id')),
                    name=component_doc.get('name', 'Untitled Component'),
                    description=component_doc.get('description', ''),
                    category=component_doc.get('category', 'general'),
                    tags=component_doc.get('tags', []),
                    html_code=component_doc.get('html_code') or component_doc.get('html', ''),
                    css_code=component_doc.get('css_code') or component_doc.get('css'),
                    js_code=component_doc.get('js_code') or component_doc.get('js'),
                    preview_image=component_doc.get('preview_image'),
                    props=component_doc.get('props', {}),
                    variants=component_doc.get('variants', []),
                    responsive=component_doc.get('responsive', True),
                    created_at=parse_datetime(component_doc.get('created_at')),
                    updated_at=parse_datetime(component_doc.get('updated_at'))
                )
                session.add(component)
                self.stats['components'] += 1
            
            await session.commit()
        
        print(f"✅ Migrated {self.stats['components']} components\n")
    
    async def verify_migration(self):
        """Verify all data was migrated correctly"""
        print("🔍 Verifying migration...\n")
        
        async with self.AsyncSessionLocal() as session:
            # Count records in PostgreSQL
            pg_counts = {}
            
            for table_name, model in [
                ('users', User),
                ('projects', Project),
                ('messages', ProjectMessage),
                ('transactions', CreditTransaction),
                ('sessions', UserSession),
                ('templates', Template),
                ('components', Component)
            ]:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {model.__tablename__}"))
                count = result.scalar()
                pg_counts[table_name] = count
        
        # Compare with MongoDB
        mongo_counts = {}
        mongo_counts['users'] = await self.mongo_db.users.count_documents({})
        mongo_counts['projects'] = await self.mongo_db.projects.count_documents({})
        mongo_counts['messages'] = await self.mongo_db.messages.count_documents({})
        mongo_counts['transactions'] = await self.mongo_db.credit_transactions.count_documents({})
        mongo_counts['sessions'] = await self.mongo_db.user_sessions.count_documents({})
        mongo_counts['templates'] = await self.mongo_db.templates.count_documents({})
        mongo_counts['components'] = await self.mongo_db.components.count_documents({})
        
        print("="*60)
        print(f"{'Collection':<20} {'MongoDB':<15} {'PostgreSQL':<15} {'Status':<10}")
        print("="*60)
        
        all_match = True
        for key in mongo_counts.keys():
            mongo_count = mongo_counts[key]
            pg_count = pg_counts[key]
            status = "✅" if mongo_count == pg_count else "❌"
            if mongo_count != pg_count:
                all_match = False
            print(f"{key:<20} {mongo_count:<15} {pg_count:<15} {status:<10}")
        
        print("="*60)
        print()
        
        return all_match
    
    async def cleanup(self):
        """Cleanup connections"""
        self.mongo_client.close()
        await self.pg_engine.dispose()
    
    async def run(self):
        """Run the complete migration"""
        print("\n" + "="*60)
        print("🚀 MongoDB to PostgreSQL Migration")
        print("="*60 + "\n")
        
        try:
            # Initialize PostgreSQL
            await self.init_postgresql()
            
            # Migrate all data
            await self.migrate_users()
            await self.migrate_projects()
            await self.migrate_messages()
            await self.migrate_transactions()
            await self.migrate_sessions()
            await self.migrate_templates()
            await self.migrate_components()
            
            # Verify migration
            success = await self.verify_migration()
            
            if success:
                print("🎉 Migration completed successfully!")
                print(f"\nTotal records migrated:")
                print(f"  Users: {self.stats['users']}")
                print(f"  Projects: {self.stats['projects']}")
                print(f"  Messages: {self.stats['messages']}")
                print(f"  Transactions: {self.stats['transactions']}")
                print(f"  Sessions: {self.stats['sessions']}")
                print(f"  Templates: {self.stats['templates']}")
                print(f"  Components: {self.stats['components']}")
                print(f"\n✅ All data migrated successfully!")
                return True
            else:
                print("❌ Migration verification failed. Some data may not have migrated correctly.")
                return False
                
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()


async def main():
    migrator = MongoToPostgreSQLMigrator()
    success = await migrator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
