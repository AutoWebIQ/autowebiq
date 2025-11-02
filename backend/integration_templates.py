# Integration Templates Manager for AutoWebIQ
# Provides code templates for popular integrations

from typing import Dict, List
import json

class IntegrationTemplates:
    """
    Provides ready-to-use code templates for popular integrations:
    - Stripe (payments)
    - Auth0 (authentication)
    - SendGrid (email)
    - Supabase (backend)
    - Google Analytics
    """
    
    def get_stripe_template(self, mode: str = "frontend") -> Dict:
        """Get Stripe integration template"""
        if mode == "frontend":
            return {
                "files": {
                    "src/lib/stripe.js": self._stripe_frontend_lib(),
                    "src/components/CheckoutForm.jsx": self._stripe_checkout_component(),
                    "src/pages/Pricing.jsx": self._stripe_pricing_page()
                },
                "dependencies": {
                    "@stripe/stripe-js": "^2.4.0",
                    "@stripe/react-stripe-js": "^2.4.0"
                },
                "env_vars": [
                    "REACT_APP_STRIPE_PUBLIC_KEY=pk_test_..."
                ]
            }
        else:  # backend
            return {
                "files": {
                    "routes/payment.py": self._stripe_backend_routes(),
                    "services/stripe_service.py": self._stripe_service()
                },
                "dependencies": {
                    "stripe": ">=7.0.0"
                },
                "env_vars": [
                    "STRIPE_SECRET_KEY=sk_test_...",
                    "STRIPE_WEBHOOK_SECRET=whsec_..."
                ]
            }
    
    def get_auth0_template(self, mode: str = "frontend") -> Dict:
        """Get Auth0 integration template"""
        if mode == "frontend":
            return {
                "files": {
                    "src/auth/Auth0Provider.jsx": self._auth0_provider(),
                    "src/hooks/useAuth.js": self._auth0_hook(),
                    "src/components/LoginButton.jsx": self._auth0_login_button()
                },
                "dependencies": {
                    "@auth0/auth0-react": "^2.2.4"
                },
                "env_vars": [
                    "REACT_APP_AUTH0_DOMAIN=your-domain.auth0.com",
                    "REACT_APP_AUTH0_CLIENT_ID=your_client_id"
                ]
            }
        else:  # backend
            return {
                "files": {
                    "middleware/auth0.py": self._auth0_middleware(),
                    "utils/jwt_validator.py": self._auth0_jwt_validator()
                },
                "dependencies": {
                    "python-jose[cryptography]": ">=3.3.0",
                    "requests": ">=2.31.0"
                },
                "env_vars": [
                    "AUTH0_DOMAIN=your-domain.auth0.com",
                    "AUTH0_API_AUDIENCE=your_api_audience"
                ]
            }
    
    def get_sendgrid_template(self) -> Dict:
        """Get SendGrid email integration template"""
        return {
            "files": {
                "services/email_service.py": self._sendgrid_service(),
                "templates/welcome_email.html": self._email_template()
            },
            "dependencies": {
                "sendgrid": ">=6.11.0"
            },
            "env_vars": [
                "SENDGRID_API_KEY=SG...",
                "FROM_EMAIL=noreply@yourdomain.com"
            ]
        }
    
    def get_supabase_template(self, mode: str = "frontend") -> Dict:
        """Get Supabase integration template"""
        if mode == "frontend":
            return {
                "files": {
                    "src/lib/supabase.js": self._supabase_client(),
                    "src/hooks/useSupabase.js": self._supabase_hook()
                },
                "dependencies": {
                    "@supabase/supabase-js": "^2.39.0"
                },
                "env_vars": [
                    "REACT_APP_SUPABASE_URL=https://xxx.supabase.co",
                    "REACT_APP_SUPABASE_ANON_KEY=eyJ..."
                ]
            }
        else:  # backend
            return {
                "files": {
                    "database/supabase.py": self._supabase_backend()
                },
                "dependencies": {
                    "supabase": ">=2.0.0"
                },
                "env_vars": [
                    "SUPABASE_URL=https://xxx.supabase.co",
                    "SUPABASE_SERVICE_KEY=eyJ..."
                ]
            }
    
    def get_google_analytics_template(self) -> Dict:
        """Get Google Analytics template"""
        return {
            "files": {
                "src/analytics/gtag.js": self._gtag_script(),
                "src/hooks/usePageTracking.js": self._page_tracking_hook()
            },
            "dependencies": {},
            "env_vars": [
                "REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX"
            ]
        }
    
    # Template content methods
    def _stripe_frontend_lib(self) -> str:
        return '''import { loadStripe } from '@stripe/stripe-js';

export const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

export const createCheckoutSession = async (priceId) => {
  const response = await fetch('/api/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priceId })
  });
  
  const session = await response.json();
  return session;
};'''
    
    def _stripe_checkout_component(self) -> str:
        return '''import React from 'react';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { stripePromise } from '../lib/stripe';

const CheckoutForm = () => {
  const stripe = useStripe();
  const elements = useElements();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!stripe || !elements) return;
    
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement)
    });
    
    if (error) {
      console.error(error);
    } else {
      // Process payment
      console.log('Payment Method:', paymentMethod);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button type="submit" disabled={!stripe}>Pay Now</button>
    </form>
  );
};

export default CheckoutForm;'''
    
    def _stripe_pricing_page(self) -> str:
        return '''import React from 'react';

const plans = [
  { id: 1, name: 'Basic', price: 9.99, features: ['Feature 1', 'Feature 2'] },
  { id: 2, name: 'Pro', price: 29.99, features: ['All Basic', 'Feature 3', 'Feature 4'] }
];

const PricingPage = () => {
  return (
    <div className="pricing-container">
      {plans.map(plan => (
        <div key={plan.id} className="pricing-card">
          <h3>{plan.name}</h3>
          <p>${plan.price}/mo</p>
          <ul>{plan.features.map(f => <li key={f}>{f}</li>)}</ul>
          <button>Subscribe</button>
        </div>
      ))}
    </div>
  );
};

export default PricingPage;'''
    
    def _stripe_backend_routes(self) -> str:
        return '''from fastapi import APIRouter, HTTPException
import stripe
import os

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-checkout-session")
async def create_checkout_session(price_id: str):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url='https://yourdomain.com/success',
            cancel_url='https://yourdomain.com/cancel'
        )
        return {"sessionId": session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))'''
    
    def _stripe_service(self) -> str:
        return '''import stripe
import os

class StripeService:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    def create_customer(self, email: str):
        return stripe.Customer.create(email=email)
    
    def create_subscription(self, customer_id: str, price_id: str):
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}]
        )
    
    def cancel_subscription(self, subscription_id: str):
        return stripe.Subscription.delete(subscription_id)'''
    
    def _auth0_provider(self) -> str:
        return '''import React from 'react';
import { Auth0Provider as Auth0ProviderSDK } from '@auth0/auth0-react';

const Auth0Provider = ({ children }) => {
  return (
    <Auth0ProviderSDK
      domain={process.env.REACT_APP_AUTH0_DOMAIN}
      clientId={process.env.REACT_APP_AUTH0_CLIENT_ID}
      redirectUri={window.location.origin}
    >
      {children}
    </Auth0ProviderSDK>
  );
};

export default Auth0Provider;'''
    
    def _auth0_hook(self) -> str:
        return '''import { useAuth0 } from '@auth0/auth0-react';

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, loginWithRedirect, logout } = useAuth0();
  
  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginWithRedirect,
    logout: () => logout({ returnTo: window.location.origin })
  };
};'''
    
    def _auth0_login_button(self) -> str:
        return '''import React from 'react';
import { useAuth } from '../hooks/useAuth';

const LoginButton = () => {
  const { isAuthenticated, login, logout, user } = useAuth();
  
  return isAuthenticated ? (
    <div>
      <span>Welcome, {user.name}</span>
      <button onClick={logout}>Logout</button>
    </div>
  ) : (
    <button onClick={login}>Login</button>
  );
};

export default LoginButton;'''
    
    def _auth0_middleware(self) -> str:
        return '''from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            os.getenv("AUTH0_DOMAIN"),
            algorithms=["RS256"],
            audience=os.getenv("AUTH0_API_AUDIENCE")
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")'''
    
    def _auth0_jwt_validator(self) -> str:
        return '''import jwt
from jwt import PyJWKClient
import os

class JWTValidator:
    def __init__(self):
        self.domain = os.getenv("AUTH0_DOMAIN")
        self.audience = os.getenv("AUTH0_API_AUDIENCE")
        self.jwks_client = PyJWKClient(f"https://{self.domain}/.well-known/jwks.json")
    
    def validate(self, token: str):
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.audience
        )'''
    
    def _sendgrid_service(self) -> str:
        return '''from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.from_email = os.getenv("FROM_EMAIL")
    
    def send_welcome_email(self, to_email: str, name: str):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Welcome!',
            html_content=f'<h1>Welcome {name}!</h1>'
        )
        return self.client.send(message)
    
    def send_template_email(self, to_email: str, template_id: str, data: dict):
        message = Mail(from_email=self.from_email, to_emails=to_email)
        message.template_id = template_id
        message.dynamic_template_data = data
        return self.client.send(message)'''
    
    def _email_template(self) -> str:
        return '''<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #007bff; color: white; padding: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to Our Platform!</h1>
    </div>
    <div class="content">
      <p>Hi {{name}},</p>
      <p>Thank you for joining us!</p>
    </div>
  </div>
</body>
</html>'''
    
    def _supabase_client(self) -> str:
        return '''import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);'''
    
    def _supabase_hook(self) -> str:
        return '''import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export const useSupabase = () => {
  const [session, setSession] = useState(null);
  
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    
    return () => subscription.unsubscribe();
  }, []);
  
  return { session, supabase };
};'''
    
    def _supabase_backend(self) -> str:
        return '''from supabase import create_client, Client
import os

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client: Client = create_client(url, key)
    
    def get_user(self, user_id: str):
        return self.client.auth.admin.get_user_by_id(user_id)
    
    def query_table(self, table: str, filters: dict = None):
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.execute()'''
    
    def _gtag_script(self) -> str:
        return '''export const GA_MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID;

export const pageview = (url) => {
  if (typeof window.gtag !== 'undefined') {
    window.gtag('config', GA_MEASUREMENT_ID, { page_path: url });
  }
};

export const event = ({ action, category, label, value }) => {
  if (typeof window.gtag !== 'undefined') {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value
    });
  }
};'''
    
    def _page_tracking_hook(self) -> str:
        return '''import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { pageview } from '../analytics/gtag';

export const usePageTracking = () => {
  const location = useLocation();
  
  useEffect(() => {
    pageview(location.pathname + location.search);
  }, [location]);
};'''


# Singleton instance
_integration_templates = None

def get_integration_templates() -> IntegrationTemplates:
    """Get or create singleton integration templates"""
    global _integration_templates
    if _integration_templates is None:
        _integration_templates = IntegrationTemplates()
    return _integration_templates
