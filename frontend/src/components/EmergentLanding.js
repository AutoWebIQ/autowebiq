import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Sparkles, Zap, Image as ImageIcon, Palette } from 'lucide-react';
import '../styles/EmergentLanding.css';

const EmergentLanding = () => {
  const navigate = useNavigate();

  // Auto-redirect logged-in users to dashboard
  useEffect(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="purple-landing">
      {/* Navigation */}
      <nav className="purple-nav">
        <div className="nav-content">
          <div className="brand">
            <div className="brand-icon">
              <Sparkles size={28} />
            </div>
            <span className="brand-name">AutoWebIQ</span>
          </div>
          <div className="nav-buttons">
            <Button className="login-btn-purple" onClick={() => navigate('/auth?mode=login')}>
              Login
            </Button>
            <Button className="get-started-purple" onClick={() => navigate('/auth?mode=register')}>
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-purple">
        <div className="hero-container-purple">
          <div className="hero-content-left">
            <h1 className="hero-title-purple">
              Build Your<br />
              Website with<br />
              AI
            </h1>
            <p className="hero-subtitle-purple">
              Easily create and launch your own<br />
              website powered by artificial<br />
              intelligence
            </p>
            <Button 
              className="hero-cta-purple" 
              size="lg"
              onClick={() => navigate('/auth?mode=register')}
            >
              Get Started
            </Button>
          </div>

          <div className="hero-content-right">
            <div className="mockup-browser">
              <div className="browser-header">
                <div className="browser-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
              <div className="browser-content">
                <div className="mockup-header">
                  <h2>Beauty Products</h2>
                  <div className="mockup-bar"></div>
                </div>
                <div className="mockup-grid">
                  <div className="mockup-product main-product">
                    <img src="https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400" alt="Beauty Product" />
                  </div>
                  <div className="mockup-product">
                    <img src="https://images.unsplash.com/photo-1515377905703-c4788e51af15?w=300" alt="Model" />
                  </div>
                  <div className="mockup-product">
                    <img src="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=300" alt="Cosmetics" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-purple">
        <div className="features-container-purple">
          <div className="feature-card-purple">
            <div className="feature-icon-purple">
              <Sparkles size={40} />
            </div>
            <h3>AI-Powered</h3>
            <p>Use the power of AI to generate websites in minutes</p>
          </div>

          <div className="feature-card-purple">
            <div className="feature-icon-purple">
              <Zap size={40} />
            </div>
            <h3>Easy to Use</h3>
            <p>No coding skills required, perfect for everyone</p>
          </div>

          <div className="feature-card-purple">
            <div className="feature-icon-purple">
              <Palette size={40} />
            </div>
            <h3>Customizable</h3>
            <p>Add your own content and make it unique</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-purple">
        <div className="cta-container-purple">
          <div className="cta-content-left-purple">
            <img 
              src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600" 
              alt="Professional" 
              className="cta-image"
            />
          </div>
          <div className="cta-content-right-purple">
            <div className="cta-bubble">
              Launch your professional<br />
              site with just a few clicks
            </div>
            <div className="laptop-mockup">
              <div className="laptop-screen">
                <div className="screen-header">
                  <span>Creative Portfolio</span>
                  <div className="screen-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="screen-content">
                  <img 
                    src="https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800" 
                    alt="Portfolio preview" 
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer-purple">
        <div className="footer-container-purple">
          <div className="footer-brand">
            <div className="brand-icon">
              <Sparkles size={24} />
            </div>
            <span>AutoWebIQ</span>
          </div>
          <p className="footer-text">© 2025 AutoWebIQ. All rights reserved.</p>
          <div className="footer-links">
            <a href="/terms">Terms</a>
            <a href="/privacy">Privacy</a>
            <a href="/contact">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default EmergentLanding;
