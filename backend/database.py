# Database Configuration - PostgreSQL + MongoDB Hybrid
# PostgreSQL: Users, Projects, Credits, Transactions
# MongoDB: Templates, Components

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

# PostgreSQL Configuration
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql+asyncpg://autowebiq:autowebiq_secure_pass@localhost/autowebiq_db'
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# ==================== PostgreSQL Models ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    name = Column(String(255))
    credits = Column(Integer, default=20)
    firebase_uid = Column(String(255), unique=True, index=True)
    github_token = Column(String(512))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    generated_code = Column(Text)
    status = Column(String(50), default="draft")  # draft, building, completed, failed
    template_id = Column(String(100))
    build_time = Column(Float)  # seconds
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="projects")
    messages = relationship("ProjectMessage", back_populates="project", cascade="all, delete-orphan")


class ProjectMessage(Base):
    __tablename__ = "project_messages"
    
    id = Column(String(36), primary_key=True)  # UUID
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_type = Column(String(50))  # planner, frontend, backend, image, testing
    agent_status = Column(String(50))  # thinking, working, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    project = relationship("Project", back_populates="messages")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)  # deduction, refund, purchase, signup_bonus, monthly_reset
    amount = Column(Integer, nullable=False)
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    status = Column(String(50), default="completed", index=True)  # pending, completed, refunded, failed
    description = Column(Text)
    metadata = Column(JSON)  # Additional data (agent breakdown, etc.)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ==================== Database Helpers ====================

async def get_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ PostgreSQL tables created")


# ==================== MongoDB Connection (for templates/components) ====================

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
mongo_client = AsyncIOMotorClient(mongo_url)
mongo_db = mongo_client.autowebiq_db

# MongoDB collections
templates_collection = mongo_db.templates
components_collection = mongo_db.components


async def close_db():
    """Close database connections"""
    await engine.dispose()
    mongo_client.close()
    print("✅ Database connections closed")
