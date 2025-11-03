import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Sparkles, Code, Zap, Globe, GitBranch, Rocket, Check, ArrowRight, Star, Users, TrendingUp, Shield, Clock, DollarSign } from 'lucide-react';
import './LandingPageV3.css';

const LandingPageV3 = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('monthly');

  const features = [
    {
      icon: <Sparkles className="w-8 h-8 text-purple-400" />,
      title: 'AI-Powered Generation',
      description: '4 specialized LLMs work together: Claude Sonnet 4 for frontend, GPT-4o for backend, Gemini 2.5 Pro for content, gpt-image-1 for HD images.'
    },
    {
      icon: <Code className="w-8 h-8 text-blue-400" />,
      title: 'Full-Stack Development',
      description: 'Generate complete applications with backend APIs, database schemas, authentication, and beautiful frontends - all in one go.'
    },
    {
      icon: <Globe className="w-8 h-8 text-green-400" />,
      title: 'Instant Preview & Deploy',
      description: 'See your website live instantly with our Emergent-style deployment. Custom subdomains, SSL included, no setup required.'
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-400" />,
      title: 'Lightning Fast',
      description: 'Generate production-ready websites in under 30 seconds. Faster than Emergent, better quality than competitors.'
    },
    {
      icon: <GitBranch className="w-8 h-8 text-pink-400" />,
      title: 'GitHub Integration',
      description: 'One-click save to GitHub. Automatic repo creation, commit history, and collaboration features built-in.'
    },
    {
      icon: <Rocket className="w-8 h-8 text-red-400" />,
      title: 'Template Library',
      description: '24+ production-ready templates across 17 categories. E-commerce, SaaS, portfolios, and more.'
    }
  ];

  const pricingPlans = [
    {
      id: 'free',
      name: 'Free',
      price: '₹0',
      period: 'forever',
      credits: '20 credits',
      description: 'Perfect for trying out AutoWebIQ',
      features: [
        '20 free credits',
        '2-3 websites',
        'Basic templates',
        'Community support',
        'Standard generation speed'
      ],
      cta: 'Start Free',
      popular: false
    },
    {
      id: 'starter',
      name: 'Starter',
      price: '₹999',
      period: 'per month',
      credits: '200 credits/month',
      description: 'Great for freelancers and indie developers',
      features: [
        '200 credits per month',
        '~20 websites',
        'All templates',
        'Priority support',
        'Fast generation',
        'Advanced features',
        'GitHub integration'
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      id: 'pro',
      name: 'Pro',
      price: '₹2,999',
      period: 'per month',
      credits: '750 credits/month',
      description: 'For professional developers and agencies',
      features: [
        '750 credits per month',
        '~75 websites',
        'All templates',
        'Priority support',
        'Fastest generation',
        'Custom domains',
        'Team collaboration',
        'API access',
        'Advanced analytics'
      ],
      cta: 'Go Pro',
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '₹9,999',
      period: 'per month',
      credits: 'Unlimited',
      description: 'For large teams and enterprises',
      features: [
        'Unlimited credits',
        'Unlimited websites',
        'All templates',
        '24/7 priority support',
        'Fastest generation',
        'Custom domains',
        'Team collaboration',
        'API access',
        'Dedicated account manager',
        'Custom integrations',
        'SLA guarantee'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  const comparison = [
    { feature: 'Generation Time', emergent: '~45s', autowebiq: '<30s ⚡', competitor: '~60s' },
    { feature: 'LLM Models', emergent: '2 models', autowebiq: '4 specialized 🧠', competitor: '1 model' },
    { feature: 'Template Library', emergent: '~15', autowebiq: '24+ 📚', competitor: '~10' },
    { feature: 'Full-Stack', emergent: 'Frontend only', autowebiq: 'Backend + Frontend + DB 💪', competitor: 'Frontend only' },
    { feature: 'Agent Transparency', emergent: 'Hidden', autowebiq: 'Real-time display ✨', competitor: 'Hidden' },
    { feature: 'Deployment', emergent: 'Manual', autowebiq: 'One-click instant 🚀', competitor: 'Manual' },
    { feature: 'Starting Price', emergent: '$20/mo', autowebiq: '₹999/mo (~$12) 💰', competitor: '$25/mo' },
    { feature: 'Collaboration', emergent: 'No', autowebiq: 'Real-time 👥', competitor: 'No' }
  ];

  const stats = [
    { number: '1,000+', label: 'Websites Generated' },
    { number: '500+', label: 'Happy Developers' },
    { number: '99.9%', label: 'Uptime' },
    { number: '<30s', label: 'Avg Generation Time' }
  ];

  return (
    <div className="landing-v3">
      {/* Navigation */}
      <nav className="nav-v3">
        <div className="nav-container">
          <div className="nav-logo">
            <Sparkles className="w-8 h-8 text-purple-500" />
            <span className="nav-brand">AutoWebIQ</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#comparison">Compare</a>
            <Button variant="ghost" onClick={() => navigate('/auth?mode=login')}>Login</Button>
            <Button onClick={() => navigate('/auth?mode=register')} className="cta-button">
              Start Building Free
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-v3">
        <div className="hero-content">
          <div className="hero-badge">
            <Star className="w-4 h-4" />
            <span>The #1 AI Website Builder</span>
          </div>
          <h1 className="hero-title">
            Build Production-Ready
            <span className="gradient-text"> Websites with AI</span>
          </h1>
          <p className="hero-subtitle">
            4 specialized AI agents work together to generate full-stack applications in under 30 seconds.
            From simple landing pages to complex web apps - we've got you covered.
          </p>
          <div className="hero-cta">
            <Button size="lg" onClick={() => navigate('/auth?mode=register')} className="cta-button-large">
              Start Building Free <ArrowRight className="ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="demo-button">
              Watch Demo
            </Button>
          </div>
          <div className="hero-stats">
            {stats.map((stat, idx) => (
              <div key={idx} className="stat-item">
                <div className="stat-number">{stat.number}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="hero-visual">
          <div className="browser-mockup">
            <div className="browser-header">
              <div className="browser-dots">
                <span></span><span></span><span></span>
              </div>
              <div className="browser-url">autowebiq.com</div>
            </div>
            <div className="browser-content">
              <div className="code-preview">
                <div className="code-line"><span className="code-keyword">const</span> website = <span className="code-function">generateWithAI</span>(prompt);</div>
                <div className="code-line"><span className="code-keyword">await</span> website.<span className="code-function">deploy</span>();</div>
                <div className="code-line"><span className="code-comment">// ✨ Done in 30 seconds!</span></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-v3">
        <div className="section-header">
          <h2 className="section-title">Why Choose AutoWebIQ?</h2>
          <p className="section-subtitle">Everything you need to build amazing websites, faster</p>
        </div>
        <div className="features-grid">
          {features.map((feature, idx) => (
            <div key={idx} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing-v3">
        <div className="section-header">
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <p className="section-subtitle">Start free, upgrade when you need more</p>
        </div>
        <div className="pricing-grid">
          {pricingPlans.map((plan) => (
            <div key={plan.id} className={`pricing-card ${plan.popular ? 'popular' : ''}`}>
              {plan.popular && <div className="popular-badge">Most Popular</div>}
              <div className="pricing-header">
                <h3 className="pricing-name">{plan.name}</h3>
                <div className="pricing-price">
                  <span className="price-amount">{plan.price}</span>
                  <span className="price-period">/{plan.period}</span>
                </div>
                <div className="pricing-credits">{plan.credits}</div>
                <p className="pricing-description">{plan.description}</p>
              </div>
              <ul className="pricing-features">
                {plan.features.map((feature, idx) => (
                  <li key={idx}>
                    <Check className="w-5 h-5 text-green-400" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button 
                className={plan.popular ? 'pricing-cta popular' : 'pricing-cta'}
                onClick={() => navigate('/auth?mode=register')}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </section>

      {/* Comparison Section */}
      <section id="comparison" className="comparison-v3">
        <div className="section-header">
          <h2 className="section-title">AutoWebIQ vs Competition</h2>
          <p className="section-subtitle">See why we're the best choice for AI website generation</p>
        </div>
        <div className="comparison-table">
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Emergent</th>
                <th className="highlight">AutoWebIQ</th>
                <th>Others</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((row, idx) => (
                <tr key={idx}>
                  <td className="feature-name">{row.feature}</td>
                  <td>{row.emergent}</td>
                  <td className="highlight">{row.autowebiq}</td>
                  <td>{row.competitor}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-v3">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Build Amazing Websites?</h2>
          <p className="cta-subtitle">Start with 20 free credits. No credit card required.</p>
          <Button size="lg" onClick={() => navigate('/auth?mode=register')} className="cta-button-large">
            Start Building Now <Rocket className="ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer-v3">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-logo">
              <Sparkles className="w-6 h-6 text-purple-500" />
              <span>AutoWebIQ</span>
            </div>
            <p>The most advanced AI website builder</p>
          </div>
          <div className="footer-section">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#comparison">Compare</a>
          </div>
          <div className="footer-section">
            <h4>Company</h4>
            <a href="/terms">Terms</a>
            <a href="/privacy">Privacy</a>
            <a href="/contact">Contact</a>
          </div>
          <div className="footer-section">
            <h4>Connect</h4>
            <a href="#">Twitter</a>
            <a href="#">GitHub</a>
            <a href="#">Discord</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 AutoWebIQ. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageV3;