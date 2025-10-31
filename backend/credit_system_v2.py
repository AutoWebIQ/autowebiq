# Credit System v2 - PostgreSQL Version
# Manages credits with PostgreSQL transactions

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, CreditTransaction
from typing import Optional, Dict
from datetime import datetime, timezone
import uuid
from enum import Enum

class TransactionType(str, Enum):
    DEDUCTION = "deduction"
    REFUND = "refund"
    PURCHASE = "purchase"
    SIGNUP_BONUS = "signup_bonus"
    MONTHLY_RESET = "monthly_reset"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"

class CreditManagerV2:
    """PostgreSQL-based credit management system"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_credits(self, user_id: str) -> Optional[int]:
        """Get user's current credit balance"""
        result = await self.session.execute(
            select(User.credits).where(User.id == user_id)
        )
        user_credits = result.scalar_one_or_none()
        return user_credits
    
    async def deduct_credits(
        self,
        user_id: str,
        amount: int,
        description: str,
        extra_data: Optional[Dict] = None
    ) -> Dict:
        """
        Deduct credits from user account
        
        Returns:
            Dict with status, balance_before, balance_after, transaction_id
        """
        # Get current balance
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        balance_before = user.credits
        
        if balance_before < amount:
            return {
                'status': 'insufficient_credits',
                'balance': balance_before,
                'required': amount,
                'message': f'Insufficient credits. Need {amount}, have {balance_before}'
            }
        
        # Deduct credits
        balance_after = balance_before - amount
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(credits=balance_after, updated_at=datetime.now(timezone.utc))
        )
        
        # Create transaction record
        transaction = CreditTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transaction_type=TransactionType.DEDUCTION,
            amount=-amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status=TransactionStatus.COMPLETED,
            description=description,
            extra_data=extra_data,
            created_at=datetime.now(timezone.utc)
        )
        
        self.session.add(transaction)
        await self.session.flush()
        
        return {
            'status': 'success',
            'balance_before': balance_before,
            'balance_after': balance_after,
            'amount_deducted': amount,
            'transaction_id': transaction.id,
            'message': f'Successfully deducted {amount} credits'
        }
    
    async def add_credits(
        self,
        user_id: str,
        amount: int,
        transaction_type: TransactionType,
        description: str,
        extra_data: Optional[Dict] = None
    ) -> Dict:
        """
        Add credits to user account
        
        Returns:
            Dict with status, balance_before, balance_after, transaction_id
        """
        # Get current balance
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        balance_before = user.credits
        balance_after = balance_before + amount
        
        # Add credits
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(credits=balance_after, updated_at=datetime.now(timezone.utc))
        )
        
        # Create transaction record
        transaction = CreditTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status=TransactionStatus.COMPLETED,
            description=description,
            extra_data=extra_data,
            created_at=datetime.now(timezone.utc)
        )
        
        self.session.add(transaction)
        await self.session.flush()
        
        return {
            'status': 'success',
            'balance_before': balance_before,
            'balance_after': balance_after,
            'amount_added': amount,
            'transaction_id': transaction.id,
            'message': f'Successfully added {amount} credits'
        }
    
    async def refund_credits(
        self,
        user_id: str,
        amount: int,
        description: str,
        original_transaction_id: Optional[str] = None
    ) -> Dict:
        """
        Refund credits to user account
        """
        extra_data = {}
        if original_transaction_id:
            extra_data['original_transaction_id'] = original_transaction_id
        
        return await self.add_credits(
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.REFUND,
            description=description,
            extra_data=extra_data
        )
    
    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """Get user's transaction history"""
        result = await self.session.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        transactions = result.scalars().all()
        
        return [
            {
                'id': tx.id,
                'transaction_type': tx.transaction_type,
                'amount': tx.amount,
                'balance_before': tx.balance_before,
                'balance_after': tx.balance_after,
                'status': tx.status,
                'description': tx.description,
                'extra_data': tx.extra_data,
                'created_at': tx.created_at.isoformat()
            }
            for tx in transactions
        ]
    
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict]:
        """Get transaction by ID"""
        result = await self.session.execute(
            select(CreditTransaction).where(CreditTransaction.id == transaction_id)
        )
        tx = result.scalar_one_or_none()
        
        if not tx:
            return None
        
        return {
            'id': tx.id,
            'user_id': tx.user_id,
            'transaction_type': tx.transaction_type,
            'amount': tx.amount,
            'balance_before': tx.balance_before,
            'balance_after': tx.balance_after,
            'status': tx.status,
            'description': tx.description,
            'extra_data': tx.extra_data,
            'created_at': tx.created_at.isoformat()
        }


def get_credit_manager_v2(session: AsyncSession) -> CreditManagerV2:
    """Dependency injection for credit manager"""
    return CreditManagerV2(session)
