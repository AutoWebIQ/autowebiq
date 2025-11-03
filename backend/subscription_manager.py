"""
Razorpay Subscription Management System
Handles monthly subscription plans for AutoWebIQ 2.0
"""
import os
import razorpay
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Manage Razorpay subscriptions and plan management"""
    
    # Subscription Plans
    PLANS = {
        'free': {
            'name': 'Free',
            'credits_per_month': 20,
            'price': 0,
            'features': [
                '20 credits per month',
                'Basic templates',
                'Community support',
                'Standard generation speed'
            ]
        },
        'starter': {
            'name': 'Starter',
            'credits_per_month': 200,
            'price': 99900,  # ₹999 in paise
            'razorpay_plan_id': 'plan_starter_monthly',
            'features': [
                '200 credits per month',
                'All templates',
                'Priority support',
                'Fast generation',
                'Advanced features'
            ]
        },
        'pro': {
            'name': 'Pro',
            'credits_per_month': 750,
            'price': 299900,  # ₹2999 in paise
            'razorpay_plan_id': 'plan_pro_monthly',
            'features': [
                '750 credits per month',
                'All templates',
                'Priority support',
                'Fastest generation',
                'Advanced features',
                'Custom domains',
                'Team collaboration',
                'API access'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'credits_per_month': 9999,  # Unlimited
            'price': 999900,  # ₹9999 in paise
            'razorpay_plan_id': 'plan_enterprise_monthly',
            'features': [
                'Unlimited credits',
                'All templates',
                '24/7 priority support',
                'Fastest generation',
                'All advanced features',
                'Custom domains',
                'Team collaboration',
                'API access',
                'Dedicated account manager',
                'Custom integrations'
            ]
        }
    }
    
    def __init__(self):
        """Initialize Razorpay client"""
        self.client = razorpay.Client(
            auth=(
                os.environ.get('RAZORPAY_KEY_ID'),
                os.environ.get('RAZORPAY_KEY_SECRET')
            )
        )
    
    def get_all_plans(self) -> List[Dict]:
        """Get all available subscription plans"""
        return [
            {
                'id': plan_id,
                'name': plan_data['name'],
                'price': plan_data['price'],
                'credits': plan_data['credits_per_month'],
                'features': plan_data['features']
            }
            for plan_id, plan_data in self.PLANS.items()
        ]
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict]:
        """Get details for a specific plan"""
        return self.PLANS.get(plan_id)
    
    async def create_subscription(self, user_id: str, plan_id: str, user_email: str) -> Dict:
        """
        Create a new subscription for a user
        
        Args:
            user_id: User ID
            plan_id: Plan ID (starter, pro, enterprise)
            user_email: User email for Razorpay
            
        Returns:
            Dict with subscription details
        """
        try:
            plan = self.PLANS.get(plan_id)
            if not plan:
                raise ValueError(f"Invalid plan: {plan_id}")
            
            if plan_id == 'free':
                raise ValueError("Cannot create subscription for free plan")
            
            # Create Razorpay subscription
            subscription_data = {
                'plan_id': plan['razorpay_plan_id'],
                'customer_notify': 1,
                'total_count': 0,  # Unlimited billing cycles
                'quantity': 1,
                'notes': {
                    'user_id': user_id,
                    'plan': plan_id
                }
            }
            
            razorpay_subscription = self.client.subscription.create(subscription_data)
            
            return {
                'subscription_id': razorpay_subscription['id'],
                'plan_id': plan_id,
                'status': razorpay_subscription['status'],
                'short_url': razorpay_subscription.get('short_url'),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Subscription creation error: {str(e)}")
            raise
    
    async def verify_subscription_payment(
        self,
        subscription_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay subscription payment signature
        
        Args:
            subscription_id: Razorpay subscription ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
            
        Returns:
            True if signature is valid
        """
        try:
            params = {
                'razorpay_subscription_id': subscription_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            self.client.utility.verify_payment_signature(params)
            return True
            
        except razorpay.errors.SignatureVerificationError:
            logger.error("Invalid signature")
            return False
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return False
    
    async def get_subscription_status(self, subscription_id: str) -> Dict:
        """
        Get current status of a subscription
        
        Args:
            subscription_id: Razorpay subscription ID
            
        Returns:
            Dict with subscription details
        """
        try:
            subscription = self.client.subscription.fetch(subscription_id)
            
            return {
                'id': subscription['id'],
                'status': subscription['status'],
                'plan_id': subscription['plan_id'],
                'start_at': subscription.get('start_at'),
                'end_at': subscription.get('end_at'),
                'charge_at': subscription.get('charge_at'),
                'paid_count': subscription.get('paid_count', 0),
                'remaining_count': subscription.get('remaining_count')
            }
            
        except Exception as e:
            logger.error(f"Get subscription status error: {str(e)}")
            raise
    
    async def cancel_subscription(self, subscription_id: str, cancel_at_cycle_end: bool = True) -> Dict:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Razorpay subscription ID
            cancel_at_cycle_end: If True, cancel at end of current billing cycle
            
        Returns:
            Dict with cancellation details
        """
        try:
            if cancel_at_cycle_end:
                subscription = self.client.subscription.cancel(
                    subscription_id,
                    {'cancel_at_cycle_end': 1}
                )
            else:
                subscription = self.client.subscription.cancel(subscription_id)
            
            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'ended_at': subscription.get('ended_at'),
                'cancelled_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cancel subscription error: {str(e)}")
            raise
    
    async def pause_subscription(self, subscription_id: str) -> Dict:
        """Pause a subscription"""
        try:
            subscription = self.client.subscription.pause(subscription_id)
            
            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'paused_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pause subscription error: {str(e)}")
            raise
    
    async def resume_subscription(self, subscription_id: str) -> Dict:
        """Resume a paused subscription"""
        try:
            subscription = self.client.subscription.resume(subscription_id)
            
            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'resumed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resume subscription error: {str(e)}")
            raise
    
    def get_credits_for_plan(self, plan_id: str) -> int:
        """Get monthly credits for a plan"""
        plan = self.PLANS.get(plan_id, {})
        return plan.get('credits_per_month', 0)
    
    async def should_refill_credits(self, user_data: Dict) -> bool:
        """
        Check if user should receive monthly credit refill
        
        Args:
            user_data: User document from database
            
        Returns:
            True if credits should be refilled
        """
        subscription = user_data.get('subscription', {})
        if not subscription or subscription.get('status') != 'active':
            return False
        
        last_refill = subscription.get('last_credit_refill')
        if not last_refill:
            return True
        
        # Check if a month has passed
        last_refill_date = datetime.fromisoformat(last_refill)
        now = datetime.now(timezone.utc)
        days_since_refill = (now - last_refill_date).days
        
        return days_since_refill >= 30
    
    async def refill_monthly_credits(self, user_data: Dict, db) -> Dict:
        """
        Refill monthly credits for a user
        
        Args:
            user_data: User document
            db: Database connection
            
        Returns:
            Dict with refill details
        """
        subscription = user_data.get('subscription', {})
        plan_id = subscription.get('plan_id', 'free')
        
        credits_to_add = self.get_credits_for_plan(plan_id)
        
        # Update user credits
        await db.users.update_one(
            {'id': user_data['id']},
            {
                '$set': {
                    'credits': credits_to_add,
                    'subscription.last_credit_refill': datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log transaction
        await db.credit_transactions.insert_one({
            'id': str(__import__('uuid').uuid4()),
            'user_id': user_data['id'],
            'type': 'monthly_refill',
            'amount': credits_to_add,
            'plan': plan_id,
            'created_at': datetime.now(timezone.utc).isoformat()
        })
        
        return {
            'credits_added': credits_to_add,
            'new_balance': credits_to_add,
            'plan': plan_id,
            'refilled_at': datetime.now(timezone.utc).isoformat()
        }

# Singleton instance
subscription_manager = SubscriptionManager()
