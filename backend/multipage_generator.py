# Multi-Page Website Generator - SUPERIOR to Emergent
from typing import List, Dict
import re

class MultiPageGenerator:
    """Generate complete multi-page websites with navigation"""
    
    def __init__(self):
        self.pages = []
        self.navigation = []
    
    async def generate_multipage_website(self, user_prompt: str) -> Dict[str, str]:
        """Generate multiple pages based on user prompt"""
        
        # Analyze what pages are needed
        pages_needed = self._determine_pages(user_prompt)
        
        # Generate each page
        files = {}
        
        # Generate shared assets
        files['style.css'] = self._generate_css(user_prompt)
        files['script.js'] = self._generate_js()
        
        # Generate HTML pages
        for page in pages_needed:
            html = await self._generate_page(page, user_prompt, pages_needed)
            files[f'{page["file"]}.html'] = html
        
        # Generate package.json
        files['package.json'] = self._generate_package_json(user_prompt)
        
        # Generate README
        files['README.md'] = self._generate_readme(user_prompt)
        
        return files
    
    def _determine_pages(self, prompt: str) -> List[Dict]:
        """Determine what pages to generate based on prompt"""
        prompt_lower = prompt.lower()
        
        pages = [
            {'name': 'Home', 'file': 'index', 'priority': 1}
        ]
        
        # Add pages based on keywords
        if any(word in prompt_lower for word in ['portfolio', 'work', 'projects', 'gallery']):
            pages.append({'name': 'Portfolio', 'file': 'portfolio', 'priority': 2})
        
        if any(word in prompt_lower for word in ['about', 'team', 'company', 'who']):
            pages.append({'name': 'About', 'file': 'about', 'priority': 3})
        
        if any(word in prompt_lower for word in ['service', 'offering', 'what we do']):
            pages.append({'name': 'Services', 'file': 'services', 'priority': 4})
        
        if any(word in prompt_lower for word in ['blog', 'news', 'article']):
            pages.append({'name': 'Blog', 'file': 'blog', 'priority': 5})
        
        if any(word in prompt_lower for word in ['contact', 'reach', 'get in touch']):
            pages.append({'name': 'Contact', 'file': 'contact', 'priority': 6})
        else:
            # Always add contact page if not specified
            pages.append({'name': 'Contact', 'file': 'contact', 'priority': 6})
        
        return sorted(pages, key=lambda x: x['priority'])
    
    def _generate_navigation(self, pages: List[Dict], current_page: str) -> str:
        """Generate navigation HTML"""
        nav_items = []
        for page in pages:
            active = 'active' if page['file'] == current_page else ''
            nav_items.append(f'<a href="{page["file"]}.html" class="{active}">{page["name"]}</a>')
        
        return f'''
        <nav class="navbar">
            <div class="nav-container">
                <div class="logo">YourBrand</div>
                <div class="nav-links">
                    {' '.join(nav_items)}
                </div>
                <div class="mobile-menu-btn">☰</div>
            </div>
        </nav>
        '''
    
    async def _generate_page(self, page: Dict, prompt: str, all_pages: List[Dict]) -> str:
        """Generate individual page HTML"""
        
        page_content = self._get_page_content(page['file'], prompt)
        nav_html = self._generate_navigation(all_pages, page['file'])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{prompt}">
    <title>{page['name']} - Your Website</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {nav_html}
    
    {page_content}
    
    <footer class="footer">
        <div class="footer-container">
            <p>&copy; 2025 Your Company. All rights reserved.</p>
            <div class="social-links">
                <a href="#">Twitter</a>
                <a href="#">LinkedIn</a>
                <a href="#">GitHub</a>
            </div>
        </div>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>'''
    
    def _get_page_content(self, page_type: str, prompt: str) -> str:
        """Get content for specific page type"""
        
        if page_type == 'index':
            return f'''
            <section class="hero">
                <div class="hero-content">
                    <h1>{prompt}</h1>
                    <p>Beautiful, modern, and professional web solution</p>
                    <div class="hero-buttons">
                        <a href="contact.html" class="btn btn-primary">Get Started</a>
                        <a href="about.html" class="btn btn-secondary">Learn More</a>
                    </div>
                </div>
            </section>
            
            <section class="features">
                <div class="container">
                    <h2>Amazing Features</h2>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="icon">⚡</div>
                            <h3>Lightning Fast</h3>
                            <p>Optimized performance for the best user experience</p>
                        </div>
                        <div class="feature-card">
                            <div class="icon">🎨</div>
                            <h3>Beautiful Design</h3>
                            <p>Modern, clean interface that users love</p>
                        </div>
                        <div class="feature-card">
                            <div class="icon">🔒</div>
                            <h3>Secure</h3>
                            <p>Built with security best practices</p>
                        </div>
                    </div>
                </div>
            </section>
            '''
        
        elif page_type == 'about':
            return f'''
            <section class="page-hero">
                <div class="container">
                    <h1>About Us</h1>
                    <p>Learn more about our mission and team</p>
                </div>
            </section>
            
            <section class="about-content">
                <div class="container">
                    <div class="about-grid">
                        <div class="about-text">
                            <h2>Our Story</h2>
                            <p>We are passionate about creating amazing solutions that make a difference. Our team combines creativity, technology, and dedication to deliver exceptional results.</p>
                            <p>Founded with a vision to innovate and inspire, we've helped countless clients achieve their goals through our expertise and commitment.</p>
                        </div>
                        <div class="about-image">
                            <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800" alt="Team">
                        </div>
                    </div>
                </div>
            </section>
            '''
        
        elif page_type == 'services':
            return f'''
            <section class="page-hero">
                <div class="container">
                    <h1>Our Services</h1>
                    <p>Comprehensive solutions for your needs</p>
                </div>
            </section>
            
            <section class="services-content">
                <div class="container">
                    <div class="services-grid">
                        <div class="service-card">
                            <h3>Consultation</h3>
                            <p>Expert guidance tailored to your goals</p>
                            <a href="contact.html" class="btn">Learn More</a>
                        </div>
                        <div class="service-card">
                            <h3>Implementation</h3>
                            <p>Professional execution of your projects</p>
                            <a href="contact.html" class="btn">Learn More</a>
                        </div>
                        <div class="service-card">
                            <h3>Support</h3>
                            <p>Ongoing assistance and maintenance</p>
                            <a href="contact.html" class="btn">Learn More</a>
                        </div>
                    </div>
                </div>
            </section>
            '''
        
        elif page_type == 'portfolio':
            return f'''
            <section class="page-hero">
                <div class="container">
                    <h1>Our Work</h1>
                    <p>Showcasing our best projects</p>
                </div>
            </section>
            
            <section class="portfolio-grid-section">
                <div class="container">
                    <div class="portfolio-grid">
                        <div class="portfolio-item">
                            <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600" alt="Project 1">
                            <div class="portfolio-overlay">
                                <h3>Project Alpha</h3>
                                <p>Web Application</p>
                            </div>
                        </div>
                        <div class="portfolio-item">
                            <img src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600" alt="Project 2">
                            <div class="portfolio-overlay">
                                <h3>Project Beta</h3>
                                <p>Mobile App</p>
                            </div>
                        </div>
                        <div class="portfolio-item">
                            <img src="https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?w=600" alt="Project 3">
                            <div class="portfolio-overlay">
                                <h3>Project Gamma</h3>
                                <p>Design System</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            '''
        
        elif page_type == 'contact':
            return f'''
            <section class="page-hero">
                <div class="container">
                    <h1>Get In Touch</h1>
                    <p>We'd love to hear from you</p>
                </div>
            </section>
            
            <section class="contact-form-section">
                <div class="container">
                    <div class="contact-grid">
                        <div class="contact-info">
                            <h2>Contact Information</h2>
                            <div class="info-item">
                                <strong>Email:</strong> hello@yourcompany.com
                            </div>
                            <div class="info-item">
                                <strong>Phone:</strong> +1 (555) 123-4567
                            </div>
                            <div class="info-item">
                                <strong>Address:</strong> 123 Main St, City, Country
                            </div>
                        </div>
                        <form class="contact-form" id="contactForm">
                            <div class="form-group">
                                <input type="text" placeholder="Your Name" required>
                            </div>
                            <div class="form-group">
                                <input type="email" placeholder="Your Email" required>
                            </div>
                            <div class="form-group">
                                <textarea placeholder="Your Message" rows="5" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Send Message</button>
                            <div id="formSuccess" class="success-message" style="display: none;">
                                ✓ Message sent successfully!
                            </div>
                        </form>
                    </div>
                </div>
            </section>
            '''
        
        return '<section class="container"><h1>Page Content</h1></section>'
    
    def _generate_css(self, prompt: str) -> str:
        """Generate shared CSS file"""
        return '''/* Modern CSS for Multi-Page Website */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* Navigation */
