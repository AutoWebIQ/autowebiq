import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Mail, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import '../styles/Contact.css';

const ContactPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.message) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      toast.success('Message sent successfully! We\'ll get back to you soon.');
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      });
      setIsSubmitting(false);
    }, 1000);
  };

  return (
    <div className="contact-page">
      {/* Navigation */}
      <nav className="contact-nav">
        <div className="nav-content">
          <div className="brand" onClick={() => navigate('/')}>
            <div className="brand-icon">
              <Sparkles size={28} />
            </div>
            <span className="brand-name">AutoWebIQ</span>
          </div>
          <Button className="back-btn" onClick={() => navigate('/')}>
            <ArrowLeft size={18} />
            Back to Home
          </Button>
        </div>
      </nav>

      {/* Content */}
      <div className="contact-container">
        <div className="contact-content">
          <div className="contact-left">
            <h1 className="contact-title">Contact Us</h1>
            <p className="contact-description">
              Have any questions or feedback? We're here to help! Reach out to us using the form or through our contact information below.
            </p>

            <div className="contact-info">
              <div className="contact-item">
                <div className="contact-icon-box">
                  <Sparkles size={32} />
                </div>
                <div className="contact-text">
                  <h3>AutoWebIQ</h3>
                </div>
              </div>

              <div className="contact-item">
                <div className="contact-icon-box">
                  <Mail size={28} />
                </div>
                <div className="contact-text">
                  <a href="mailto:info@autowebiq.com">info@autowebiq.com</a>
                </div>
              </div>

              <div className="contact-item">
                <div className="contact-icon-box discord-icon">
                  <MessageCircle size={28} />
                </div>
                <div className="contact-text">
                  <span>AutoWebIQ</span>
                </div>
              </div>
            </div>
          </div>

          <div className="contact-right">
            <div className="contact-form-wrapper">
              <h2 className="form-title">Send Us a Message</h2>
              
              <form onSubmit={handleSubmit} className="contact-form">
                <div className="form-group">
                  <label>Name</label>
                  <Input
                    type="text"
                    name="name"
                    placeholder="Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <Input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Subject</label>
                  <Input
                    type="text"
                    name="subject"
                    placeholder="Subject"
                    value={formData.subject}
                    onChange={handleChange}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Message</label>
                  <Textarea
                    name="message"
                    placeholder="Message"
                    value={formData.message}
                    onChange={handleChange}
                    required
                    rows={6}
                    className="form-textarea"
                  />
                </div>

                <Button 
                  type="submit" 
                  className="submit-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Sending...' : 'Send Message'}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="contact-footer">
        <div className="footer-container-contact">
          <div className="footer-brand">
            <div className="brand-icon">
              <Sparkles size={24} />
            </div>
            <span>AutoWebIQ</span>
          </div>
          <p className="footer-text">© 2025 AutoWebIQ. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default ContactPage;
