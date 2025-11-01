# Credit Endpoints - PostgreSQL Version
# Migrated from MongoDB to PostgreSQL

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_helpers import (
    get_user_by_id, update_user_credits,
    get_user_transactions, create_transaction,
    transaction_to_dict, user_to_dict
)


class CreditDeduction(BaseModel):
    amount: int
    description: str
    extra_data: Optional[dict] = None


class CreditAddition(BaseModel):
    amount: int
    description: str
    payment_id: Optional[str] = None


async def get_credit_balance_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user's credit balance"""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "credits": user.credits,
        "user_id": user.id
    }


async def deduct_credits_endpoint(
    deduction_data: CreditDeduction,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deduct credits from user"""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.credits < deduction_data.amount:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. You have {user.credits}, but need {deduction_data.amount}"
        )
    
    # Calculate new balance
    balance_before = user.credits
    balance_after = balance_before - deduction_data.amount
    
    # Update user credits
    await update_user_credits(db, user_id, balance_after)
    
    # Create transaction record
    transaction_dict = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'transaction_type': 'deduction',
        'amount': deduction_data.amount,
        'balance_before': balance_before,
        'balance_after': balance_after,
        'status': 'completed',
        'description': deduction_data.description,
        'extra_data': deduction_data.extra_data,
        'created_at': datetime.now(timezone.utc)
    }
    
    transaction = await create_transaction(db, transaction_dict)
    
    return {
        "success": True,
        "credits_remaining": balance_after,
        "transaction": transaction_to_dict(transaction)
    }


async def add_credits_endpoint(
    addition_data: CreditAddition,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Add credits to user"""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate new balance
    balance_before = user.credits
    balance_after = balance_before + addition_data.amount
    
    # Update user credits
    await update_user_credits(db, user_id, balance_after)
    
    # Create transaction record
    extra_data = {}
    if addition_data.payment_id:
        extra_data['payment_id'] = addition_data.payment_id
    
    transaction_dict = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'transaction_type': 'addition',
        'amount': addition_data.amount,
        'balance_before': balance_before,
        'balance_after': balance_after,
        'status': 'completed',
        'description': addition_data.description,
        'extra_data': extra_data,
        'created_at': datetime.now(timezone.utc)
    }
    
    transaction = await create_transaction(db, transaction_dict)
    
    return {
        "success": True,
        "credits": balance_after,
        "transaction": transaction_to_dict(transaction)
    }


async def get_credit_transactions_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get credit transaction history for user"""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = await get_user_transactions(db, user_id, limit=100)
    
    return {
        "transactions": [transaction_to_dict(t) for t in transactions],
        "current_balance": user.credits
    }


async def get_credit_summary_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get credit usage summary"""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = await get_user_transactions(db, user_id, limit=1000)
    
    # Calculate totals
    total_earned = sum(t.amount for t in transactions if t.transaction_type == 'addition')
    total_spent = sum(t.amount for t in transactions if t.transaction_type == 'deduction')
    
    return {
        "current_balance": user.credits,
        "total_earned": total_earned,
        "total_spent": total_spent,
        "transaction_count": len(transactions)
    }