.navbar {
    background: white;
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

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-links a {
    color: #333;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

.nav-links a:hover,
.nav-links a.active {
    color: #667eea;
}

.mobile-menu-btn {
    display: none;
    font-size: 1.5rem;
    cursor: pointer;
}

/* Hero Section */
.hero {
    min-height: 90vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 4rem 2rem;
}

.hero-content h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    animation: fadeInUp 1s ease;
}

.hero-content p {
    font-size: 1.3rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

/* Buttons */
.btn {
    padding: 1rem 2rem;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s;
    display: inline-block;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary {
    background: white;
    color: #667eea;
}

.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn-secondary:hover {
    background: white;
    color: #667eea;
}

/* Features */
.features {
    padding: 6rem 2rem;
    background: white;
}

.features h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    padding: 2rem;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s;
}

.feature-card:hover {
    transform: translateY(-10px);
}

.feature-card .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* Page Hero */
.page-hero {
    padding: 6rem 2rem 3rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
}

.page-hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* About */
.about-content {
    padding: 6rem 2rem;
}

.about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.about-image img {
    width: 100%;
    border-radius: 20px;
}

/* Services */
.services-content {
    padding: 6rem 2rem;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.service-card {
    padding: 3rem 2rem;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;
}

/* Portfolio */
.portfolio-grid-section {
    padding: 6rem 2rem;
}

.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.portfolio-item {
    position: relative;
    overflow: hidden;
    border-radius: 15px;
    cursor: pointer;
}

.portfolio-item img {
    width: 100%;
    display: block;
    transition: transform 0.3s;
}

.portfolio-item:hover img {
    transform: scale(1.1);
}

.portfolio-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
    color: white;
    padding: 2rem;
    transform: translateY(100%);
    transition: transform 0.3s;
}

.portfolio-item:hover .portfolio-overlay {
    transform: translateY(0);
}

/* Contact */
.contact-form-section {
    padding: 6rem 2rem;
}

.contact-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 4rem;
}

.contact-info {
    padding: 2rem;
}

.info-item {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 10px;
}

.contact-form {
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 20px;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
}

.success-message {
    margin-top: 1rem;
    padding: 1rem;
    background: #10b981;
    color: white;
    border-radius: 10px;
    text-align: center;
}

/* Footer */
.footer {
    background: #1a1a1a;
    color: white;
    padding: 3rem 2rem;
    text-align: center;
}

.footer-container {
    max-width: 1200px;
    margin: 0 auto;
}

.social-links {
    margin-top: 1rem;
    display: flex;
    gap: 2rem;
    justify-content: center;
}

.social-links a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

.social-links a:hover {
    color: #667eea;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive */
@media (max-width: 768px) {
    .nav-links {
        display: none;
    }
    
    .mobile-menu-btn {
        display: block;
    }
    
    .hero-content h1 {
        font-size: 2rem;
    }
    
    .about-grid,
    .contact-grid {
        grid-template-columns: 1fr;
    }
    
    .hero-buttons {
        flex-direction: column;
    }
}
'''
    
    def _generate_js(self) -> str:
        """Generate shared JavaScript file"""
        return '''// Interactive JavaScript for Multi-Page Website

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }
    
    // Contact Form Handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const successMessage = document.getElementById('formSuccess');
            if (successMessage) {
                successMessage.style.display = 'block';
                contactForm.reset();
                
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 5000);
            }
        });
    }
    
    // Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
