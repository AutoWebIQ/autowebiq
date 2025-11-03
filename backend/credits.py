# Emergent-Style Gradual Credit System
from datetime import datetime, timezone
from fastapi import HTTPException
from config import db, CREDIT_COSTS
import uuid

async def get_user_credits(user_id: str) -> int:
    """Get user's current credit balance"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'credits': 1})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user.get('credits', 0)

async def deduct_credits(user_id: str, amount: int, action: str) -> dict:
    """Deduct credits and record transaction (Emergent-style gradual deduction)"""
    # Get current balance
    current_balance = await get_user_credits(user_id)
    
    if current_balance < amount:
        raise HTTPException(status_code=402, detail='Insufficient credits')
    
    # Deduct credits
    new_balance = current_balance - amount
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'credits': new_balance}}
    )
    
    # Record transaction
    transaction = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'amount': -amount,
        'action': action,
        'balance_before': current_balance,
        'balance_after': new_balance,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.transactions.insert_one(transaction)
    
    return {
        'credits_deducted': amount,
        'new_balance': new_balance,
        'action': action
    }

async def get_transactions(user_id: str, limit: int = 50) -> list:
    """Get user's credit transaction history"""
    transactions = await db.transactions.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('created_at', -1).limit(limit).to_list(length=limit)
    
    return transactions

def get_action_cost(action: str) -> int:
    """Get credit cost for an action"""
    return CREDIT_COSTS.get(action, 2)  # Default 2 credits
