import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Sparkles, ArrowRight, Users, Globe, Zap } from 'lucide-react';
import '../styles/EmergentLanding.css';

const EmergentLanding = () => {
  const navigate = useNavigate();
  const [buildPrompt, setBuildPrompt] = useState('');
  const [pricingTab, setPricingTab] = useState('individual');
  const [billingCycle, setBillingCycle] = useState('annual');

  // Auto-redirect logged-in users to dashboard
  useEffect(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const exampleApps = [
    { icon: '📺', text: 'Clone Netflix' },
    { icon: '💰', text: 'Budget Planner' },
    { icon: '👟', text: 'EliteFootwear' },
    { icon: '✨', text: 'Surprise Me' }
  ];

  const showcaseImages = [
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400',
    'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400',
    'https://images.unsplash.com/photo-1559028012-481c04fa702d?w=400',
    'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400',
    'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400'
  ];

  return (
    <div className="emergent-landing">
      {/* Navigation */}
      <nav className="emergent-nav">
        <div className="nav-container">
          <div className="logo">
            <Sparkles className="logo-icon-nav" />
            autowebiq
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#faqs">FAQs</a>
            <a href="#enterprise">Enterprise</a>
          </div>
          <Button className="get-started-btn" onClick={() => navigate('/auth?mode=register')}>
            Get Started <ArrowRight size={16} />
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-left">
            <div className="hero-badge">
              <Sparkles size={32} className="sparkle-icon" />
            </div>
            <h1 className="hero-title">
              The fastest path from<br />
              idea to <span className="text-gradient">product</span>
            </h1>
            <p className="hero-subtitle">
              Already have an account? <a href="/auth?mode=login" className="sign-in-link">Sign in</a>
            </p>

            {/* Google Sign In */}
            <button className="google-btn" onClick={() => navigate('/auth?mode=register')}>
              <svg width="18" height="18" viewBox="0 0 18 18">
                <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/>
                <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
                <path fill="#FBBC05" d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.332z"/>
                <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
              </svg>
              Continue with Google
            </button>

            {/* GitHub and Apple Icons */}
            <div className="alt-auth-icons">
              <button className="icon-btn" onClick={() => navigate('/auth?mode=register')}>
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </button>
              <button className="icon-btn" onClick={() => navigate('/auth?mode=register')}>
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                </svg>
              </button>
            </div>

            <div className="divider">Or start with email</div>

            <Button className="email-signup-btn" onClick={() => navigate('/auth?mode=register')}>
              <span className="btn-icon">💚</span>
              Sign up with Email
            </Button>

            <p className="terms-text">
              By continuing, you agree to our <a href="/terms">Terms of Service</a><br />
              and <a href="/privacy">Privacy Policy</a>
            </p>

            <p className="scroll-text">↓ Scroll down to see magic ↓</p>
          </div>

          <div className="hero-right">
            <div className="showcase-container">
              <div className="badge-top">
                <div className="user-avatars">
                  <div className="user-avatar" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}></div>
                  <div className="user-avatar" style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}}></div>
                  <div className="user-avatar" style={{background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}}></div>
                </div>
                <span className="badge-text">Trusted by 1.5M+ Users</span>
              </div>
              
              <div className="showcase-carousel">
                {showcaseImages.map((img, idx) => (
                  <div key={idx} className="showcase-image-wrapper">
                    <img src={img} alt={`Showcase ${idx + 1}`} className="showcase-image" />
                  </div>
                ))}
              </div>

              <div className="stats-grid">
                <div className="stat">
                  <div className="stat-value">1.5M+</div>
                  <div className="stat-label">Users</div>
                </div>
                <div className="stat">
                  <div className="stat-value">2M+</div>
                  <div className="stat-label">Apps</div>
                </div>
                <div className="stat">
                  <div className="stat-value">180+</div>
                  <div className="stat-label">Countries</div>
                </div>
                <div className="stat">
                  <div className="stat-value highlight-stat">YC</div>
                  <div className="stat-label">Backed by</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Meet AutoWebIQ Section */}
      <section className="meet-section">
        <div className="meet-container">
          <div className="emergent-icon">
            <Sparkles className="icon-sparkle" size={48} />
          </div>
          <h2 className="meet-title">Meet AutoWebIQ</h2>
          <p className="meet-subtitle">
            AutoWebIQ turns concepts into production-ready applications, saving<br />
            time and eliminating technical barriers.
          </p>

          <div className="build-input-container">
            <Input
              placeholder="Build me an app for tracking expenses..."
              value={buildPrompt}
              onChange={(e) => setBuildPrompt(e.target.value)}
              className="build-input"
            />
            <button className="submit-icon" onClick={() => navigate('/auth?mode=register')}>
              <ArrowRight />
            </button>
          </div>

          <div className="example-apps">
            {exampleApps.map((app, idx) => (
              <button key={idx} className="example-app-btn" onClick={() => navigate('/auth?mode=register')}>
                <span className="app-icon">{app.icon}</span>
                {app.text}
              </button>
            ))}
          </div>

          <Button className="start-building-btn" size="lg" onClick={() => navigate('/auth?mode=register')}>
            Start Building <ArrowRight size={20} />
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="features-container">
          <h2 className="features-title">
            What can Emergent<br />
            do for you?
          </h2>
          <p className="features-subtitle">
            From concept to deployment, Emergent handles every aspect of software<br />
            development so you can focus on what matters most - your vision!
          </p>

          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">📱</div>
              <h3>Build websites and mobile apps</h3>
              <p>Transform your ideas into fully functional websites and mobile apps with instant deployment, seamless data connections, and powerful scalability.</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🤖</div>
              <h3>Build custom agents</h3>
              <p>Create intelligent AI agents tailored to your specific needs and workflows.</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🔗</div>
              <h3>Build powerful integrations</h3>
              <p>Connect your apps with third-party services and APIs effortlessly.</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">👥</div>
              <h3>Build with your favourite people</h3>
              <p>Collaborate with your team in real-time and bring ideas to life together.</p>
            </div>
          </div>

          <div className="app-showcase">
            <img src="https://via.placeholder.com/800x600" alt="App showcase" className="showcase-image" />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section" id="pricing">
        <div className="pricing-container">
          <h2 className="pricing-title">Transparent pricing for every builder</h2>
          <p className="pricing-subtitle">
            Choose the plan that fits your building ambitions.<br />
            From weekend projects to enterprise applications, we've got you covered.
          </p>

          <div className="pricing-tabs">
            <button
              className={`tab-btn ${pricingTab === 'individual' ? 'active' : ''}`}
              onClick={() => setPricingTab('individual')}
            >
              Individual
            </button>
            <button
              className={`tab-btn ${pricingTab === 'teams' ? 'active' : ''}`}
              onClick={() => setPricingTab('teams')}
            >
              Teams & Enterprise
            </button>
          </div>

          <div className="pricing-cards">
            {/* Free Plan */}
            <div className="pricing-card">
              <div className="card-header">
                <h3 className="plan-name">Free <span className="gift-icon">🎁</span></h3>
                <p className="plan-description">Get started with essential features at no cost</p>
              </div>
              <div className="card-price">
                <span className="price">$0</span>
                <span className="period">/ month</span>
              </div>
              <div className="card-features">
                <div className="feature">✓ 10 free monthly credits</div>
              </div>
            </div>

            {/* Standard Plan */}
            <div className="pricing-card featured">
              <div className="card-header">
                <h3 className="plan-name">Standard <span className="zero-icon">Ø</span></h3>
                <p className="plan-description">Perfect for first-time builders</p>
                <div className="billing-toggle">
                  <span>Annual</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={billingCycle === 'monthly'}
                      onChange={() => setBillingCycle(billingCycle === 'annual' ? 'monthly' : 'annual')}
                    />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
              <div className="card-price">
                <span className="price">$17</span>
                <span className="period">/ month</span>
                {billingCycle === 'annual' && <span className="save-badge">Save $36</span>}
              </div>
              <div className="card-features">
                <div className="feature-group">Everything in Free, plus:</div>
              </div>
            </div>

            {/* Pro Plan */}
            <div className="pricing-card">
              <div className="card-header">
                <h3 className="plan-name">Pro <span className="star-icon">✦</span></h3>
                <p className="plan-description">Built for serious creators and brands</p>
                <div className="billing-toggle">
                  <span>Annual</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={billingCycle === 'monthly'}
                      onChange={() => setBillingCycle(billingCycle === 'annual' ? 'monthly' : 'annual')}
                    />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
              <div className="card-price">
                <span className="price">$167</span>
                <span className="period">/ month</span>
                {billingCycle === 'annual' && <span className="save-badge">Save $396</span>}
              </div>
              <div className="card-features">
                <div className="feature-group">Everything in Standard, plus:</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="emergent-footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="logo">emergent</div>
            <p className="footer-text">
              © 2025 Emergent. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default EmergentLanding;
