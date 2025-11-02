# Multi-Page Website Generator
# Generates fully functional multi-page websites with working navigation and forms

from typing import Dict, List, Optional
import re

class MultiPageGenerator:
    """Generates multi-page websites with working navigation"""
    
    def __init__(self):
        self.pages = {}
        self.shared_styles = ""
        self.shared_scripts = ""
    
    def analyze_requirements(self, prompt: str) -> Dict:
        """
        Analyze user prompt to determine what pages are needed
        Returns: {
            'pages': ['home', 'about', 'contact', 'services', 'login', 'signup'],
            'features': ['contact_form', 'user_auth', 'newsletter'],
            'business_type': 'ecommerce|portfolio|saas|restaurant|etc'
        }
        """
        prompt_lower = prompt.lower()
        pages = ['home']  # Always include home
        features = []
        business_type = 'general'
        
        # Detect business type
        if any(word in prompt_lower for word in ['shop', 'store', 'ecommerce', 'buy', 'product', 'cart']):
            business_type = 'ecommerce'
            pages.extend(['products', 'cart', 'checkout'])
        elif any(word in prompt_lower for word in ['portfolio', 'designer', 'photographer', 'creative']):
            business_type = 'portfolio'
            pages.extend(['portfolio', 'services'])
        elif any(word in prompt_lower for word in ['saas', 'software', 'app', 'platform', 'tool']):
            business_type = 'saas'
            pages.extend(['features', 'pricing', 'demo'])
        elif any(word in prompt_lower for word in ['restaurant', 'cafe', 'food', 'menu', 'dining']):
            business_type = 'restaurant'
            pages.extend(['menu', 'reservations'])
        elif any(word in prompt_lower for word in ['hotel', 'booking', 'reservation', 'rooms', 'accommodation']):
            business_type = 'hotel'
            pages.extend(['rooms', 'booking', 'amenities'])
        elif any(word in prompt_lower for word in ['blog', 'news', 'article', 'content']):
            business_type = 'blog'
            pages.extend(['blog', 'archive'])
        
        # Always add common pages
        if 'about' not in pages:
            pages.append('about')
        if 'contact' not in pages:
            pages.append('contact')
        
        # Detect authentication needs
        if any(word in prompt_lower for word in ['login', 'signup', 'register', 'account', 'user', 'member']):
            if 'login' not in pages:
                pages.append('login')
            if 'signup' not in pages:
                pages.append('signup')
            features.append('user_auth')
        
        # Detect forms
        if 'contact' in pages or any(word in prompt_lower for word in ['contact', 'form', 'message', 'inquiry']):
            features.append('contact_form')
        
        if any(word in prompt_lower for word in ['newsletter', 'subscribe', 'email']):
            features.append('newsletter')
        
        if any(word in prompt_lower for word in ['booking', 'reservation', 'appointment']):
            features.append('booking_form')
        
        return {
            'pages': pages,
            'features': features,
            'business_type': business_type
        }
    
    def generate_navigation(self, pages: List[str], current_page: str) -> str:
        """Generate navigation HTML for all pages"""
        nav_items = []
        
        # Page display names
        page_names = {
            'home': 'Home',
            'about': 'About',
            'contact': 'Contact',
            'services': 'Services',
            'products': 'Products',
            'portfolio': 'Portfolio',
            'features': 'Features',
            'pricing': 'Pricing',
            'blog': 'Blog',
            'menu': 'Menu',
            'rooms': 'Rooms',
            'booking': 'Book Now',
            'reservations': 'Reservations',
            'cart': 'Cart',
            'checkout': 'Checkout',
            'login': 'Login',
            'signup': 'Sign Up',
            'demo': 'Demo',
            'amenities': 'Amenities',
            'archive': 'Archive'
        }
        
        for page in pages:
            if page == 'home':
                href = 'index.html'
            else:
                href = f'{page}.html'
            
            active_class = 'active' if page == current_page else ''
            display_name = page_names.get(page, page.title())
            
            nav_items.append(f'<a href="{href}" class="nav-link {active_class}">{display_name}</a>')
        
        nav_html = f'''
        <nav class="navbar">
            <div class="nav-container">
                <div class="nav-logo">
                    <a href="index.html">YourBrand</a>
                </div>
                <div class="nav-links">
                    {' '.join(nav_items)}
                </div>
                <div class="nav-mobile-toggle">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </nav>
        '''
        
        return nav_html
    
    def generate_contact_form(self, business_info: Dict) -> str:
        """Generate functional contact form"""
        return '''
        <section class="contact-section" id="contact">
            <div class="container">
                <h2>Get In Touch</h2>
                <p class="section-subtitle">Have a question? We'd love to hear from you.</p>
                
                <div class="contact-grid">
                    <div class="contact-form-wrapper">
                        <form class="contact-form" id="contactForm" onsubmit="handleContactSubmit(event)">
                            <div class="form-group">
                                <label for="name">Full Name *</label>
                                <input type="text" id="name" name="name" required 
                                       placeholder="John Doe">
                            </div>
                            
                            <div class="form-group">
                                <label for="email">Email Address *</label>
                                <input type="email" id="email" name="email" required 
                                       placeholder="john@example.com">
                            </div>
                            
                            <div class="form-group">
                                <label for="phone">Phone Number</label>
                                <input type="tel" id="phone" name="phone" 
                                       placeholder="+1 (555) 123-4567">
                            </div>
                            
                            <div class="form-group">
                                <label for="subject">Subject *</label>
                                <input type="text" id="subject" name="subject" required 
                                       placeholder="How can we help?">
                            </div>
                            
                            <div class="form-group">
                                <label for="message">Message *</label>
                                <textarea id="message" name="message" rows="5" required 
                                          placeholder="Tell us more about your inquiry..."></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">
                                <span class="btn-text">Send Message</span>
                                <span class="btn-loading" style="display: none;">Sending...</span>
                            </button>
                            
                            <div class="form-message" id="formMessage"></div>
                        </form>
                    </div>
                    
                    <div class="contact-info">
                        <div class="info-item">
                            <h3>📧 Email</h3>
                            <p>hello@yourbrand.com</p>
                        </div>
                        
                        <div class="info-item">
                            <h3>📞 Phone</h3>
                            <p>+1 (555) 123-4567</p>
                        </div>
                        
                        <div class="info-item">
                            <h3>📍 Location</h3>
                            <p>123 Business St, Suite 100<br>San Francisco, CA 94103</p>
                        </div>
                        
                        <div class="info-item">
                            <h3>⏰ Business Hours</h3>
                            <p>Monday - Friday: 9am - 6pm<br>Weekend: By Appointment</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <script>
        function handleContactSubmit(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Show loading state
            const btn = form.querySelector('button[type="submit"]');
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            btn.disabled = true;
            
            // Simulate API call (replace with actual API endpoint)
            setTimeout(() => {
                // Success
                const messageDiv = document.getElementById('formMessage');
                messageDiv.innerHTML = '<div class="alert alert-success">✅ Thank you! Your message has been sent successfully. We\'ll get back to you soon.</div>';
                messageDiv.style.display = 'block';
                
                // Reset form
                form.reset();
                
                // Reset button
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
                btn.disabled = false;
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
                
                // Log to console (for demo - replace with actual API call)
                console.log('Contact Form Submission:', data);
                console.log('TODO: Send this data to your backend API at /api/contact');
            }, 1500);
        }
        </script>
        '''
    
    def generate_login_page(self) -> str:
        """Generate functional login page"""
        return '''
        <section class="auth-section">
            <div class="auth-container">
                <div class="auth-box">
                    <h2>Welcome Back</h2>
                    <p class="auth-subtitle">Login to your account</p>
                    
                    <form class="auth-form" id="loginForm" onsubmit="handleLogin(event)">
                        <div class="form-group">
                            <label for="email">Email Address</label>
                            <input type="email" id="email" name="email" required 
                                   placeholder="john@example.com">
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" required 
                                   placeholder="Enter your password">
                        </div>
                        
                        <div class="form-options">
                            <label class="checkbox-label">
                                <input type="checkbox" name="remember"> Remember me
                            </label>
                            <a href="#" class="forgot-link">Forgot password?</a>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-block">
                            <span class="btn-text">Login</span>
                            <span class="btn-loading" style="display: none;">Logging in...</span>
                        </button>
                        
                        <div class="form-message" id="loginMessage"></div>
                    </form>
                    
                    <div class="auth-footer">
                        Don't have an account? <a href="signup.html">Sign up</a>
                    </div>
                    
                    <div class="social-login">
                        <p>Or continue with</p>
                        <div class="social-buttons">
                            <button class="btn-social btn-google">
                                <svg width="18" height="18" viewBox="0 0 18 18"><path d="M9 3.48c1.69 0 2.83.73 3.48 1.34l2.54-2.48C13.46.89 11.43 0 9 0 5.48 0 2.44 2.02.96 4.96l2.91 2.26C4.6 5.05 6.62 3.48 9 3.48z" fill="#EA4335"/><path d="M17.64 9.2c0-.74-.06-1.28-.19-1.84H9v3.34h4.96c-.1.83-.64 2.08-1.84 2.92l2.84 2.2c1.7-1.57 2.68-3.88 2.68-6.62z" fill="#4285F4"/><path d="M3.88 10.78A5.54 5.54 0 0 1 3.58 9c0-.62.11-1.22.29-1.78L.96 4.96A9.008 9.008 0 0 0 0 9c0 1.45.35 2.82.96 4.04l2.92-2.26z" fill="#FBBC05"/><path d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.84-2.2c-.76.53-1.78.9-3.12.9-2.38 0-4.4-1.57-5.12-3.74L.97 13.04C2.45 15.98 5.48 18 9 18z" fill="#34A853"/></svg>
                                Google
                            </button>
                            <button class="btn-social btn-facebook">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                                Facebook
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <script>
        function handleLogin(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Show loading
            const btn = form.querySelector('button[type="submit"]');
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            btn.disabled = true;
            
            // Simulate login (replace with actual API call)
            setTimeout(() => {
                const messageDiv = document.getElementById('loginMessage');
                messageDiv.innerHTML = '<div class="alert alert-success">✅ Login successful! Redirecting...</div>';
                messageDiv.style.display = 'block';
                
                console.log('Login Data:', data);
                console.log('TODO: Send POST request to /api/auth/login with this data');
                
                // Simulate redirect
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1500);
            }, 1500);
        }
        </script>
        '''
    
    def generate_signup_page(self) -> str:
        """Generate functional signup page"""
        return '''
        <section class="auth-section">
            <div class="auth-container">
                <div class="auth-box">
                    <h2>Create Account</h2>
                    <p class="auth-subtitle">Sign up to get started</p>
                    
                    <form class="auth-form" id="signupForm" onsubmit="handleSignup(event)">
                        <div class="form-group">
                            <label for="name">Full Name</label>
                            <input type="text" id="name" name="name" required 
                                   placeholder="John Doe">
                        </div>
                        
                        <div class="form-group">
                            <label for="email">Email Address</label>
                            <input type="email" id="email" name="email" required 
                                   placeholder="john@example.com">
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" required 
                                   placeholder="Minimum 8 characters"
                                   minlength="8">
                            <small class="form-hint">Must be at least 8 characters</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="confirm_password">Confirm Password</label>
                            <input type="password" id="confirm_password" name="confirm_password" required 
                                   placeholder="Re-enter password">
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" name="terms" required>
                                I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-block">
                            <span class="btn-text">Create Account</span>
                            <span class="btn-loading" style="display: none;">Creating account...</span>
                        </button>
                        
                        <div class="form-message" id="signupMessage"></div>
                    </form>
                    
                    <div class="auth-footer">
                        Already have an account? <a href="login.html">Login</a>
                    </div>
                </div>
            </div>
        </section>
        
        <script>
        function handleSignup(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Validate passwords match
            if (data.password !== data.confirm_password) {
                const messageDiv = document.getElementById('signupMessage');
                messageDiv.innerHTML = '<div class="alert alert-error">❌ Passwords do not match</div>';
                messageDiv.style.display = 'block';
                return;
            }
            
            // Show loading
            const btn = form.querySelector('button[type="submit"]');
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            btn.disabled = true;
            
            // Simulate signup (replace with actual API call)
            setTimeout(() => {
                const messageDiv = document.getElementById('signupMessage');
                messageDiv.innerHTML = '<div class="alert alert-success">✅ Account created successfully! Redirecting to login...</div>';
                messageDiv.style.display = 'block';
                
                console.log('Signup Data:', data);
                console.log('TODO: Send POST request to /api/auth/register with this data');
                
                // Simulate redirect
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            }, 1500);
        }
        </script>
        '''
    
    def generate_shared_styles(self) -> str:
        """Generate shared CSS for all pages"""
        return '''
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --gray: #6b7280;
            --light-gray: #f3f4f6;
            --white: #ffffff;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: var(--white);
        }
        
        /* Navigation */
        .navbar {
            background: var(--white);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nav-logo a {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            color: var(--dark);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-link:hover,
        .nav-link.active {
            color: var(--primary);
        }
        
        .nav-mobile-toggle {
            display: none;
            flex-direction: column;
            gap: 4px;
            cursor: pointer;
        }
        
        .nav-mobile-toggle span {
            width: 25px;
            height: 3px;
            background: var(--dark);
            border-radius: 3px;
        }
        
        /* Container */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        /* Sections */
        section {
            padding: 4rem 0;
        }
        
        h1, h2, h3, h4 {
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 3rem;
            line-height: 1.2;
        }
        
        h2 {
            font-size: 2.5rem;
            text-align: center;
        }
        
        .section-subtitle {
            text-align: center;
            color: var(--gray);
            margin-bottom: 3rem;
        }
        
        /* Buttons */
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: var(--primary);
            color: var(--white);
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        
        .btn-block {
            width: 100%;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .form-hint {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.875rem;
            color: var(--gray);
        }
        
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: normal;
        }
        
        /* Alerts */
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
        
        .alert-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
        }
        
        /* Auth Section */
        .auth-section {
            min-height: 80vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--light-gray);
        }
        
        .auth-container {
            width: 100%;
            max-width: 450px;
            padding: 2rem;
        }
        
        .auth-box {
            background: var(--white);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .auth-subtitle {
            text-align: center;
            color: var(--gray);
            margin-bottom: 2rem;
        }
        
        .auth-footer {
            text-align: center;
            margin-top: 1.5rem;
            color: var(--gray);
        }
        
        .auth-footer a {
            color: var(--primary);
            font-weight: 600;
            text-decoration: none;
        }
        
        /* Contact Section */
        .contact-section {
            background: var(--light-gray);
        }
        
        .contact-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            margin-top: 2rem;
        }
        
        .contact-form-wrapper {
            background: var(--white);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .contact-info {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .info-item {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .info-item h3 {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .nav-mobile-toggle {
                display: flex;
            }
            
            .contact-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            h2 {
                font-size: 1.75rem;
            }
        }
        </style>
        '''
    
    def generate_page_template(self, page_name: str, content: str, pages: List[str]) -> str:
        """Generate complete HTML page with navigation"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name.title()} - Your Brand</title>
    {self.generate_shared_styles()}
</head>
<body>
    {self.generate_navigation(pages, page_name)}
    
    <main>
        {content}
    </main>
    
    <footer style="background: #1f2937; color: white; padding: 3rem 0; text-align: center;">
        <div class="container">
            <p>&copy; 2024 YourBrand. All rights reserved.</p>
            <p style="margin-top: 1rem; color: #9ca3af;">
                Built with ❤️ by AutoWebIQ
            </p>
        </div>
    </footer>
</body>
</html>'''
    
    def generate_complete_website(self, prompt: str, business_info: Dict, images: List[str]) -> Dict[str, str]:
        """
        Generate complete multi-page website
        Returns: {'index.html': '...', 'about.html': '...', 'contact.html': '...', ...}
        """
        # Analyze requirements
        analysis = self.analyze_requirements(prompt)
        pages_needed = analysis['pages']
        features = analysis['features']
        business_type = analysis['business_type']
        
        result = {}
        
        # Generate each page
        for page in pages_needed:
            if page == 'home':
                content = self.generate_home_page(business_info, images, business_type)
                result['index.html'] = self.generate_page_template('home', content, pages_needed)
            
            elif page == 'about':
                content = self.generate_about_page(business_info)
                result['about.html'] = self.generate_page_template('about', content, pages_needed)
            
            elif page == 'contact':
                content = self.generate_contact_form(business_info)
                result['contact.html'] = self.generate_page_template('contact', content, pages_needed)
            
            elif page == 'login':
                content = self.generate_login_page()
                result['login.html'] = self.generate_page_template('login', content, pages_needed)
            
            elif page == 'signup':
                content = self.generate_signup_page()
                result['signup.html'] = self.generate_page_template('signup', content, pages_needed)
            
            else:
                # Generate generic page
                content = self.generate_generic_page(page, business_info)
                result[f'{page}.html'] = self.generate_page_template(page, content, pages_needed)
        
        return result
    
    def generate_home_page(self, business_info: Dict, images: List[str], business_type: str) -> str:
        """Generate home page content"""
        hero_image = images[0] if images else 'https://images.unsplash.com/photo-1497366216548-37526070297c'
        
        return f'''
        <section class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6rem 0;">
            <div class="container">
                <div style="max-width: 600px;">
                    <h1>Welcome to Your Brand</h1>
                    <p style="font-size: 1.25rem; margin: 1.5rem 0;">
                        Transform your business with our innovative solutions. 
                        We help companies grow and succeed in the digital age.
                    </p>
                    <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                        <a href="contact.html" class="btn" style="background: white; color: #667eea;">Get Started</a>
                        <a href="about.html" class="btn" style="background: rgba(255,255,255,0.2); color: white; border: 2px solid white;">Learn More</a>
                    </div>
                </div>
            </div>
        </section>
        
        <section style="padding: 4rem 0;">
            <div class="container">
                <h2>Why Choose Us</h2>
                <p class="section-subtitle">We deliver exceptional results that exceed expectations</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-top: 3rem;">
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
                        <h3>Fast Delivery</h3>
                        <p style="color: #6b7280;">Quick turnaround times without compromising quality</p>
                    </div>
                    
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">💎</div>
                        <h3>Premium Quality</h3>
                        <p style="color: #6b7280;">High-quality solutions tailored to your needs</p>
                    </div>
                    
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                        <h3>Expert Team</h3>
                        <p style="color: #6b7280;">Experienced professionals dedicated to your success</p>
                    </div>
                </div>
            </div>
        </section>
        
        <section style="background: #f3f4f6; padding: 4rem 0;">
            <div class="container">
                <h2>Our Services</h2>
                <p class="section-subtitle">Comprehensive solutions for your business needs</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem;">
                    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <h3>Consulting</h3>
                        <p style="color: #6b7280; margin: 1rem 0;">Strategic guidance to help your business thrive in competitive markets.</p>
                        <a href="contact.html" style="color: #6366f1; font-weight: 600; text-decoration: none;">Learn More →</a>
                    </div>
                    
                    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <h3>Development</h3>
                        <p style="color: #6b7280; margin: 1rem 0;">Custom software solutions built with cutting-edge technology.</p>
                        <a href="contact.html" style="color: #6366f1; font-weight: 600; text-decoration: none;">Learn More →</a>
                    </div>
                    
                    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <h3>Support</h3>
                        <p style="color: #6b7280; margin: 1rem 0;">24/7 dedicated support to ensure your success.</p>
                        <a href="contact.html" style="color: #6366f1; font-weight: 600; text-decoration: none;">Learn More →</a>
                    </div>
                </div>
            </div>
        </section>
        
        <section style="padding: 4rem 0;">
            <div class="container" style="text-align: center;">
                <h2>Ready to Get Started?</h2>
                <p style="font-size: 1.25rem; color: #6b7280; margin: 1.5rem 0;">
                    Join thousands of satisfied customers who trust us
                </p>
                <a href="contact.html" class="btn btn-primary" style="margin-top: 1rem; font-size: 1.1rem; padding: 1rem 2rem;">
                    Contact Us Today
                </a>
            </div>
        </section>
        '''
    
    def generate_about_page(self, business_info: Dict) -> str:
        """Generate about page content"""
        return '''
        <section style="padding: 4rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div class="container" style="text-align: center;">
                <h1>About Us</h1>
                <p style="font-size: 1.25rem; margin-top: 1rem; max-width: 800px; margin-left: auto; margin-right: auto;">
                    We're passionate about helping businesses succeed in the digital world
                </p>
            </div>
        </section>
        
        <section style="padding: 4rem 0;">
            <div class="container">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h2 style="text-align: left;">Our Story</h2>
                    <p style="font-size: 1.1rem; color: #6b7280; line-height: 1.8; margin-top: 1rem;">
                        Founded in 2024, we've been on a mission to transform how businesses operate in the digital age. 
                        What started as a small team with a big vision has grown into a trusted partner for companies worldwide.
                    </p>
                    
                    <p style="font-size: 1.1rem; color: #6b7280; line-height: 1.8; margin-top: 1rem;">
                        Our approach combines innovation with reliability, ensuring that every solution we deliver 
                        not only meets but exceeds expectations. We believe in building long-term partnerships based 
                        on trust, transparency, and tangible results.
                    </p>
                    
                    <h2 style="text-align: left; margin-top: 3rem;">Our Values</h2>
                    
                    <div style="margin-top: 2rem;">
                        <div style="margin-bottom: 2rem;">
                            <h3>Innovation</h3>
                            <p style="color: #6b7280;">We constantly push boundaries to deliver cutting-edge solutions.</p>
                        </div>
                        
                        <div style="margin-bottom: 2rem;">
                            <h3>Excellence</h3>
                            <p style="color: #6b7280;">Quality is at the heart of everything we do.</p>
                        </div>
                        
                        <div style="margin-bottom: 2rem;">
                            <h3>Integrity</h3>
                            <p style="color: #6b7280;">We operate with honesty and transparency in all our dealings.</p>
                        </div>
                        
                        <div style="margin-bottom: 2rem;">
                            <h3>Customer Success</h3>
                            <p style="color: #6b7280;">Your success is our success. We're committed to your growth.</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 3rem; padding: 3rem; background: #f3f4f6; border-radius: 12px;">
                        <h2>Want to Join Our Team?</h2>
                        <p style="color: #6b7280; margin: 1rem 0;">We're always looking for talented individuals</p>
                        <a href="contact.html" class="btn btn-primary" style="margin-top: 1rem;">Get in Touch</a>
                    </div>
                </div>
            </div>
        </section>
        '''
    
    def generate_generic_page(self, page_name: str, business_info: Dict) -> str:
        """Generate generic page content"""
        return f'''
        <section style="padding: 4rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div class="container" style="text-align: center;">
                <h1>{page_name.replace('_', ' ').title()}</h1>
                <p style="font-size: 1.25rem; margin-top: 1rem;">
                    Discover our {page_name.replace('_', ' ')} offerings
                </p>
            </div>
        </section>
        
        <section style="padding: 4rem 0;">
            <div class="container">
                <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                    <h2>Coming Soon</h2>
                    <p style="font-size: 1.1rem; color: #6b7280; margin: 2rem 0;">
                        We're working hard to bring you amazing {page_name.replace('_', ' ')} content. 
                        Check back soon for updates!
                    </p>
                    <a href="contact.html" class="btn btn-primary">Contact Us for More Info</a>
                </div>
            </div>
        </section>
        '''
