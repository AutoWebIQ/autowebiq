import React, { useState } from 'react';
import './LandingPage.css';

const LandingPage = ({ onLogin }) => {
  const [showAuth, setShowAuth] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const body = isLogin
        ? { email, password }
        : { email, password, name };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data.user, data.access_token);
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <nav className="nav">
          <div className="nav-logo">
            <span className="logo-icon">⚡</span>
            <span>AutoWebIQ</span>
          </div>
          <button className="btn btn-primary" onClick={() => setShowAuth(true)}>
            Get Started
          </button>
        </nav>

        <div className="hero-content">
          <h1 className="hero-title">
            Build Beautiful Websites
            <br />
            <span className="gradient-text">with AI in Seconds</span>
          </h1>
          <p className="hero-subtitle">
            Just describe your vision, and watch as our AI agents
            <br />
            create a professional website right before your eyes.
          </p>
          <div className="hero-stats">
            <div className="stat">
              <div className="stat-number">10</div>
              <div className="stat-label">Free Credits</div>
            </div>
            <div className="stat">
              <div className="stat-number">30s</div>
              <div className="stat-label">Generation Time</div>
            </div>
            <div className="stat">
              <div className="stat-number">100%</div>
              <div className="stat-label">Responsive</div>
            </div>
          </div>
          <button className="btn btn-primary btn-large" onClick={() => setShowAuth(true)}>
            Start Building Free →
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">Powered by AI Agents</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>Planning Agent</h3>
            <p>Analyzes your requirements and creates a strategic plan</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎨</div>
            <h3>Design Agent</h3>
            <p>Creates beautiful, modern designs that convert</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💻</div>
            <h3>Code Agent</h3>
            <p>Generates clean, responsive, production-ready code</p>
          </div>
        </div>
      </section>

      {/* Auth Modal */}
      {showAuth && (
        <div className="modal-overlay" onClick={() => setShowAuth(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuth(false)}>×</button>
            
            <h2 className="modal-title">
              {isLogin ? 'Welcome Back' : 'Get Started Free'}
            </h2>
            <p className="modal-subtitle">
              {isLogin ? 'Login to continue building' : 'Start with 10 free credits'}
            </p>

            <form onSubmit={handleSubmit}>
              {!isLogin && (
                <input
                  type="text"
                  className="input"
                  placeholder="Your Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              )}
              <input
                type="email"
                className="input mt-2"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                className="input mt-2"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              {error && <div className="error-message mt-2">{error}</div>}

              <button
                type="submit"
                className="btn btn-primary mt-3"
                style={{ width: '100%' }}
                disabled={loading}
              >
                {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
              </button>
            </form>

            <p className="modal-footer mt-3">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <span className="link" onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Sign up' : 'Login'}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