'''
    
    def _generate_package_json(self, prompt: str) -> str:
        """Generate package.json for the project"""
        project_name = re.sub(r'[^a-z0-9-]', '-', prompt.lower()[:30])
        return f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "{prompt}",
  "main": "index.html",
  "scripts": {{
    "start": "python -m http.server 8000",
    "dev": "live-server"
  }},
  "keywords": ["website", "html", "css", "javascript"],
  "author": "Generated by AutoWebIQ",
  "license": "MIT",
  "devDependencies": {{
    "live-server": "^1.2.1"
  }}
}}
'''
    
    def _generate_readme(self, prompt: str) -> str:
        """Generate README.md documentation"""
        return f'''# {prompt}

Generated by AutoWebIQ - Professional Multi-Page Website

## 🚀 Features

- Multi-page structure with navigation
- Responsive design (mobile, tablet, desktop)
- Modern UI with smooth animations
- Working contact form
- SEO-friendly structure
- Production-ready code

## 📁 File Structure

```
.
├── index.html          # Home page
├── about.html          # About page
├── services.html       # Services page
├── portfolio.html      # Portfolio page
├── contact.html        # Contact page
├── style.css           # Shared CSS styles
├── script.js           # Shared JavaScript
├── package.json        # Project configuration
└── README.md          # This file
```

## 🛠️ How to Run

### Option 1: Simple Python Server
```bash
python -m http.server 8000
```
Then open http://localhost:8000

### Option 2: Live Server (with hot reload)
```bash
npm install
npm run dev
```

### Option 3: Just Open Files
Simply open `index.html` in your browser

## 🌐 Deploy

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
Drag and drop the folder to netlify.com/drop

### Deploy to GitHub Pages
1. Create a GitHub repository
2. Push this code
3. Enable GitHub Pages in repository settings

## 📝 Customization

- Edit `style.css` to change colors, fonts, layouts
- Modify HTML files to update content
- Update `script.js` for additional functionality

## 💎 What's Included

✅ Professional navigation with smooth scroll
✅ Mobile-responsive hamburger menu
✅ Hero section with call-to-action buttons
✅ Features/services showcase
✅ Portfolio gallery with hover effects
✅ Working contact form with validation
✅ Professional footer with social links
✅ Modern animations and transitions
✅ SEO-friendly meta tags
✅ Cross-browser compatible

## 📧 Contact Form

The contact form includes client-side validation. To make it actually send emails:

1. Use FormSpree: Add `action="https://formspree.io/f/YOUR_ID"`
2. Use EmailJS: Follow their integration guide
3. Use Netlify Forms: Add `netlify` attribute to form

## 🎨 Credits

- Images from Unsplash
- Icons from Unicode emoji
- Generated by AutoWebIQ - The Best AI Website Builder

---

Built with ❤️ by AutoWebIQ
'''
