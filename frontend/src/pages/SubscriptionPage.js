import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, Crown, Zap, Rocket, Shield, CreditCard, Calendar, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import './SubscriptionPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubscriptionPage = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchPlans();
    fetchSubscriptionStatus();
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchPlans = async () => {
    try {
      const res = await fetch(`${API}/subscriptions/plans`);
      const data = await res.json();
      if (data.success) {
        setPlans(data.plans);
      }
    } catch (error) {
      console.error('Error fetching plans:', error);
      toast.error('Failed to load plans');
    }
  };

  const fetchSubscriptionStatus = async () => {
    try {
      const res = await fetch(`${API}/subscriptions/status`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      if (data.success) {
        setCurrentSubscription(data.subscription);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const handleSubscribe = async (planId) => {
    if (planId === 'free') {
      toast.info('You are already on the free plan');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API}/subscriptions/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ plan_id: planId })
      });

      const data = await res.json();
      if (data.success) {
        // Open Razorpay checkout
        const options = {
          key: process.env.REACT_APP_RAZORPAY_KEY_ID || 'rzp_live_RYTAnp7d314cDq',
          subscription_id: data.subscription.subscription_id,
          name: 'AutoWebIQ',
          description: `${planId.charAt(0).toUpperCase() + planId.slice(1)} Plan`,
          handler: async (response) => {
            await verifyPayment(response);
          },
          prefill: {
            email: user?.email
          },
          theme: {
            color: '#667eea'
          }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        toast.error(data.message || 'Failed to create subscription');
      }
    } catch (error) {
      console.error('Subscribe error:', error);
      toast.error('Failed to create subscription');
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (response) => {
    try {
      const res = await fetch(`${API}/subscriptions/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subscription_id: response.razorpay_subscription_id,
          payment_id: response.razorpay_payment_id,
          signature: response.razorpay_signature
        })
      });

      const data = await res.json();
      if (data.success) {
        toast.success(`Subscription activated! ${data.credits_added} credits added`);
        fetchSubscriptionStatus();
        fetchUser();
      } else {
        toast.error('Payment verification failed');
      }
    } catch (error) {
      console.error('Verify payment error:', error);
      toast.error('Payment verification failed');
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return;

    try {
      const res = await fetch(`${API}/subscriptions/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ cancel_at_cycle_end: true })
      });

      const data = await res.json();
      if (data.success) {
        toast.success('Subscription cancelled. You can use it until the end of the billing period.');
        fetchSubscriptionStatus();
      } else {
        toast.error('Failed to cancel subscription');
      }
    } catch (error) {
      console.error('Cancel error:', error);
      toast.error('Failed to cancel subscription');
    }
  };

  const getPlanIcon = (planId) => {
    switch (planId) {
      case 'free': return <Zap className="w-8 h-8" />;
      case 'starter': return <Rocket className="w-8 h-8" />;
      case 'pro': return <Crown className="w-8 h-8" />;
      case 'enterprise': return <Shield className="w-8 h-8" />;
      default: return <Zap className="w-8 h-8" />;
    }
  };

  const formatPrice = (price) => {
    if (price === 0) return '₹0';
    return `₹${(price / 100).toLocaleString()}`;
  };

  return (
    <div className="subscription-page">
      <div className="subscription-header">
        <button className="back-button" onClick={() => navigate('/dashboard')}>← Back to Dashboard</button>
        <h1 className="subscription-title">Subscription Plans</h1>
        <p className="subscription-subtitle">Choose the plan that works best for you</p>
      </div>

      {currentSubscription && currentSubscription.status !== 'none' && (
        <Card className="current-subscription-card">
          <div className="current-sub-header">
            <div>
              <h3>Current Plan: {currentSubscription.plan_id}</h3>
              <p>Status: <span className={`status-badge ${currentSubscription.status}`}>{currentSubscription.status}</span></p>
            </div>
            {currentSubscription.status === 'active' && (
              <Button variant="destructive" onClick={handleCancelSubscription}>Cancel Subscription</Button>
            )}
          </div>
          {currentSubscription.charge_at && (
            <p className="next-billing"><Calendar className="w-4 h-4" /> Next billing: {new Date(currentSubscription.charge_at * 1000).toLocaleDateString()}</p>
          )}
        </Card>
      )}

      <div className="plans-grid">
        {plans.map((plan) => {
          const isCurrentPlan = currentSubscription?.plan_id === plan.id;
          const isPro = plan.id === 'pro';
          
          return (
            <Card key={plan.id} className={`plan-card ${isPro ? 'popular' : ''} ${isCurrentPlan ? 'current' : ''}`}>
              {isPro && <div className="popular-badge">Most Popular</div>}
              {isCurrentPlan && <div className="current-badge">Current Plan</div>}
              
              <div className="plan-icon">{getPlanIcon(plan.id)}</div>
              
              <h3 className="plan-name">{plan.name}</h3>
              
              <div className="plan-price">
                <span className="price-amount">{formatPrice(plan.price)}</span>
                {plan.price > 0 && <span className="price-period">/month</span>}
              </div>
              
              <div className="plan-credits">{plan.credits} credits{plan.price > 0 ? '/month' : ''}</div>
              
              <ul className="plan-features">
                {plan.features.map((feature, idx) => (
                  <li key={idx}>
                    <Check className="w-4 h-4 text-green-500" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              
              <Button
                className={`subscribe-button ${isPro ? 'pro' : ''}`}
                onClick={() => handleSubscribe(plan.id)}
                disabled={loading || isCurrentPlan || plan.id === 'free'}
              >
                {isCurrentPlan ? 'Current Plan' : plan.id === 'free' ? 'Free Plan' : `Subscribe to ${plan.name}`}
              </Button>
            </Card>
          );
        })}
      </div>

      <div className="subscription-faq">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-grid">
          <div className="faq-item">
            <h4><CreditCard className="w-5 h-5" /> How do credits work?</h4>
            <p>Each website generation costs 30-50 credits depending on complexity. Credits reset monthly with your subscription.</p>
          </div>
          <div className="faq-item">
            <h4><AlertCircle className="w-5 h-5" /> Can I cancel anytime?</h4>
            <p>Yes! Cancel anytime and keep using your plan until the end of the billing period.</p>
          </div>
          <div className="faq-item">
            <h4><Zap className="w-5 h-5" /> What happens if I run out of credits?</h4>
            <p>You can purchase additional credit packages or upgrade to a higher plan.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;