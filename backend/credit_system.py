# AutoWebIQ Dynamic Credit System
# Replicates Emergent Labs' credit deduction, refund, and ledger tracking

from datetime import datetime, timezone
from typing import Dict, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Agent types with associated credit costs"""
    PLANNER = "planner"
    FRONTEND = "frontend"
    BACKEND = "backend"
    IMAGE = "image"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class ModelType(Enum):
    """AI Models with base credit costs"""
    GPT_5 = "gpt-5"
    GPT_4O = "gpt-4o"
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    DALLE_3 = "dall-e-3"

class TransactionType(Enum):
    """Credit transaction types"""
    DEDUCTION = "deduction"
    REFUND = "refund"
    PURCHASE = "purchase"
    SIGNUP_BONUS = "signup_bonus"
    MONTHLY_RESET = "monthly_reset"

class CreditStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"

# Credit Cost Configuration (Based on Emergent's pricing model)
# These are dynamic and can be adjusted based on actual API costs

AGENT_CREDIT_COSTS = {
    AgentType.PLANNER: 5,        # Claude Sonnet 4 - planning/analysis
    AgentType.FRONTEND: 8,       # GPT-4o - large HTML/CSS/JS generation
    AgentType.BACKEND: 6,        # GPT-4o - API code generation
    AgentType.IMAGE: 12,         # DALL-E 3 - image generation per image
    AgentType.TESTING: 4,        # GPT-4o - code analysis/testing
    AgentType.DEPLOYMENT: 3,     # Infrastructure operations
}

MODEL_BASE_COSTS = {
    ModelType.GPT_5: 8,              # Most advanced, highest cost
    ModelType.GPT_4O: 5,             # Standard cost
    ModelType.CLAUDE_SONNET_4: 6,    # Claude pricing
    ModelType.GEMINI_2_5_PRO: 4,     # Google AI pricing
    ModelType.DALLE_3: 12,           # Image generation
}

# Model name mappings (for string lookup)
MODEL_NAME_MAPPING = {
    "gpt-5": ModelType.GPT_5,
    "gpt-4o": ModelType.GPT_4O,
    "claude-sonnet-4-20250514": ModelType.CLAUDE_SONNET_4,
    "gemini-2.5-pro": ModelType.GEMINI_2_5_PRO,
    "dall-e-3": ModelType.DALLE_3,
}

# Complexity multipliers
COMPLEXITY_MULTIPLIERS = {
    "simple_chat": 1.0,           # Single message
    "code_generation": 1.5,       # Code generation task
    "multi_agent": 2.0,           # Multi-agent workflow
    "with_images": 1.3,           # Includes image generation
    "with_backend": 1.4,          # Includes backend code
}

class CreditManager:
    """Manages credit deductions, refunds, and ledger tracking"""
    
    def __init__(self, db):
        self.db = db
        self.max_credits_per_task = 1000  # Emergent's technical constraint
    
    async def get_user_balance(self, user_id: str) -> int:
        """Get current credit balance for user"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return 0
        return user.get('credits', 0)
    
    async def calculate_agent_cost(
        self,
        agent_type: AgentType,
        model: Optional[ModelType] = None,
        complexity: str = "simple_chat",
        additional_factors: Optional[Dict] = None
    ) -> int:
        """
        Calculate dynamic credit cost for an agent operation
        
        Args:
            agent_type: Type of agent being used
            model: AI model being used (optional)
            complexity: Operation complexity level
            additional_factors: Dict with custom factors (e.g., token_count, image_count)
        
        Returns:
            Calculated credit cost
        """
        # Base cost from agent type
        base_cost = AGENT_CREDIT_COSTS.get(agent_type, 5)
        
        # Add model cost if specified
        if model:
            model_cost = MODEL_BASE_COSTS.get(model, 0)
            base_cost = max(base_cost, model_cost)  # Use higher of agent or model cost
        
        # Apply complexity multiplier
        multiplier = COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)
        cost = base_cost * multiplier
        
        # Apply additional factors
        if additional_factors:
            # Token-based adjustment (if provided)
            if 'token_count' in additional_factors:
                tokens = additional_factors['token_count']
                # Add 1 credit per 1000 tokens beyond base
                token_cost = max(0, (tokens - 1000) // 1000)
                cost += token_cost
            
            # Image count adjustment
            if 'image_count' in additional_factors:
                image_count = additional_factors['image_count']
                cost += (image_count - 1) * AGENT_CREDIT_COSTS[AgentType.IMAGE]
            
            # Custom multiplier
            if 'multiplier' in additional_factors:
                cost *= additional_factors['multiplier']
        
        # Round up and ensure minimum
        cost = max(1, int(cost))
        
        # Cap at max credits per task
        cost = min(cost, self.max_credits_per_task)
        
        return cost
    
    async def calculate_multi_agent_cost(
        self,
        agents_used: List[AgentType],
        models_used: Dict[AgentType, ModelType],
        has_images: bool = False,
        has_backend: bool = False
    ) -> Dict:
        """
        Calculate total cost for multi-agent build
        
        Returns:
            Dict with breakdown: {
                'total': int,
                'breakdown': {agent: cost, ...},
                'complexity_multiplier': float
            }
        """
        breakdown = {}
        total = 0
        
        # Calculate per-agent costs
        for agent_type in agents_used:
            model = models_used.get(agent_type)
            
            # Determine complexity
            complexity = "multi_agent"
            if has_images and agent_type == AgentType.IMAGE:
                complexity = "with_images"
            if has_backend and agent_type == AgentType.BACKEND:
                complexity = "with_backend"
            
            cost = await self.calculate_agent_cost(agent_type, model, complexity)
            breakdown[agent_type.value] = cost
            total += cost
        
        # Apply multi-agent discount (Emergent-style efficiency)
        # More agents = slight discount (bulk operation)
        if len(agents_used) >= 4:
            discount = 0.9  # 10% discount for full workflow
            total = int(total * discount)
        
        return {
            'total': total,
            'breakdown': breakdown,
            'agents_count': len(agents_used),
            'has_discount': len(agents_used) >= 4
        }
    
    async def reserve_credits(
        self,
        user_id: str,
        amount: int,
        operation: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Reserve credits for an operation (deduct upfront)
        
        Returns:
            {
                'status': 'success' | 'insufficient',
                'transaction_id': str,
                'reserved_amount': int,
                'remaining_balance': int
            }
        """
        # Get current balance
        current_balance = await self.get_user_balance(user_id)
        
        # Check if sufficient
        if current_balance < amount:
            logger.warning(f"Insufficient credits for user {user_id}: {current_balance} < {amount}")
            return {
                'status': 'insufficient',
                'required': amount,
                'available': current_balance,
                'shortfall': amount - current_balance
            }
        
        # Create transaction record
        transaction_id = f"txn_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        transaction = {
            'id': transaction_id,
            'user_id': user_id,
            'type': TransactionType.DEDUCTION.value,
            'amount': -amount,  # Negative for deduction
            'operation': operation,
            'status': CreditStatus.PENDING.value,
            'metadata': metadata or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert transaction
        await self.db.credit_transactions.insert_one(transaction)
        
        # Deduct credits
        result = await self.db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"credits": -amount},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        new_balance = current_balance - amount
        
        logger.info(f"Reserved {amount} credits for user {user_id} (operation: {operation})")
        
        return {
            'status': 'success',
            'transaction_id': transaction_id,
            'reserved_amount': amount,
            'previous_balance': current_balance,
            'remaining_balance': new_balance
        }
    
    async def complete_transaction(
        self,
        transaction_id: str,
        actual_cost: Optional[int] = None
    ) -> Dict:
        """
        Mark transaction as completed
        If actual_cost < reserved, refund difference
        """
        transaction = await self.db.credit_transactions.find_one({"id": transaction_id})
        if not transaction:
            return {'status': 'error', 'message': 'Transaction not found'}
        
        reserved_amount = abs(transaction['amount'])
        user_id = transaction['user_id']
        
        # If actual cost is less, refund difference
        refund_amount = 0
        if actual_cost and actual_cost < reserved_amount:
            refund_amount = reserved_amount - actual_cost
            
            # Create refund transaction
            await self.refund_credits(
                user_id,
                refund_amount,
                f"Partial refund for {transaction['operation']}",
                {'original_transaction': transaction_id}
            )
        
        # Update transaction status
        await self.db.credit_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": {
                    "status": CreditStatus.COMPLETED.value,
                    "actual_cost": actual_cost or reserved_amount,
                    "refund_amount": refund_amount,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Completed transaction {transaction_id} (refund: {refund_amount})")
        
        return {
            'status': 'success',
            'transaction_id': transaction_id,
            'reserved': reserved_amount,
            'actual_cost': actual_cost or reserved_amount,
            'refunded': refund_amount
        }
    
    async def refund_credits(
        self,
        user_id: str,
        amount: int,
        reason: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Refund credits to user (on failure or partial completion)
        """
        transaction_id = f"ref_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        transaction = {
            'id': transaction_id,
            'user_id': user_id,
            'type': TransactionType.REFUND.value,
            'amount': amount,  # Positive for refund
            'reason': reason,
            'status': CreditStatus.COMPLETED.value,
            'metadata': metadata or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert transaction
        await self.db.credit_transactions.insert_one(transaction)
        
        # Add credits back
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"credits": amount},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        new_balance = await self.get_user_balance(user_id)
        
        logger.info(f"Refunded {amount} credits to user {user_id} (reason: {reason})")
        
        return {
            'status': 'success',
            'transaction_id': transaction_id,
            'refunded_amount': amount,
            'new_balance': new_balance
        }
    
    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get credit transaction history for user"""
        transactions = await self.db.credit_transactions.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return transactions
    
    async def get_transaction_summary(self, user_id: str) -> Dict:
        """Get summary of credit usage"""
        # Get all transactions
        transactions = await self.db.credit_transactions.find(
            {"user_id": user_id}
        ).to_list(length=None)
        
        total_spent = 0
        total_refunded = 0
        total_purchased = 0
        
        for txn in transactions:
            if txn['type'] == TransactionType.DEDUCTION.value:
                total_spent += abs(txn['amount'])
            elif txn['type'] == TransactionType.REFUND.value:
                total_refunded += txn['amount']
            elif txn['type'] == TransactionType.PURCHASE.value:
                total_purchased += txn['amount']
        
        current_balance = await self.get_user_balance(user_id)
        
        return {
            'current_balance': current_balance,
            'total_spent': total_spent,
            'total_refunded': total_refunded,
            'total_purchased': total_purchased,
            'net_usage': total_spent - total_refunded,
            'transaction_count': len(transactions)
        }
    
    async def add_signup_bonus(self, user_id: str, amount: int = 20) -> Dict:
        """Add signup bonus credits"""
        transaction_id = f"bonus_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        transaction = {
            'id': transaction_id,
            'user_id': user_id,
            'type': TransactionType.SIGNUP_BONUS.value,
            'amount': amount,
            'status': CreditStatus.COMPLETED.value,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.credit_transactions.insert_one(transaction)
        
        await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"credits": amount}}
        )
        
        logger.info(f"Added signup bonus of {amount} credits to user {user_id}")
        
        return {
            'status': 'success',
            'amount': amount,
            'transaction_id': transaction_id
        }

# Global instance
_credit_manager = None

def get_credit_manager(db):
    """Get or create credit manager instance"""
    global _credit_manager
    if _credit_manager is None:
        _credit_manager = CreditManager(db)
    return _credit_manager
