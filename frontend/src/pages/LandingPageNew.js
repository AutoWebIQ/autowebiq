import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPageNew.css';

const LandingPageNew = () => {
  const navigate = useNavigate();
  const heroRef = useRef(null);

  useEffect(() => {
    // Animate elements on scroll
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('.fade-up, .fade-in').forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="landing-new">
      {/* Header */}
      <header className="header">
        <div className="header-container">
          <div className="logo" onClick={() => navigate('/')}>
            <span className="logo-icon">✨</span>
            <span className="logo-text">AutoWebIQ</span>
          </div>
          
          <div className="header-actions">
            <button className="btn-secondary" onClick={() => navigate('/auth')}>
              Login
            </button>
            <button className="btn-primary" onClick={() => navigate('/auth')}>
              Get Started Free
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero" ref={heroRef}>
        <div className="hero-background">
          <div className="gradient-orb orb-1"></div>
          <div className="gradient-orb orb-2"></div>
          <div className="gradient-orb orb-3"></div>
          <div className="grid-pattern"></div>
        </div>

        <div className="hero-content">
          <div className="hero-badge fade-in">
            <span className="badge-dot"></span>
            <span>4 AI Agents • Lightning Fast • Production Ready</span>
          </div>

          <h1 className="hero-title fade-up">
            Build Production-Ready
            <br />
            <span className="gradient-text">Websites with AI</span>
          </h1>

          <p className="hero-description fade-up">
            AutoWebIQ uses 4 specialized AI agents to generate complete, 
            full-stack websites in seconds. From idea to deployment, faster than ever.
          </p>

          <div className="hero-buttons fade-up">
            <button className="btn-hero-primary" onClick={() => navigate('/auth')}>
              <span>Start Building Free</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="btn-hero-secondary" onClick={() => navigate('/auth')}>
              <span>View Demo</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 5V15M10 15L5 10M10 15L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>

          <div className="hero-stats fade-up">
            <div className="stat">
              <div className="stat-value">1,000+</div>
              <div className="stat-label">Websites Created</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat">
              <div className="stat-value">&lt;30s</div>
              <div className="stat-label">Average Build Time</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat">
              <div className="stat-value">99.9%</div>
              <div className="stat-label">Uptime</div>
            </div>
          </div>
        </div>

        {/* Animated Code Preview */}
        <div className="hero-preview fade-up">
          <div className="preview-window">
            <div className="window-header">
              <div className="window-dots">
                <span className="dot dot-red"></span>
                <span className="dot dot-yellow"></span>
                <span className="dot dot-green"></span>
              </div>
              <div className="window-title">AutoWebIQ Editor</div>
            </div>
            <div className="window-content">
              <div className="code-line">
                <span className="line-number">1</span>
                <span className="code-text">
                  <span className="code-keyword">const</span>{' '}
                  <span className="code-variable">website</span> = 
                  <span className="code-function"> generate</span>
                  <span className="code-bracket">(</span>
                  <span className="code-string">"modern portfolio"</span>
                  <span className="code-bracket">)</span>
                </span>
              </div>
              <div className="code-line">
                <span className="line-number">2</span>
                <span className="code-text">
                  <span className="code-comment">// ✨ 4 AI agents working...</span>
                </span>
              </div>
              <div className="code-line">
                <span className="line-number">3</span>
                <span className="code-text">
                  <span className="code-keyword">await</span>{' '}
                  <span className="code-variable">website</span>
                  <span className="code-operator">.</span>
                  <span className="code-function">deploy</span>
                  <span className="code-bracket">()</span>
                </span>
              </div>
              <div className="code-line">
                <span className="line-number">4</span>
                <span className="code-text">
                  <span className="code-comment">// 🚀 Live in 30 seconds!</span>
                </span>
              </div>
            </div>
            <div className="window-footer">
              <div className="status-indicator">
                <span className="status-dot pulsing"></span>
                <span>Generating...</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <div className="section-container">
          <div className="section-header fade-up">
            <h2 className="section-title">How It Works</h2>
            <p className="section-description">
              4 specialized AI agents collaborate to build your perfect website
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card fade-up">
              <div className="step-number">
                <span>1</span>
              </div>
              <div className="step-content">
                <h3 className="step-title">Describe Your Vision</h3>
                <p className="step-description">
                  Tell us what you want to build in plain English. 
                  Be as detailed or simple as you like.
                </p>
              </div>
              <div className="step-icon">💬</div>
            </div>

            <div className="step-arrow fade-up">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M15 20H25M25 20L20 15M25 20L20 25" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>

            <div className="step-card fade-up">
              <div className="step-number">
                <span>2</span>
              </div>
              <div className="step-content">
                <h3 className="step-title">AI Agents Build</h3>
                <p className="step-description">
                  4 specialized agents create your frontend, backend, 
                  database, and deploy everything automatically.
                </p>
              </div>
              <div className="step-icon">🤖</div>
            </div>

            <div className="step-arrow fade-up">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M15 20H25M25 20L20 15M25 20L20 25" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>

            <div className="step-card fade-up">
              <div className="step-number">
                <span>3</span>
              </div>
              <div className="step-content">
                <h3 className="step-title">Deploy & Share</h3>
                <p className="step-description">
                  Your website goes live instantly with a custom URL. 
                  Share it, iterate, or save to GitHub.
                </p>
              </div>
              <div className="step-icon">🚀</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container fade-up">
          <div className="cta-background">
            <div className="cta-orb cta-orb-1"></div>
            <div className="cta-orb cta-orb-2"></div>
          </div>
          
          <div className="cta-content">
            <h2 className="cta-title">Ready to Build Something Amazing?</h2>
            <p className="cta-description">
              Start with 20 free credits. No credit card required.
            </p>
            <button className="btn-cta" onClick={() => navigate('/auth')}>
              <span>Get Started Now</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-brand">
            <div className="footer-logo">
              <span className="logo-icon">✨</span>
              <span className="logo-text">AutoWebIQ</span>
            </div>
            <p className="footer-tagline">
              Build production-ready websites with AI
            </p>
          </div>

          <div className="footer-bottom">
            <p>&copy; 2025 AutoWebIQ. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageNew;
