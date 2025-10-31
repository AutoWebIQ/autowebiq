# Data Migration Script - MongoDB to PostgreSQL
# Migrates users, projects, messages, and transactions while preserving data integrity

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import select
from database import (
    AsyncSessionLocal, 
    User, Project, ProjectMessage, CreditTransaction, UserSession,
    mongo_client, mongo_db
)
from datetime import datetime, timezone
import uuid
from typing import Dict, List

def parse_datetime(value):
    """Parse datetime from MongoDB (could be string or datetime)"""
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, str):
        from dateutil import parser
        return parser.isoparse(value)
    return value

class DataMigrator:
    """Handles migration from MongoDB to PostgreSQL"""
    
    def __init__(self):
        self.mongo_db = mongo_db
        self.stats = {
            'users': {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0},
            'projects': {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0},
            'messages': {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0},
            'transactions': {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0},
            'sessions': {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0}
        }
    
    async def migrate_users(self, session):
        """Migrate users from MongoDB to PostgreSQL"""
        print("\n" + "="*60)
        print("MIGRATING USERS")
        print("="*60)
        
        # Get all users from MongoDB
        mongo_users = await self.mongo_db.users.find({}).to_list(length=None)
        self.stats['users']['total'] = len(mongo_users)
        
        print(f"📊 Found {len(mongo_users)} users in MongoDB")
        
        for mongo_user in mongo_users:
            try:
                # Check if user already exists
                user_id = mongo_user.get('id') or str(uuid.uuid4())
                existing = await session.execute(
                    select(User).where(User.id == user_id)
                )
                if existing.scalar_one_or_none():
                    print(f"⏭️  User {mongo_user.get('email')} already exists, skipping...")
                    self.stats['users']['skipped'] += 1
                    continue
                
                # Parse dates (MongoDB might store as ISO strings)
                created_at = parse_datetime(mongo_user.get('created_at'))
                updated_at = parse_datetime(mongo_user.get('updated_at'))
                
                # Create PostgreSQL user
                pg_user = User(
                    id=user_id,
                    email=mongo_user.get('email'),
                    password_hash=mongo_user.get('password_hash'),
                    name=mongo_user.get('name'),
                    credits=mongo_user.get('credits', 20),
                    firebase_uid=mongo_user.get('firebase_uid'),
                    github_token=mongo_user.get('github_token'),
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                session.add(pg_user)
                await session.flush()
                
                print(f"✅ Migrated user: {pg_user.email} (Credits: {pg_user.credits})")
                self.stats['users']['migrated'] += 1
                
            except Exception as e:
                print(f"❌ Error migrating user {mongo_user.get('email')}: {e}")
                self.stats['users']['errors'] += 1
                continue
        
        await session.commit()
        print(f"\n✅ Users migration complete: {self.stats['users']['migrated']} migrated, {self.stats['users']['skipped']} skipped, {self.stats['users']['errors']} errors")
    
    async def migrate_projects(self, session):
        """Migrate projects from MongoDB to PostgreSQL"""
        print("\n" + "="*60)
        print("MIGRATING PROJECTS")
        print("="*60)
        
        # Get all projects from MongoDB
        mongo_projects = await self.mongo_db.projects.find({}).to_list(length=None)
        self.stats['projects']['total'] = len(mongo_projects)
        
        print(f"📊 Found {len(mongo_projects)} projects in MongoDB")
        
        for mongo_project in mongo_projects:
            try:
                # Check if project already exists
                project_id = mongo_project.get('id') or str(uuid.uuid4())
                existing = await session.execute(
                    select(Project).where(Project.id == project_id)
                )
                if existing.scalar_one_or_none():
                    print(f"⏭️  Project {mongo_project.get('name')} already exists, skipping...")
                    self.stats['projects']['skipped'] += 1
                    continue
                
                # Verify user exists
                user_id = mongo_project.get('user_id')
                user_check = await session.execute(
                    select(User).where(User.id == user_id)
                )
                if not user_check.scalar_one_or_none():
                    print(f"⚠️  User not found for project {mongo_project.get('name')}, skipping...")
                    self.stats['projects']['skipped'] += 1
                    continue
                
                # Create PostgreSQL project
                pg_project = Project(
                    id=project_id,
                    user_id=user_id,
                    name=mongo_project.get('name', 'Untitled'),
                    description=mongo_project.get('description'),
                    generated_code=mongo_project.get('generated_code'),
                    status=mongo_project.get('status', 'draft'),
                    template_id=mongo_project.get('template_id'),
                    build_time=mongo_project.get('build_time'),
                    created_at=mongo_project.get('created_at', datetime.now(timezone.utc)),
                    updated_at=mongo_project.get('updated_at', datetime.now(timezone.utc))
                )
                
                session.add(pg_project)
                await session.flush()
                
                print(f"✅ Migrated project: {pg_project.name} (User: {user_id[:8]}...)")
                self.stats['projects']['migrated'] += 1
                
            except Exception as e:
                print(f"❌ Error migrating project {mongo_project.get('name')}: {e}")
                self.stats['projects']['errors'] += 1
                continue
        
        await session.commit()
        print(f"\n✅ Projects migration complete: {self.stats['projects']['migrated']} migrated, {self.stats['projects']['skipped']} skipped, {self.stats['projects']['errors']} errors")
    
    async def migrate_messages(self, session):
        """Migrate project messages from MongoDB to PostgreSQL"""
        print("\n" + "="*60)
        print("MIGRATING MESSAGES")
        print("="*60)
        
        # Get all messages from MongoDB
        mongo_messages = await self.mongo_db.project_messages.find({}).to_list(length=None)
        self.stats['messages']['total'] = len(mongo_messages)
        
        print(f"📊 Found {len(mongo_messages)} messages in MongoDB")
        
        for mongo_message in mongo_messages:
            try:
                # Check if message already exists
                message_id = mongo_message.get('id') or str(uuid.uuid4())
                existing = await session.execute(
                    select(ProjectMessage).where(ProjectMessage.id == message_id)
                )
                if existing.scalar_one_or_none():
                    self.stats['messages']['skipped'] += 1
                    continue
                
                # Verify project exists
                project_id = mongo_message.get('project_id')
                project_check = await session.execute(
                    select(Project).where(Project.id == project_id)
                )
                if not project_check.scalar_one_or_none():
                    self.stats['messages']['skipped'] += 1
                    continue
                
                # Create PostgreSQL message
                pg_message = ProjectMessage(
                    id=message_id,
                    project_id=project_id,
                    role=mongo_message.get('role', 'user'),
                    content=mongo_message.get('content', ''),
                    agent_type=mongo_message.get('agent_type'),
                    agent_status=mongo_message.get('agent_status'),
                    progress=mongo_message.get('progress', 0),
                    created_at=mongo_message.get('created_at', datetime.now(timezone.utc))
                )
                
                session.add(pg_message)
                self.stats['messages']['migrated'] += 1
                
            except Exception as e:
                self.stats['messages']['errors'] += 1
                continue
        
        await session.commit()
        print(f"\n✅ Messages migration complete: {self.stats['messages']['migrated']} migrated, {self.stats['messages']['skipped']} skipped, {self.stats['messages']['errors']} errors")
    
    async def migrate_transactions(self, session):
        """Migrate credit transactions from MongoDB to PostgreSQL"""
        print("\n" + "="*60)
        print("MIGRATING CREDIT TRANSACTIONS")
        print("="*60)
        
        # Get all transactions from MongoDB
        mongo_transactions = await self.mongo_db.credit_transactions.find({}).to_list(length=None)
        self.stats['transactions']['total'] = len(mongo_transactions)
        
        print(f"📊 Found {len(mongo_transactions)} transactions in MongoDB")
        
        for mongo_tx in mongo_transactions:
            try:
                # Check if transaction already exists
                tx_id = mongo_tx.get('id') or str(uuid.uuid4())
                existing = await session.execute(
                    select(CreditTransaction).where(CreditTransaction.id == tx_id)
                )
                if existing.scalar_one_or_none():
                    self.stats['transactions']['skipped'] += 1
                    continue
                
                # Verify user exists
                user_id = mongo_tx.get('user_id')
                user_check = await session.execute(
                    select(User).where(User.id == user_id)
                )
                if not user_check.scalar_one_or_none():
                    self.stats['transactions']['skipped'] += 1
                    continue
                
                # Create PostgreSQL transaction
                pg_tx = CreditTransaction(
                    id=tx_id,
                    user_id=user_id,
                    transaction_type=mongo_tx.get('transaction_type', 'deduction'),
                    amount=mongo_tx.get('amount', 0),
                    balance_before=mongo_tx.get('balance_before', 0),
                    balance_after=mongo_tx.get('balance_after', 0),
                    status=mongo_tx.get('status', 'completed'),
                    description=mongo_tx.get('description'),
                    extra_data=mongo_tx.get('metadata'),
                    created_at=mongo_tx.get('created_at', datetime.now(timezone.utc))
                )
                
                session.add(pg_tx)
                self.stats['transactions']['migrated'] += 1
                
            except Exception as e:
                self.stats['transactions']['errors'] += 1
                continue
        
        await session.commit()
        print(f"\n✅ Transactions migration complete: {self.stats['transactions']['migrated']} migrated, {self.stats['transactions']['skipped']} skipped, {self.stats['transactions']['errors']} errors")
    
    async def migrate_sessions(self, session):
        """Migrate user sessions from MongoDB to PostgreSQL"""
        print("\n" + "="*60)
        print("MIGRATING USER SESSIONS")
        print("="*60)
        
        # Get all sessions from MongoDB
        mongo_sessions = await self.mongo_db.user_sessions.find({}).to_list(length=None)
        self.stats['sessions']['total'] = len(mongo_sessions)
        
        print(f"📊 Found {len(mongo_sessions)} sessions in MongoDB")
        
        for mongo_session in mongo_sessions:
            try:
                # Skip expired sessions
                expires_at = mongo_session.get('expires_at')
                if expires_at and expires_at < datetime.now(timezone.utc):
                    self.stats['sessions']['skipped'] += 1
                    continue
                
                # Check if session already exists
                session_id = mongo_session.get('id') or str(uuid.uuid4())
                existing = await session.execute(
                    select(UserSession).where(UserSession.id == session_id)
                )
                if existing.scalar_one_or_none():
                    self.stats['sessions']['skipped'] += 1
                    continue
                
                # Verify user exists
                user_id = mongo_session.get('user_id')
                user_check = await session.execute(
                    select(User).where(User.id == user_id)
                )
                if not user_check.scalar_one_or_none():
                    self.stats['sessions']['skipped'] += 1
                    continue
                
                # Create PostgreSQL session
                pg_session = UserSession(
                    id=session_id,
                    user_id=user_id,
                    session_token=mongo_session.get('session_token'),
                    expires_at=expires_at,
                    created_at=mongo_session.get('created_at', datetime.now(timezone.utc))
                )
                
                session.add(pg_session)
                self.stats['sessions']['migrated'] += 1
                
            except Exception as e:
                self.stats['sessions']['errors'] += 1
                continue
        
        await session.commit()
        print(f"\n✅ Sessions migration complete: {self.stats['sessions']['migrated']} migrated, {self.stats['sessions']['skipped']} skipped, {self.stats['sessions']['errors']} errors")
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        for entity, stats in self.stats.items():
            print(f"\n{entity.upper()}:")
            print(f"  Total: {stats['total']}")
            print(f"  ✅ Migrated: {stats['migrated']}")
            print(f"  ⏭️  Skipped: {stats['skipped']}")
            print(f"  ❌ Errors: {stats['errors']}")
        
        total_migrated = sum(s['migrated'] for s in self.stats.values())
        total_errors = sum(s['errors'] for s in self.stats.values())
        
        print(f"\n{'='*60}")
        print(f"TOTAL: {total_migrated} records migrated, {total_errors} errors")
        print(f"{'='*60}\n")


async def run_migration(dry_run=False):
    """Run the complete migration"""
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be written")
    else:
        print("🚀 STARTING MIGRATION - This will modify your database")
        print("⚠️  Make sure you have backups before proceeding!")
        print("\nPress Ctrl+C within 5 seconds to cancel...")
        await asyncio.sleep(5)
    
    migrator = DataMigrator()
    
    async with AsyncSessionLocal() as session:
        try:
            # Run migrations in order (respecting foreign keys)
            await migrator.migrate_users(session)
            await migrator.migrate_projects(session)
            await migrator.migrate_messages(session)
            await migrator.migrate_transactions(session)
            await migrator.migrate_sessions(session)
            
            # Print summary
            migrator.print_summary()
            
            if dry_run:
                await session.rollback()
                print("✅ Dry run complete - no changes committed")
            else:
                print("✅ Migration complete!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    import sys
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    # Run migration
    asyncio.run(run_migration(dry_run=dry_run))
