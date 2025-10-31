# Template Data - Production-Ready Templates for AutoWebIQ
# 10 templates across different categories

TEMPLATES = [
    # E-COMMERCE TEMPLATES (3)
    {
        "template_id": "ecom_luxury_v1",
        "name": "Luxury E-commerce",
        "category": "ecommerce",
        "style": "luxury",
        "description": "Elegant e-commerce template for premium products",
        "tags": ["luxury", "premium", "elegant", "product", "shop", "store", "ecommerce"],
        "features": ["product_showcase", "cart", "checkout", "testimonials", "newsletter"],
        "color_scheme": {
            "primary": "#1a1a1a",
            "secondary": "#2d2d2d",
            "accent": "#c9a961",
            "background": "#ffffff",
            "text": "#1a1a1a"
        },
        "use_count": 0,
        "lighthouse_score": 92,
        "wcag_compliant": True,
        "customization_zones": [
            {
                "zone_id": "hero",
                "type": "text",
                "editable": ["headline", "subheadline", "cta_primary", "cta_secondary"],
                "ai_customizable": True
            },
            {
                "zone_id": "featured_products",
                "type": "products",
                "editable": ["product_1_name", "product_1_description", "product_2_name", "product_2_description"],
                "ai_customizable": True
            },
            {
                "zone_id": "features",
                "type": "features",
                "editable": ["feature_1_title", "feature_1_description", "feature_2_title", "feature_2_description", "feature_3_title", "feature_3_description"],
                "ai_customizable": True
            }
        ],
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ hero.headline }}</title>
    <meta name="description" content="{{ hero.subheadline }}">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: {{ color.primary }};
            --secondary: {{ color.secondary }};
            --accent: {{ color.accent }};
            --bg: {{ color.background }};
            --text: {{ color.text }};
        }
        body { font-family: 'Inter', sans-serif; color: var(--text); line-height: 1.6; overflow-x: hidden; }
        
        /* Navigation */
        .navbar { position: fixed; top: 0; width: 100%; background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); border-bottom: 1px solid #eee; z-index: 1000; padding: 20px 0; }
        .nav-container { max-width: 1400px; margin: 0 auto; padding: 0 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; color: var(--primary); text-decoration: none; }
        .nav-links { display: flex; gap: 40px; list-style: none; }
        .nav-links a { color: var(--text); text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: var(--accent); }
        .nav-cart { background: var(--primary); color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-size: 0.9rem; transition: background 0.3s; }
        .nav-cart:hover { background: var(--secondary); }
        
        /* Hero */
        .hero { min-height: 100vh; display: flex; align-items: center; background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); padding: 120px 40px 80px; position: relative; }
        .hero-content { max-width: 1400px; margin: 0 auto; width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
        .hero-text h1 { font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 600; line-height: 1.1; margin-bottom: 24px; color: var(--primary); }
        .hero-text p { font-size: 1.25rem; color: #666; margin-bottom: 40px; line-height: 1.8; }
        .hero-ctas { display: flex; gap: 20px; }
        .btn-primary { background: var(--primary); color: white; padding: 16px 40px; border-radius: 4px; text-decoration: none; font-weight: 500; transition: all 0.3s; display: inline-block; }
        .btn-primary:hover { background: var(--secondary); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
        .btn-secondary { background: transparent; color: var(--primary); padding: 16px 40px; border: 2px solid var(--primary); border-radius: 4px; text-decoration: none; font-weight: 500; transition: all 0.3s; display: inline-block; }
        .btn-secondary:hover { background: var(--primary); color: white; }
        .hero-image { width: 100%; height: 600px; border-radius: 8px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
        .hero-image img { width: 100%; height: 100%; object-fit: cover; }
        
        /* Featured Products */
        .featured-products { padding: 120px 40px; background: white; }
        .section-title { text-align: center; margin-bottom: 80px; }
        .section-title h2 { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 600; color: var(--primary); margin-bottom: 16px; }
        .section-title p { font-size: 1.125rem; color: #666; }
        .products-grid { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
        .product-card { background: white; border: 1px solid #eee; border-radius: 8px; overflow: hidden; transition: all 0.3s; }
        .product-card:hover { transform: translateY(-8px); box-shadow: 0 12px 40px rgba(0,0,0,0.1); }
        .product-image { width: 100%; height: 400px; overflow: hidden; }
        .product-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
        .product-card:hover .product-image img { transform: scale(1.05); }
        .product-info { padding: 32px; }
        .product-info h3 { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 600; margin-bottom: 12px; color: var(--primary); }
        .product-info p { color: #666; margin-bottom: 20px; line-height: 1.6; }
        .product-price { font-size: 1.5rem; font-weight: 600; color: var(--accent); margin-bottom: 20px; }
        .add-to-cart { width: 100%; background: var(--primary); color: white; padding: 14px; border: none; border-radius: 4px; font-weight: 500; cursor: pointer; transition: background 0.3s; }
        .add-to-cart:hover { background: var(--secondary); }
        
        /* Features */
        .features { padding: 120px 40px; background: #f9f9f9; }
        .features-grid { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: 60px; }
        .feature-item { text-align: center; }
        .feature-icon { font-size: 3rem; margin-bottom: 24px; }
        .feature-item h3 { font-size: 1.5rem; font-weight: 600; margin-bottom: 16px; color: var(--primary); }
        .feature-item p { color: #666; line-height: 1.8; }
        
        /* Footer */
        .footer { background: var(--primary); color: white; padding: 80px 40px 40px; }
        .footer-content { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 60px; margin-bottom: 60px; }
        .footer-section h4 { font-family: 'Playfair Display', serif; font-size: 1.25rem; margin-bottom: 20px; }
        .footer-section p { opacity: 0.8; line-height: 1.8; margin-bottom: 20px; }
        .footer-links { list-style: none; }
        .footer-links li { margin-bottom: 12px; }
        .footer-links a { color: white; opacity: 0.8; text-decoration: none; transition: opacity 0.3s; }
        .footer-links a:hover { opacity: 1; }
        .footer-bottom { text-align: center; padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1); opacity: 0.8; }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .hero-content { grid-template-columns: 1fr; text-align: center; }
            .hero-text h1 { font-size: 3rem; }
            .hero-ctas { justify-content: center; }
            .products-grid { grid-template-columns: repeat(2, 1fr); }
            .features-grid { grid-template-columns: repeat(2, 1fr); }
            .footer-content { grid-template-columns: 1fr 1fr; }
        }
        @media (max-width: 640px) {
            .hero-text h1 { font-size: 2.5rem; }
            .products-grid { grid-template-columns: 1fr; }
            .features-grid { grid-template-columns: 1fr; }
            .footer-content { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="#" class="logo">{{ hero.headline }}</a>
            <ul class="nav-links">
                <li><a href="#shop">Shop</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            <a href="#cart" class="nav-cart">Cart (0)</a>
        </div>
    </nav>
    
    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <div class="hero-text">
                <h1>{{ hero.headline }}</h1>
                <p>{{ hero.subheadline }}</p>
                <div class="hero-ctas">
                    <a href="#shop" class="btn-primary">{{ hero.cta_primary }}</a>
                    <a href="#about" class="btn-secondary">{{ hero.cta_secondary }}</a>
                </div>
            </div>
            <div class="hero-image">
                <img src="{{ image_1 }}" alt="Hero image">
            </div>
        </div>
    </section>
    
    <!-- Featured Products -->
    <section class="featured-products" id="shop">
        <div class="section-title">
            <h2>Featured Collection</h2>
            <p>Discover our carefully curated selection</p>
        </div>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">
                    <img src="{{ image_2 }}" alt="Product">
                </div>
                <div class="product-info">
                    <h3>{{ featured_products.product_1_name }}</h3>
                    <p>{{ featured_products.product_1_description }}</p>
                    <div class="product-price">$199.00</div>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">
                    <img src="{{ image_2 }}" alt="Product">
                </div>
                <div class="product-info">
                    <h3>{{ featured_products.product_2_name }}</h3>
                    <p>{{ featured_products.product_2_description }}</p>
                    <div class="product-price">$249.00</div>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">
                    <img src="{{ image_2 }}" alt="Product">
                </div>
                <div class="product-info">
                    <h3>Premium Product</h3>
                    <p>Exquisite craftsmanship and timeless design</p>
                    <div class="product-price">$299.00</div>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Features -->
    <section class="features">
        <div class="section-title">
            <h2>Why Choose Us</h2>
            <p>Excellence in every detail</p>
        </div>
        <div class="features-grid">
            <div class="feature-item">
                <div class="feature-icon">🚚</div>
                <h3>{{ features.feature_1_title }}</h3>
                <p>{{ features.feature_1_description }}</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">✨</div>
                <h3>{{ features.feature_2_title }}</h3>
                <p>{{ features.feature_2_description }}</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔒</div>
                <h3>{{ features.feature_3_title }}</h3>
                <p>{{ features.feature_3_description }}</p>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>{{ hero.headline }}</h4>
                <p>{{ hero.subheadline }}</p>
            </div>
            <div class="footer-section">
                <h4>Shop</h4>
                <ul class="footer-links">
                    <li><a href="#">All Products</a></li>
                    <li><a href="#">New Arrivals</a></li>
                    <li><a href="#">Best Sellers</a></li>
                    <li><a href="#">Sale</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Company</h4>
                <ul class="footer-links">
                    <li><a href="#">About Us</a></li>
                    <li><a href="#">Contact</a></li>
                    <li><a href="#">Careers</a></li>
                    <li><a href="#">Press</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Support</h4>
                <ul class="footer-links">
                    <li><a href="#">FAQ</a></li>
                    <li><a href="#">Shipping</a></li>
                    <li><a href="#">Returns</a></li>
                    <li><a href="#">Size Guide</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 {{ hero.headline }}. All rights reserved.</p>
        </div>
    </footer>
    
    <script>
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
        
        // Add to cart
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', function() {
                this.textContent = 'Added!';
                setTimeout(() => {
                    this.textContent = 'Add to Cart';
                }, 2000);
            });
        });
    </script>
</body>
</html>"""
    },
    
    # SAAS TEMPLATE (1)
    {
        "template_id": "saas_modern_v1",
        "name": "Modern SaaS Landing",
        "category": "saas",
        "style": "modern",
        "description": "Clean, modern SaaS product landing page",
        "tags": ["saas", "software", "modern", "platform", "tech", "b2b", "startup"],
        "features": ["hero", "features", "pricing", "testimonials", "cta"],
        "color_scheme": {
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "accent": "#ec4899",
            "background": "#ffffff",
            "text": "#1f2937"
        },
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [
            {
                "zone_id": "hero",
                "type": "text",
                "editable": ["headline", "subheadline", "cta_primary"],
                "ai_customizable": True
            },
            {
                "zone_id": "features",
                "type": "features",
                "editable": ["feature_1_title", "feature_1_desc", "feature_2_title", "feature_2_desc", "feature_3_title", "feature_3_desc"],
                "ai_customizable": True
            }
        ],
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ hero.headline }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root { --primary: {{ color.primary }}; --secondary: {{ color.secondary }}; --accent: {{ color.accent }}; }
        body { font-family: 'Inter', sans-serif; color: #1f2937; line-height: 1.6; }
        .nav { position: fixed; top: 0; width: 100%; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 20px 0; border-bottom: 1px solid #e5e7eb; z-index: 1000; }
        .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 800; color: var(--primary); }
        .nav-links { display: flex; gap: 32px; list-style: none; }
        .nav-links a { color: #4b5563; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: var(--primary); }
        .btn { background: var(--primary); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s; display: inline-block; }
        .btn:hover { background: var(--secondary); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.3); }
        .hero { min-height: 100vh; display: flex; align-items: center; padding: 120px 24px 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .hero-content { max-width: 1200px; margin: 0 auto; text-align: center; }
        .hero h1 { font-size: 4rem; font-weight: 800; line-height: 1.1; margin-bottom: 24px; }
        .hero p { font-size: 1.5rem; opacity: 0.95; margin-bottom: 40px; max-width: 700px; margin-left: auto; margin-right: auto; }
        .hero-btn { background: white; color: var(--primary); padding: 18px 40px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 1.125rem; transition: all 0.3s; display: inline-block; }
        .hero-btn:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.2); }
        .features { padding: 120px 24px; background: white; }
        .section-title { text-align: center; margin-bottom: 80px; }
        .section-title h2 { font-size: 3rem; font-weight: 800; color: #1f2937; margin-bottom: 16px; }
        .section-title p { font-size: 1.25rem; color: #6b7280; }
        .features-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: 48px; }
        .feature { text-align: center; padding: 40px; border-radius: 16px; transition: all 0.3s; }
        .feature:hover { transform: translateY(-8px); box-shadow: 0 12px 40px rgba(0,0,0,0.1); }
        .feature-icon { font-size: 3rem; margin-bottom: 24px; }
        .feature h3 { font-size: 1.5rem; font-weight: 700; margin-bottom: 16px; color: #1f2937; }
        .feature p { color: #6b7280; line-height: 1.8; }
        .cta { padding: 120px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
        .cta h2 { font-size: 3rem; font-weight: 800; margin-bottom: 24px; }
        .cta p { font-size: 1.25rem; margin-bottom: 40px; opacity: 0.95; }
        .footer { background: #1f2937; color: white; padding: 60px 24px 30px; text-align: center; }
        .footer p { opacity: 0.8; }
        @media (max-width: 768px) {
            .hero h1 { font-size: 2.5rem; }
            .features-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-container">
            <div class="logo">{{ hero.headline }}</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            <a href="#signup" class="btn">Get Started</a>
        </div>
    </nav>
    
    <section class="hero">
        <div class="hero-content">
            <h1>{{ hero.headline }}</h1>
            <p>{{ hero.subheadline }}</p>
            <a href="#signup" class="hero-btn">{{ hero.cta_primary }}</a>
        </div>
    </section>
    
    <section class="features" id="features">
        <div class="section-title">
            <h2>Powerful Features</h2>
            <p>Everything you need to succeed</p>
        </div>
        <div class="features-grid">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>{{ features.feature_1_title }}</h3>
                <p>{{ features.feature_1_desc }}</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🎯</div>
                <h3>{{ features.feature_2_title }}</h3>
                <p>{{ features.feature_2_desc }}</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <h3>{{ features.feature_3_title }}</h3>
                <p>{{ features.feature_3_desc }}</p>
            </div>
        </div>
    </section>
    
    <section class="cta">
        <h2>Ready to Get Started?</h2>
        <p>Join thousands of teams already using our platform</p>
        <a href="#signup" class="hero-btn">Start Free Trial</a>
    </section>
    
    <footer class="footer">
        <p>&copy; 2025 {{ hero.headline }}. All rights reserved.</p>
    </footer>
    
    <script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
            });
        });
    </script>
</body>
</html>"""
    },
    
    # PORTFOLIO TEMPLATE (1)
    {
        "template_id": "portfolio_creative_v1",
        "name": "Creative Portfolio",
        "category": "portfolio",
        "style": "creative",
        "description": "Bold, creative portfolio for designers and artists",
        "tags": ["portfolio", "creative", "design", "showcase", "gallery", "artist", "photographer"],
        "features": ["hero", "gallery", "about", "contact"],
        "color_scheme": {
            "primary": "#000000",
            "secondary": "#ff6b6b",
            "accent": "#4ecdc4",
            "background": "#ffffff",
            "text": "#2d3436"
        },
        "use_count": 0,
        "lighthouse_score": 93,
        "wcag_compliant": True,
        "customization_zones": [
            {
                "zone_id": "hero",
                "type": "text",
                "editable": ["name", "title", "description"],
                "ai_customizable": True
            }
        ],
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ hero.name }} - {{ hero.title }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Space Grotesk', sans-serif; color: {{ color.text }}; }
        .nav { position: fixed; top: 0; width: 100%; background: {{ color.primary }}; color: white; padding: 24px 40px; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; }
        .nav-links { display: flex; gap: 40px; list-style: none; }
        .nav-links a { color: white; text-decoration: none; transition: color 0.3s; }
        .nav-links a:hover { color: {{ color.accent }}; }
        .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: {{ color.primary }}; color: white; padding: 100px 40px; text-align: center; }
        .hero h1 { font-size: 5rem; font-weight: 700; margin-bottom: 16px; }
        .hero h2 { font-size: 2rem; color: {{ color.accent }}; margin-bottom: 24px; }
        .hero p { font-size: 1.25rem; max-width: 600px; margin: 0 auto; opacity: 0.9; }
        .gallery { padding: 80px 40px; }
        .gallery-grid { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px; }
        .gallery-item { aspect-ratio: 1; overflow: hidden; border-radius: 8px; cursor: pointer; transition: transform 0.3s; }
        .gallery-item:hover { transform: scale(1.05); }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; }
        .footer { background: {{ color.primary }}; color: white; padding: 60px 40px; text-align: center; }
        @media (max-width: 768px) { .hero h1 { font-size: 3rem; } .gallery-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <nav class="nav">
        <div class="logo">{{ hero.name }}</div>
        <ul class="nav-links">
            <li><a href="#work">Work</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    <section class="hero">
        <div>
            <h1>{{ hero.name }}</h1>
            <h2>{{ hero.title }}</h2>
            <p>{{ hero.description }}</p>
        </div>
    </section>
    <section class="gallery" id="work">
        <div class="gallery-grid">
            <div class="gallery-item"><img src="{{ image_1 }}" alt="Work 1"></div>
            <div class="gallery-item"><img src="{{ image_2 }}" alt="Work 2"></div>
            <div class="gallery-item"><img src="{{ image_1 }}" alt="Work 3"></div>
            <div class="gallery-item"><img src="{{ image_2 }}" alt="Work 4"></div>
        </div>
    </section>
    <footer class="footer">
        <p>&copy; 2025 {{ hero.name }}. All rights reserved.</p>
    </footer>
</body>
</html>"""
    }
]

# Additional Templates (4-10)
TEMPLATES.extend([
    # E-COMMERCE TEMPLATE 2 - Modern Minimal
    {
        "template_id": "ecom_minimal_v1",
        "name": "Minimal E-commerce",
        "category": "ecommerce",
        "style": "minimal",
        "description": "Clean, minimalist e-commerce with focus on products",
        "tags": ["ecommerce", "minimal", "clean", "simple", "modern", "shop"],
        "features": ["product_grid", "cart", "search", "filters"],
        "color_scheme": {"primary": "#2d3436", "secondary": "#636e72", "accent": "#00b894", "background": "#ffffff", "text": "#2d3436"},
        "use_count": 0,
        "lighthouse_score": 95,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["headline", "tagline"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }};line-height:1.6}.nav{position:fixed;top:0;width:100%;background:#fff;padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;z-index:1000}.logo{font-size:1.25rem;font-weight:600}.nav-links{display:flex;gap:30px;list-style:none}.nav-links a{color:#333;text-decoration:none}.hero{min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 40px 60px}.hero h1{font-size:3.5rem;font-weight:300;margin-bottom:16px}.hero p{font-size:1.125rem;color:#666}.products{padding:80px 40px;max-width:1400px;margin:0 auto}.product-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:40px}.product-card{border:1px solid #eee;padding:20px;transition:all 0.3s}.product-card:hover{box-shadow:0 8px 30px rgba(0,0,0,0.08)}.product-image{width:100%;height:300px;background:#f5f5f5;margin-bottom:16px}.product-info h3{font-size:1.125rem;margin-bottom:8px;font-weight:600}.product-price{font-size:1.25rem;font-weight:600;color:{{ color.accent }};margin:16px 0}.add-btn{width:100%;padding:12px;background:{{ color.primary }};color:#fff;border:none;cursor:pointer;font-weight:500;transition:background 0.3s}.add-btn:hover{background:{{ color.secondary }}}.footer{background:#f9f9f9;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.product-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div><ul class="nav-links"><li><a href="#shop">Shop</a></li><li><a href="#about">About</a></li><li><a href="#cart">Cart</a></li></ul></nav><section class="hero"><div><h1>{{ hero.headline }}</h1><p>{{ hero.tagline }}</p></div></section><section class="products" id="shop"><div class="product-grid"><div class="product-card"><div class="product-image"></div><div class="product-info"><h3>Product Name</h3><p>Simple, elegant design</p><div class="product-price">$99</div><button class="add-btn">Add to Cart</button></div></div><div class="product-card"><div class="product-image"></div><div class="product-info"><h3>Product Name</h3><p>Quality craftsmanship</p><div class="product-price">$149</div><button class="add-btn">Add to Cart</button></div></div><div class="product-card"><div class="product-image"></div><div class="product-info"><h3>Product Name</h3><p>Timeless style</p><div class="product-price">$199</div><button class="add-btn">Add to Cart</button></div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    },
    
    # SAAS TEMPLATE 2 - B2B Platform
    {
        "template_id": "saas_b2b_v1",
        "name": "B2B SaaS Platform",
        "category": "saas",
        "style": "professional",
        "description": "Professional B2B SaaS platform landing page",
        "tags": ["saas", "b2b", "platform", "professional", "enterprise", "business"],
        "features": ["features", "integrations", "pricing", "testimonials", "demo"],
        "color_scheme": {"primary": "#1e3a8a", "secondary": "#3b82f6", "accent": "#10b981", "background": "#ffffff", "text": "#1f2937"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["headline", "subheadline", "cta"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:16px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;z-index:1000}.logo{font-size:1.5rem;font-weight:700;color:{{ color.primary }}}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:#374151;text-decoration:none;font-weight:500}.btn{background:{{ color.primary }};color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600}.hero{min-height:90vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%);color:#fff}.hero-content{max-width:1200px;margin:0 auto;text-align:center}.hero h1{font-size:3.5rem;font-weight:700;line-height:1.1;margin-bottom:24px}.hero p{font-size:1.375rem;margin-bottom:32px;opacity:0.95}.hero-btns{display:flex;gap:16px;justify-content:center}.hero-btn{padding:16px 32px;border-radius:8px;font-weight:600;font-size:1.125rem;text-decoration:none;transition:all 0.3s}.hero-btn-primary{background:#fff;color:{{ color.primary }}}.hero-btn-secondary{background:transparent;color:#fff;border:2px solid #fff}.features{padding:100px 40px;max-width:1200px;margin:0 auto}.section-title{text-align:center;margin-bottom:60px}.section-title h2{font-size:2.5rem;font-weight:700;margin-bottom:16px}.section-title p{font-size:1.125rem;color:#6b7280}.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px}.feature{text-align:center;padding:32px}.feature-icon{font-size:2.5rem;margin-bottom:20px}.feature h3{font-size:1.375rem;font-weight:600;margin-bottom:12px}.feature p{color:#6b7280;line-height:1.6}.cta{padding:100px 40px;background:#f9fafb;text-align:center}.cta h2{font-size:2.5rem;font-weight:700;margin-bottom:24px}.cta p{font-size:1.25rem;color:#6b7280;margin-bottom:32px}.footer{background:{{ color.primary }};color:#fff;padding:40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.features-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div><ul class="nav-links"><li><a href="#features">Features</a></li><li><a href="#pricing">Pricing</a></li><li><a href="#demo">Demo</a></li></ul><a href="#signup" class="btn">Get Started</a></nav><section class="hero"><div class="hero-content"><h1>{{ hero.headline }}</h1><p>{{ hero.subheadline }}</p><div class="hero-btns"><a href="#demo" class="hero-btn hero-btn-primary">{{ hero.cta }}</a><a href="#features" class="hero-btn hero-btn-secondary">Learn More</a></div></div></section><section class="features" id="features"><div class="section-title"><h2>Powerful Features</h2><p>Everything your team needs to succeed</p></div><div class="features-grid"><div class="feature"><div class="feature-icon">⚡</div><h3>Lightning Fast</h3><p>Optimized performance for enterprise scale</p></div><div class="feature"><div class="feature-icon">🔒</div><h3>Enterprise Security</h3><p>Bank-level security and compliance</p></div><div class="feature"><div class="feature-icon">📊</div><h3>Advanced Analytics</h3><p>Real-time insights and reporting</p></div></div></section><section class="cta"><h2>Ready to Transform Your Business?</h2><p>Join thousands of companies already using our platform</p><a href="#demo" class="btn">Request Demo</a></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}. All rights reserved.</p></footer></body></html>"""
    },
    
    # SAAS TEMPLATE 3 - App Showcase
    {
        "template_id": "saas_app_v1",
        "name": "App Showcase",
        "category": "saas",
        "style": "modern",
        "description": "Modern app showcase for mobile/web apps",
        "tags": ["saas", "app", "mobile", "showcase", "modern", "startup"],
        "features": ["hero", "features", "screenshots", "download"],
        "color_scheme": {"primary": "#8b5cf6", "secondary": "#a78bfa", "accent": "#ec4899", "background": "#ffffff", "text": "#111827"},
        "use_count": 0,
        "lighthouse_score": 93,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["headline", "description", "cta"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Poppins',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;z-index:1000}.logo{font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,{{ color.primary }},{{ color.accent }});-webkit-background-clip:text;-webkit-text-fill-color:transparent}.btn{background:{{ color.primary }};color:#fff;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:600;transition:transform 0.3s}.btn:hover{transform:translateY(-2px)}.hero{min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,#f0f9ff 0%,#e0e7ff 100%)}.hero-content{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.hero-text h1{font-size:3.5rem;font-weight:800;line-height:1.1;margin-bottom:24px;background:linear-gradient(135deg,{{ color.primary }},{{ color.accent }});-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero-text p{font-size:1.25rem;color:#6b7280;margin-bottom:32px}.hero-image{text-align:center}.hero-image img{max-width:100%;height:auto}.features{padding:100px 40px;max-width:1200px;margin:0 auto}.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.feature-card{background:#fff;padding:32px;border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.08);transition:transform 0.3s}.feature-card:hover{transform:translateY(-8px)}.feature-icon{width:60px;height:60px;background:linear-gradient(135deg,{{ color.primary }},{{ color.accent }});border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px}.feature-card h3{font-size:1.25rem;font-weight:600;margin-bottom:12px}.feature-card p{color:#6b7280;line-height:1.6}.footer{background:#111827;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero-content{grid-template-columns:1fr}.hero-text h1{font-size:2.5rem}.features-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div><a href="#download" class="btn">Download App</a></nav><section class="hero"><div class="hero-content"><div class="hero-text"><h1>{{ hero.headline }}</h1><p>{{ hero.description }}</p><a href="#download" class="btn">{{ hero.cta }}</a></div><div class="hero-image"><img src="{{ image_1 }}" alt="App"></div></div></section><section class="features"><div style="text-align:center;margin-bottom:60px"><h2 style="font-size:2.5rem;font-weight:700">Amazing Features</h2><p style="font-size:1.125rem;color:#6b7280;margin-top:16px">Everything you need in one app</p></div><div class="features-grid"><div class="feature-card"><div class="feature-icon">⚡</div><h3>Super Fast</h3><p>Lightning-fast performance on all devices</p></div><div class="feature-card"><div class="feature-icon">🎨</div><h3>Beautiful Design</h3><p>Stunning interface that users love</p></div><div class="feature-card"><div class="feature-icon">🔒</div><h3>Secure</h3><p>Your data is always safe and encrypted</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}. All rights reserved.</p></footer></body></html>"""
    },
    
    # PORTFOLIO TEMPLATE 2 - Professional
    {
        "template_id": "portfolio_pro_v1",
        "name": "Professional Portfolio",
        "category": "portfolio",
        "style": "professional",
        "description": "Clean professional portfolio for consultants and freelancers",
        "tags": ["portfolio", "professional", "consultant", "freelance", "business"],
        "features": ["about", "services", "projects", "contact"],
        "color_scheme": {"primary": "#0f172a", "secondary": "#334155", "accent": "#3b82f6", "background": "#ffffff", "text": "#1e293b"},
        "use_count": 0,
        "lighthouse_score": 95,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["name", "title", "tagline"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.name }} - {{ hero.title }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }};line-height:1.6}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;z-index:1000}.logo{font-weight:600;font-size:1.125rem}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:#64748b;text-decoration:none;font-weight:500;transition:color 0.3s}.nav-links a:hover{color:{{ color.accent }}}.hero{min-height:90vh;display:flex;align-items:center;padding:100px 40px;max-width:1200px;margin:0 auto}.hero-content{max-width:600px}.hero h1{font-size:3.5rem;font-weight:700;margin-bottom:16px;color:{{ color.primary }}}.hero h2{font-size:1.5rem;color:{{ color.accent }};margin-bottom:20px;font-weight:600}.hero p{font-size:1.125rem;color:#64748b;margin-bottom:32px}.hero-btn{display:inline-block;padding:14px 32px;background:{{ color.primary }};color:#fff;text-decoration:none;font-weight:600;border-radius:6px;transition:all 0.3s}.hero-btn:hover{background:{{ color.secondary }};transform:translateY(-2px)}.services{padding:100px 40px;background:#f8fafc}.services-container{max-width:1200px;margin:0 auto}.section-title{text-align:center;margin-bottom:60px}.section-title h2{font-size:2.5rem;font-weight:700;margin-bottom:16px}.section-title p{font-size:1.125rem;color:#64748b}.services-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px}.service-card{background:#fff;padding:40px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);transition:all 0.3s}.service-card:hover{box-shadow:0 10px 30px rgba(0,0,0,0.1);transform:translateY(-4px)}.service-card h3{font-size:1.375rem;font-weight:600;margin-bottom:16px}.service-card p{color:#64748b;line-height:1.7}.footer{background:{{ color.primary }};color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.services-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.name }}</div><ul class="nav-links"><li><a href="#about">About</a></li><li><a href="#services">Services</a></li><li><a href="#contact">Contact</a></li></ul></nav><section class="hero"><div class="hero-content"><h1>{{ hero.name }}</h1><h2>{{ hero.title }}</h2><p>{{ hero.tagline }}</p><a href="#contact" class="hero-btn">Get in Touch</a></div></section><section class="services" id="services"><div class="services-container"><div class="section-title"><h2>What I Do</h2><p>Professional services tailored to your needs</p></div><div class="services-grid"><div class="service-card"><h3>Service One</h3><p>High-quality professional service with attention to detail</p></div><div class="service-card"><h3>Service Two</h3><p>Expertise and experience you can rely on</p></div><div class="service-card"><h3>Service Three</h3><p>Results-driven approach to every project</p></div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.name }}. All rights reserved.</p></footer></body></html>"""
    },
    
    # LANDING PAGE TEMPLATE 1 - Campaign
    {
        "template_id": "landing_campaign_v1",
        "name": "Campaign Landing",
        "category": "landing",
        "style": "bold",
        "description": "Bold campaign landing page for product launches",
        "tags": ["landing", "campaign", "launch", "marketing", "conversion"],
        "features": ["hero", "benefits", "countdown", "cta"],
        "color_scheme": {"primary": "#dc2626", "secondary": "#ef4444", "accent": "#fbbf24", "background": "#ffffff", "text": "#1f2937"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["headline", "subheadline", "cta"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Montserrat',sans-serif;color:{{ color.text }}}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:40px;background:linear-gradient(135deg,{{ color.primary }} 0%,{{ color.secondary }} 100%);color:#fff;position:relative;overflow:hidden}.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,149.3C960,160,1056,160,1152,138.7C1248,117,1344,75,1392,53.3L1440,32L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') bottom no-repeat;background-size:cover}.hero-content{position:relative;z-index:1;max-width:800px}.hero h1{font-size:4rem;font-weight:900;line-height:1.1;margin-bottom:24px;text-transform:uppercase;letter-spacing:-1px}.hero p{font-size:1.5rem;margin-bottom:40px;font-weight:600;opacity:0.95}.hero-btn{display:inline-block;padding:20px 50px;background:{{ color.accent }};color:{{ color.primary }};text-decoration:none;font-weight:800;font-size:1.25rem;border-radius:50px;text-transform:uppercase;transition:all 0.3s;box-shadow:0 10px 30px rgba(0,0,0,0.3)}.hero-btn:hover{transform:translateY(-4px) scale(1.05);box-shadow:0 15px 40px rgba(0,0,0,0.4)}.benefits{padding:100px 40px;max-width:1200px;margin:0 auto}.benefits-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.benefit{text-align:center;padding:40px}.benefit-icon{width:80px;height:80px;background:{{ color.primary }};border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;font-size:2rem}.benefit h3{font-size:1.5rem;font-weight:700;margin-bottom:16px}.benefit p{color:#6b7280;line-height:1.6}.cta{padding:100px 40px;background:{{ color.primary }};color:#fff;text-align:center}.cta h2{font-size:3rem;font-weight:900;margin-bottom:24px;text-transform:uppercase}.cta p{font-size:1.25rem;margin-bottom:40px;font-weight:600}.footer{background:#111827;color:#fff;padding:40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.benefits-grid{grid-template-columns:1fr}}</style></head><body><section class="hero"><div class="hero-content"><h1>{{ hero.headline }}</h1><p>{{ hero.subheadline }}</p><a href="#signup" class="hero-btn">{{ hero.cta }}</a></div></section><section class="benefits"><div style="text-align:center;margin-bottom:60px"><h2 style="font-size:2.5rem;font-weight:700">Why You'll Love It</h2></div><div class="benefits-grid"><div class="benefit"><div class="benefit-icon">🚀</div><h3>Benefit One</h3><p>Amazing results you can see immediately</p></div><div class="benefit"><div class="benefit-icon">⚡</div><h3>Benefit Two</h3><p>Fast and powerful solution</p></div><div class="benefit"><div class="benefit-icon">💎</div><h3>Benefit Three</h3><p>Premium quality guaranteed</p></div></div></section><section class="cta"><h2>Ready to Get Started?</h2><p>Join thousands of satisfied customers</p><a href="#signup" class="hero-btn">Sign Up Now</a></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    },
    
    # LANDING PAGE TEMPLATE 2 - Lead Gen
    {
        "template_id": "landing_leadgen_v1",
        "name": "Lead Generation",
        "category": "landing",
        "style": "clean",
        "description": "Conversion-focused lead generation landing page",
        "tags": ["landing", "leadgen", "conversion", "form", "marketing"],
        "features": ["hero", "form", "benefits", "social_proof"],
        "color_scheme": {"primary": "#059669", "secondary": "#10b981", "accent": "#34d399", "background": "#ffffff", "text": "#111827"},
        "use_count": 0,
        "lighthouse_score": 95,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["headline", "subheadline", "form_title"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }}}.hero{min-height:100vh;display:flex;align-items:center;padding:60px 40px;background:linear-gradient(135deg,{{ color.primary }} 0%,{{ color.secondary }} 100%)}.hero-container{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.hero-content{color:#fff}.hero-content h1{font-size:3rem;font-weight:800;line-height:1.2;margin-bottom:20px}.hero-content p{font-size:1.25rem;margin-bottom:32px;opacity:0.95}.benefits-list{list-style:none}.benefits-list li{padding:12px 0;font-size:1.125rem;display:flex;align-items:center}.benefits-list li::before{content:'✓';margin-right:12px;font-weight:800;font-size:1.5rem;color:{{ color.accent }}}.form-container{background:#fff;padding:40px;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}.form-container h2{font-size:1.75rem;font-weight:700;margin-bottom:24px;color:{{ color.primary }}}.form-group{margin-bottom:20px}.form-group label{display:block;margin-bottom:8px;font-weight:600;color:#374151}.form-group input{width:100%;padding:14px;border:2px solid #e5e7eb;border-radius:6px;font-size:1rem;transition:border 0.3s}.form-group input:focus{outline:none;border-color:{{ color.primary }}}.submit-btn{width:100%;padding:16px;background:{{ color.primary }};color:#fff;border:none;border-radius:6px;font-weight:700;font-size:1.125rem;cursor:pointer;transition:all 0.3s}.submit-btn:hover{background:{{ color.secondary }};transform:translateY(-2px);box-shadow:0 8px 20px rgba(5,150,105,0.3)}.trust{padding:60px 40px;text-align:center;background:#f9fafb}.trust p{color:#6b7280;font-weight:600;margin-bottom:24px}.trust-logos{display:flex;justify-content:center;gap:40px;flex-wrap:wrap}.footer{background:#111827;color:#fff;padding:40px;text-align:center}@media(max-width:768px){.hero-container{grid-template-columns:1fr}.hero-content h1{font-size:2.25rem}}</style></head><body><section class="hero"><div class="hero-container"><div class="hero-content"><h1>{{ hero.headline }}</h1><p>{{ hero.subheadline }}</p><ul class="benefits-list"><li>Immediate access to exclusive content</li><li>No credit card required</li><li>Join over 10,000 satisfied users</li></ul></div><div class="form-container"><h2>{{ hero.form_title }}</h2><form><div class="form-group"><label>Full Name</label><input type="text" placeholder="Enter your name" required></div><div class="form-group"><label>Email Address</label><input type="email" placeholder="Enter your email" required></div><div class="form-group"><label>Company</label><input type="text" placeholder="Your company name"></div><button type="submit" class="submit-btn">Get Started Free</button></form></div></div></section><section class="trust"><p>Trusted by leading companies worldwide</p><div class="trust-logos"><div style="padding:20px;color:#9ca3af;font-weight:600">Company 1</div><div style="padding:20px;color:#9ca3af;font-weight:600">Company 2</div><div style="padding:20px;color:#9ca3af;font-weight:600">Company 3</div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    },
    
    # BLOG TEMPLATE
    {
        "template_id": "blog_modern_v1",
        "name": "Modern Blog",
        "category": "blog",
        "style": "modern",
        "description": "Clean modern blog with article showcase",
        "tags": ["blog", "content", "articles", "magazine", "news"],
        "features": ["articles", "categories", "author", "newsletter"],
        "color_scheme": {"primary": "#1f2937", "secondary": "#374151", "accent": "#f59e0b", "background": "#ffffff", "text": "#111827"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [
            {"zone_id": "hero", "type": "text", "editable": ["blog_name", "tagline"], "ai_customizable": True}
        ],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.blog_name }}</title><link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }};line-height:1.7}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;z-index:1000}.logo{font-family:'Lora',serif;font-size:1.75rem;font-weight:700}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:#6b7280;text-decoration:none;font-weight:500}.header{padding:120px 40px 80px;text-align:center;max-width:800px;margin:0 auto}.header h1{font-family:'Lora',serif;font-size:3.5rem;font-weight:700;margin-bottom:16px}.header p{font-size:1.25rem;color:#6b7280}.articles{padding:60px 40px;max-width:1200px;margin:0 auto}.articles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px}.article-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);transition:all 0.3s}.article-card:hover{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,0.12)}.article-image{width:100%;height:220px;background:#f3f4f6;object-fit:cover}.article-content{padding:24px}.article-meta{color:#9ca3af;font-size:0.875rem;margin-bottom:12px}.article-title{font-family:'Lora',serif;font-size:1.5rem;font-weight:600;margin-bottom:12px;line-height:1.4}.article-excerpt{color:#6b7280;margin-bottom:16px;line-height:1.6}.read-more{color:{{ color.accent }};font-weight:600;text-decoration:none}.footer{background:#f9fafb;padding:60px 40px;text-align:center;margin-top:60px}@media(max-width:768px){.header h1{font-size:2.5rem}.articles-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.blog_name }}</div><ul class="nav-links"><li><a href="#articles">Articles</a></li><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul></nav><header class="header"><h1>{{ hero.blog_name }}</h1><p>{{ hero.tagline }}</p></header><section class="articles" id="articles"><div class="articles-grid"><article class="article-card"><img src="{{ image_1 }}" class="article-image" alt="Article"><div class="article-content"><div class="article-meta">May 15, 2025 · 5 min read</div><h2 class="article-title">Article Title Goes Here</h2><p class="article-excerpt">A compelling excerpt that draws readers into the full article...</p><a href="#" class="read-more">Read More →</a></div></article><article class="article-card"><div class="article-image"></div><div class="article-content"><div class="article-meta">May 12, 2025 · 8 min read</div><h2 class="article-title">Another Great Article</h2><p class="article-excerpt">Insights and stories that matter to you and your audience...</p><a href="#" class="read-more">Read More →</a></div></article><article class="article-card"><div class="article-image"></div><div class="article-content"><div class="article-meta">May 10, 2025 · 6 min read</div><h2 class="article-title">Featured Story</h2><p class="article-excerpt">Discover the latest trends and developments in our field...</p><a href="#" class="read-more">Read More →</a></div></article></div></section><footer class="footer"><p>&copy; 2025 {{ hero.blog_name }}. All rights reserved.</p></footer></body></html>"""
    }
])

# Component definitions (40 components)
COMPONENTS = [
    # ==================== NAVIGATION BARS (7 variants) ====================
    {
        "component_id": "nav_minimal_v1",
        "name": "Minimal Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Clean minimal navigation with logo and links",
        "tags": ["minimal", "clean", "modern", "simple"],
        "responsive": True,
        "customization_points": ["logo_text", "nav_links", "cta_text"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);backdrop-filter:blur(10px);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;z-index:1000"><div style="font-size:1.25rem;font-weight:700;color:#1a1a1a">{{ logo_text }}</div><div style="display:flex;gap:32px;align-items:center"><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Features</a><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Pricing</a><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">About</a><a href="#" style="background:#1a1a1a;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600">{{ cta_text }}</a></div></nav>"""
    },
    {
        "component_id": "nav_glassmorphism_v1",
        "name": "Glassmorphism Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Modern glass effect navigation with blur",
        "tags": ["glassmorphism", "modern", "blur", "premium"],
        "responsive": True,
        "customization_points": ["logo_text", "nav_links"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.2);z-index:1000;box-shadow:0 4px 30px rgba(0,0,0,0.1)"><div style="font-size:1.5rem;font-weight:800;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{{ logo_text }}</div><div style="display:flex;gap:40px"><a href="#" style="color:#fff;text-decoration:none;font-weight:600">Home</a><a href="#" style="color:#fff;text-decoration:none;font-weight:600">Products</a><a href="#" style="color:#fff;text-decoration:none;font-weight:600">Contact</a></div></nav>"""
    },
    {
        "component_id": "nav_sidebar_v1",
        "name": "Sidebar Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Vertical sidebar navigation for dashboard layouts",
        "tags": ["sidebar", "vertical", "dashboard", "app"],
        "responsive": True,
        "customization_points": ["logo_text", "menu_items"],
        "html": """<aside style="position:fixed;left:0;top:0;width:260px;height:100vh;background:#1a1a1a;color:#fff;padding:32px 20px;display:flex;flex-direction:column;gap:8px;z-index:1000"><div style="font-size:1.5rem;font-weight:800;margin-bottom:40px;color:#fff">{{ logo_text }}</div><a href="#" style="padding:12px 16px;border-radius:8px;color:#9ca3af;text-decoration:none;display:flex;align-items:center;gap:12px;transition:all 0.3s;font-weight:500"><span>📊</span> Dashboard</a><a href="#" style="padding:12px 16px;border-radius:8px;color:#9ca3af;text-decoration:none;display:flex;align-items:center;gap:12px;transition:all 0.3s;font-weight:500"><span>📈</span> Analytics</a><a href="#" style="padding:12px 16px;border-radius:8px;color:#9ca3af;text-decoration:none;display:flex;align-items:center;gap:12px;transition:all 0.3s;font-weight:500"><span>⚙️</span> Settings</a></aside>"""
    },
    {
        "component_id": "nav_dropdown_v1",
        "name": "Dropdown Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Navigation with dropdown menus",
        "tags": ["dropdown", "mega-menu", "complex"],
        "responsive": True,
        "customization_points": ["logo_text", "menu_categories"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:#fff;padding:20px 40px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 10px rgba(0,0,0,0.05);z-index:1000"><div style="font-size:1.5rem;font-weight:700">{{ logo_text }}</div><div style="display:flex;gap:32px;align-items:center"><div style="position:relative"><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Products ▾</a></div><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Solutions</a><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Pricing</a><a href="#" style="background:#667eea;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600">Get Started</a></div></nav>"""
    },
    {
        "component_id": "nav_gradient_v1",
        "name": "Gradient Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Bold navigation with gradient background",
        "tags": ["gradient", "colorful", "bold", "modern"],
        "responsive": True,
        "customization_points": ["logo_text", "nav_items"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;z-index:1000;box-shadow:0 4px 20px rgba(102,126,234,0.3)"><div style="font-size:1.5rem;font-weight:800;color:#fff">{{ logo_text }}</div><div style="display:flex;gap:32px;align-items:center"><a href="#" style="color:#fff;text-decoration:none;font-weight:600;opacity:0.9">Features</a><a href="#" style="color:#fff;text-decoration:none;font-weight:600;opacity:0.9">Pricing</a><a href="#" style="background:#fff;color:#667eea;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:700">Sign Up</a></div></nav>"""
    },
    {
        "component_id": "nav_dark_v1",
        "name": "Dark Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Sleek dark mode navigation",
        "tags": ["dark", "sleek", "elegant", "modern"],
        "responsive": True,
        "customization_points": ["logo_text", "nav_links"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:#0f172a;padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e293b;z-index:1000"><div style="font-size:1.5rem;font-weight:800;color:#fff">{{ logo_text }}</div><div style="display:flex;gap:32px;align-items:center"><a href="#" style="color:#cbd5e1;text-decoration:none;font-weight:500">Home</a><a href="#" style="color:#cbd5e1;text-decoration:none;font-weight:500">About</a><a href="#" style="color:#cbd5e1;text-decoration:none;font-weight:500">Services</a><a href="#" style="background:#3b82f6;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600">Contact</a></div></nav>"""
    },
    {
        "component_id": "nav_centered_v1",
        "name": "Centered Navigation",
        "category": "navigation",
        "type": "navbar",
        "description": "Centered logo with balanced navigation",
        "tags": ["centered", "balanced", "symmetric", "elegant"],
        "responsive": True,
        "customization_points": ["logo_text", "nav_links"],
        "html": """<nav style="position:fixed;top:0;width:100%;background:#fff;padding:20px 40px;display:flex;justify-content:center;align-items:center;border-bottom:1px solid #e5e7eb;z-index:1000"><div style="display:flex;gap:40px;align-items:center"><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Features</a><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">About</a><div style="font-size:1.5rem;font-weight:800;color:#1a1a1a;margin:0 20px">{{ logo_text }}</div><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Blog</a><a href="#" style="color:#1a1a1a;text-decoration:none;font-weight:500">Contact</a></div></nav>"""
    },

    # ==================== HERO SECTIONS (10 variants) ====================
    {
        "component_id": "hero_split_v1",
        "name": "Split Hero Section",
        "category": "hero",
        "type": "hero",
        "description": "Split layout with text on left, image on right",
        "tags": ["split", "two-column", "image", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text", "image_url"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:#fafafa"><div style="max-width:1400px;margin:0 auto;width:100%;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center"><div><h1 style="font-size:4rem;font-weight:800;line-height:1.1;margin-bottom:24px;color:#1a1a1a">{{ headline }}</h1><p style="font-size:1.25rem;color:#6b7280;margin-bottom:40px;line-height:1.8">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#1a1a1a;color:#fff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:700">{{ cta_text }}</a></div><div style="width:100%;height:600px;border-radius:16px;background:linear-gradient(135deg,#667eea,#764ba2);box-shadow:0 20px 60px rgba(0,0,0,0.15)"></div></div></section>"""
    },
    {
        "component_id": "hero_centered_v1",
        "name": "Centered Hero Section",
        "category": "hero",
        "type": "hero",
        "description": "Centered text with gradient background",
        "tags": ["centered", "gradient", "bold", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_primary", "cta_secondary"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)"><div style="max-width:900px"><h1 style="font-size:4.5rem;font-weight:900;line-height:1.1;margin-bottom:24px;color:#fff">{{ headline }}</h1><p style="font-size:1.375rem;color:rgba(255,255,255,0.9);margin-bottom:40px;line-height:1.8">{{ subheadline }}</p><div style="display:flex;gap:20px;justify-content:center"><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:18px 40px;border-radius:8px;text-decoration:none;font-weight:700">{{ cta_primary }}</a><a href="#" style="display:inline-block;background:transparent;color:#fff;padding:18px 40px;border:2px solid #fff;border-radius:8px;text-decoration:none;font-weight:700">{{ cta_secondary }}</a></div></div></section>"""
    },
    {
        "component_id": "hero_minimal_v1",
        "name": "Minimal Hero Section",
        "category": "hero",
        "type": "hero",
        "description": "Clean minimal hero with subtle design",
        "tags": ["minimal", "clean", "simple", "elegant"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="min-height:90vh;display:flex;align-items:center;padding:120px 40px;background:#fff"><div style="max-width:800px;margin:0 auto"><h1 style="font-size:4rem;font-weight:700;line-height:1.2;margin-bottom:32px;color:#1a1a1a">{{ headline }}</h1><p style="font-size:1.25rem;color:#6b7280;margin-bottom:48px;line-height:1.8">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#1a1a1a;color:#fff;padding:16px 40px;border-radius:6px;text-decoration:none;font-weight:600;transition:transform 0.3s">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "hero_video_bg_v1",
        "name": "Video Background Hero",
        "category": "hero",
        "type": "hero",
        "description": "Hero with video or animated background",
        "tags": ["video", "animated", "dynamic", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:#000;overflow:hidden"><div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(102,126,234,0.8),rgba(118,75,162,0.8));z-index:1"></div><div style="position:relative;z-index:2;max-width:900px;color:#fff"><h1 style="font-size:5rem;font-weight:900;line-height:1.1;margin-bottom:24px">{{ headline }}</h1><p style="font-size:1.5rem;margin-bottom:40px;opacity:0.95">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:20px 50px;border-radius:12px;text-decoration:none;font-weight:700;font-size:1.125rem">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "hero_stats_v1",
        "name": "Hero with Stats",
        "category": "hero",
        "type": "hero",
        "description": "Hero section with integrated statistics",
        "tags": ["stats", "data", "metrics", "saas"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "stat_1", "stat_2", "stat_3"],
        "html": """<section style="min-height:90vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(to bottom,#f9fafb,#fff)"><div style="max-width:1200px;margin:0 auto;text-align:center"><h1 style="font-size:4rem;font-weight:800;line-height:1.1;margin-bottom:24px;color:#1a1a1a">{{ headline }}</h1><p style="font-size:1.25rem;color:#6b7280;margin-bottom:60px;max-width:700px;margin-left:auto;margin-right:auto">{{ subheadline }}</p><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px"><div style="padding:32px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="font-size:3rem;font-weight:800;color:#667eea;margin-bottom:8px">{{ stat_1 }}</div><div style="color:#6b7280">Active Users</div></div><div style="padding:32px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="font-size:3rem;font-weight:800;color:#10b981;margin-bottom:8px">{{ stat_2 }}</div><div style="color:#6b7280">Projects</div></div><div style="padding:32px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="font-size:3rem;font-weight:800;color:#f59e0b;margin-bottom:8px">{{ stat_3 }}</div><div style="color:#6b7280">Countries</div></div></div></div></section>"""
    },
    {
        "component_id": "hero_app_showcase_v1",
        "name": "App Showcase Hero",
        "category": "hero",
        "type": "hero",
        "description": "Hero designed for app landing pages",
        "tags": ["app", "mobile", "product", "showcase"],
        "responsive": True,
        "customization_points": ["app_name", "tagline", "cta_text"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)"><div style="max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center"><div style="color:#fff"><h1 style="font-size:4.5rem;font-weight:900;line-height:1.1;margin-bottom:24px">{{ app_name }}</h1><p style="font-size:1.5rem;margin-bottom:40px;opacity:0.95">{{ tagline }}</p><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:18px 40px;border-radius:12px;text-decoration:none;font-weight:700">{{ cta_text }}</a></div><div style="position:relative;height:600px;display:flex;justify-content:center;align-items:center"><div style="width:300px;height:600px;background:#1a1a1a;border-radius:40px;box-shadow:0 40px 80px rgba(0,0,0,0.3);border:8px solid #333"></div></div></div></section>"""
    },
    {
        "component_id": "hero_fullscreen_image_v1",
        "name": "Fullscreen Image Hero",
        "category": "hero",
        "type": "hero",
        "description": "Full-screen hero with overlay text",
        "tags": ["fullscreen", "image", "overlay", "dramatic"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text", "background_image"],
        "html": """<section style="position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.5)),url('{{ background_image }}') center/cover;color:#fff"><div style="max-width:800px;z-index:2"><h1 style="font-size:5rem;font-weight:900;line-height:1.1;margin-bottom:24px;text-shadow:2px 2px 8px rgba(0,0,0,0.3)">{{ headline }}</h1><p style="font-size:1.5rem;margin-bottom:40px;opacity:0.95">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#fff;color:#1a1a1a;padding:18px 50px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1.125rem">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "hero_asymmetric_v1",
        "name": "Asymmetric Hero",
        "category": "hero",
        "type": "hero",
        "description": "Creative asymmetric layout for unique designs",
        "tags": ["asymmetric", "creative", "unique", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:#fff;position:relative;overflow:hidden"><div style="position:absolute;top:-20%;right:-10%;width:800px;height:800px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;opacity:0.1;z-index:0"></div><div style="max-width:1400px;margin:0 auto;position:relative;z-index:1"><h1 style="font-size:5rem;font-weight:900;line-height:1.1;margin-bottom:24px;color:#1a1a1a;max-width:700px">{{ headline }}</h1><p style="font-size:1.25rem;color:#6b7280;margin-bottom:40px;max-width:600px">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#667eea;color:#fff;padding:18px 40px;border-radius:8px;text-decoration:none;font-weight:700">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "hero_illustration_v1",
        "name": "Hero with Illustration",
        "category": "hero",
        "type": "hero",
        "description": "Hero with custom illustration graphics",
        "tags": ["illustration", "graphic", "colorful", "friendly"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(to bottom right,#fef3c7,#fde68a)"><div style="max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center"><div><h1 style="font-size:4rem;font-weight:800;line-height:1.1;margin-bottom:24px;color:#1a1a1a">{{ headline }}</h1><p style="font-size:1.25rem;color:#4b5563;margin-bottom:40px">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#f59e0b;color:#fff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:700">{{ cta_text }}</a></div><div style="width:100%;height:500px;background:linear-gradient(135deg,#f59e0b,#fbbf24);border-radius:24px;box-shadow:0 20px 60px rgba(245,158,11,0.3)"></div></div></section>"""
    },
    {
        "component_id": "hero_particles_v1",
        "name": "Animated Particles Hero",
        "category": "hero",
        "type": "hero",
        "description": "Hero with particle animation effect",
        "tags": ["particles", "animated", "tech", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:#0f172a;color:#fff;overflow:hidden"><div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(102,126,234,0.2),transparent);z-index:0"></div><div style="max-width:900px;position:relative;z-index:1"><h1 style="font-size:5rem;font-weight:900;line-height:1.1;margin-bottom:24px">{{ headline }}</h1><p style="font-size:1.5rem;color:#cbd5e1;margin-bottom:40px">{{ subheadline }}</p><a href="#" style="display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:18px 50px;border-radius:12px;text-decoration:none;font-weight:700;font-size:1.125rem">{{ cta_text }}</a></div></section>"""
    },

    # ==================== FEATURE GRIDS & PRODUCT CARDS (10 variants) ====================
    {
        "component_id": "feature_grid_3col_v1",
        "name": "3-Column Feature Grid",
        "category": "features",
        "type": "feature_grid",
        "description": "Classic 3-column feature layout",
        "tags": ["grid", "3-column", "features", "clean"],
        "responsive": True,
        "customization_points": ["title", "subtitle", "features"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1200px;margin:0 auto;text-align:center"><h2 style="font-size:3rem;font-weight:800;margin-bottom:16px;color:#1a1a1a">{{ title }}</h2><p style="font-size:1.125rem;color:#6b7280;margin-bottom:60px">{{ subtitle }}</p><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px"><div style="padding:40px;background:#f9fafb;border-radius:12px"><div style="width:60px;height:60px;background:#667eea;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px;color:#fff">🚀</div><h3 style="font-size:1.25rem;font-weight:700;margin-bottom:12px">Fast Performance</h3><p style="color:#6b7280;line-height:1.6">Lightning-fast load times and optimized performance</p></div><div style="padding:40px;background:#f9fafb;border-radius:12px"><div style="width:60px;height:60px;background:#10b981;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px;color:#fff">🔒</div><h3 style="font-size:1.25rem;font-weight:700;margin-bottom:12px">Secure</h3><p style="color:#6b7280;line-height:1.6">Bank-level security and data protection</p></div><div style="padding:40px;background:#f9fafb;border-radius:12px"><div style="width:60px;height:60px;background:#f59e0b;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px;color:#fff">⚡</div><h3 style="font-size:1.25rem;font-weight:700;margin-bottom:12px">Reliable</h3><p style="color:#6b7280;line-height:1.6">99.9% uptime guarantee and 24/7 support</p></div></div></div></section>"""
    },
    {
        "component_id": "product_card_ecom_v1",
        "name": "E-commerce Product Card",
        "category": "products",
        "type": "product_card",
        "description": "Product card for online stores",
        "tags": ["ecommerce", "product", "shop", "store"],
        "responsive": True,
        "customization_points": ["product_name", "price", "description", "image_url"],
        "html": """<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;transition:all 0.3s"><div style="width:100%;height:300px;background:linear-gradient(135deg,#f3f4f6,#e5e7eb);overflow:hidden"></div><div style="padding:24px"><h3 style="font-size:1.25rem;font-weight:700;margin-bottom:8px;color:#1a1a1a">{{ product_name }}</h3><p style="color:#6b7280;margin-bottom:16px;font-size:0.9375rem">{{ description }}</p><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:1.5rem;font-weight:800;color:#1a1a1a">{{ price }}</span><button style="background:#1a1a1a;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-weight:600;cursor:pointer">Add to Cart</button></div></div></div>"""
    },
    {
        "component_id": "feature_icon_grid_v1",
        "name": "Icon Feature Grid",
        "category": "features",
        "type": "feature_grid",
        "description": "Feature grid with prominent icons",
        "tags": ["icons", "visual", "features", "modern"],
        "responsive": True,
        "customization_points": ["section_title", "features"],
        "html": """<section style="padding:100px 40px;background:#f9fafb"><div style="max-width:1200px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:80px">{{ section_title }}</h2><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:32px"><div style="text-align:center"><div style="width:80px;height:80px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin:0 auto 20px">📊</div><h3 style="font-weight:700;margin-bottom:8px">Analytics</h3><p style="color:#6b7280;font-size:0.9375rem">Track metrics</p></div><div style="text-align:center"><div style="width:80px;height:80px;background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin:0 auto 20px">🎨</div><h3 style="font-weight:700;margin-bottom:8px">Design</h3><p style="color:#6b7280;font-size:0.9375rem">Beautiful UI</p></div><div style="text-align:center"><div style="width:80px;height:80px;background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin:0 auto 20px">⚡</div><h3 style="font-weight:700;margin-bottom:8px">Speed</h3><p style="color:#6b7280;font-size:0.9375rem">Fast load</p></div><div style="text-align:center"><div style="width:80px;height:80px;background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin:0 auto 20px">🔐</div><h3 style="font-weight:700;margin-bottom:8px">Security</h3><p style="color:#6b7280;font-size:0.9375rem">Protected</p></div></div></div></section>"""
    },
    {
        "component_id": "product_showcase_v1",
        "name": "Product Showcase Grid",
        "category": "products",
        "type": "product_grid",
        "description": "Grid layout for showcasing multiple products",
        "tags": ["showcase", "grid", "products", "ecommerce"],
        "responsive": True,
        "customization_points": ["section_title", "products"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1400px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">{{ section_title }}</h2><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px"><div style="position:relative;overflow:hidden;border-radius:12px;aspect-ratio:1;background:linear-gradient(135deg,#667eea,#764ba2)"></div><div style="position:relative;overflow:hidden;border-radius:12px;aspect-ratio:1;background:linear-gradient(135deg,#f093fb,#f5576c)"></div><div style="position:relative;overflow:hidden;border-radius:12px;aspect-ratio:1;background:linear-gradient(135deg,#4facfe,#00f2fe)"></div><div style="position:relative;overflow:hidden;border-radius:12px;aspect-ratio:1;background:linear-gradient(135deg,#43e97b,#38f9d7)"></div></div></div></section>"""
    },
    {
        "component_id": "feature_alternating_v1",
        "name": "Alternating Feature Layout",
        "category": "features",
        "type": "feature_section",
        "description": "Alternating text and image feature sections",
        "tags": ["alternating", "zigzag", "detailed", "modern"],
        "responsive": True,
        "customization_points": ["features"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1200px;margin:0 auto"><div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;margin-bottom:100px"><div><h3 style="font-size:2.5rem;font-weight:800;margin-bottom:20px">Powerful Analytics</h3><p style="font-size:1.125rem;color:#6b7280;line-height:1.8">Track your performance with real-time analytics and detailed insights into your metrics.</p></div><div style="height:400px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center"><div style="height:400px;background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px"></div><div><h3 style="font-size:2.5rem;font-weight:800;margin-bottom:20px">Seamless Integration</h3><p style="font-size:1.125rem;color:#6b7280;line-height:1.8">Connect with your favorite tools and platforms for a unified workflow.</p></div></div></div></section>"""
    },
    {
        "component_id": "product_featured_v1",
        "name": "Featured Product Display",
        "category": "products",
        "type": "featured_product",
        "description": "Large featured product with details",
        "tags": ["featured", "highlight", "product", "hero"],
        "responsive": True,
        "customization_points": ["product_name", "tagline", "features", "price"],
        "html": """<section style="padding:100px 40px;background:linear-gradient(to bottom,#f9fafb,#fff)"><div style="max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center"><div style="height:600px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:24px;box-shadow:0 40px 80px rgba(102,126,234,0.2)"></div><div><div style="display:inline-block;background:#667eea;color:#fff;padding:8px 16px;border-radius:20px;font-size:0.875rem;font-weight:600;margin-bottom:20px">NEW</div><h2 style="font-size:3.5rem;font-weight:900;margin-bottom:20px">{{ product_name }}</h2><p style="font-size:1.25rem;color:#6b7280;margin-bottom:32px">{{ tagline }}</p><ul style="list-style:none;padding:0;margin-bottom:40px"><li style="padding:12px 0;border-bottom:1px solid #e5e7eb;color:#1a1a1a">✓ Feature One</li><li style="padding:12px 0;border-bottom:1px solid #e5e7eb;color:#1a1a1a">✓ Feature Two</li><li style="padding:12px 0;border-bottom:1px solid #e5e7eb;color:#1a1a1a">✓ Feature Three</li></ul><div style="display:flex;align-items:center;gap:24px"><span style="font-size:3rem;font-weight:900">{{ price }}</span><a href="#" style="background:#1a1a1a;color:#fff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:700">Buy Now</a></div></div></div></section>"""
    },
    {
        "component_id": "feature_cards_v1",
        "name": "Feature Cards Grid",
        "category": "features",
        "type": "feature_cards",
        "description": "Cards-based feature presentation",
        "tags": ["cards", "modern", "shadow", "clean"],
        "responsive": True,
        "customization_points": ["section_title", "features"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1200px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">{{ section_title }}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px"><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:1px solid #e5e7eb;transition:all 0.3s"><div style="font-size:2.5rem;margin-bottom:20px">💡</div><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:12px">Innovation</h3><p style="color:#6b7280;line-height:1.6">Cutting-edge solutions that push boundaries</p></div><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:1px solid #e5e7eb;transition:all 0.3s"><div style="font-size:2.5rem;margin-bottom:20px">🎯</div><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:12px">Precision</h3><p style="color:#6b7280;line-height:1.6">Accurate and reliable results every time</p></div><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:1px solid #e5e7eb;transition:all 0.3s"><div style="font-size:2.5rem;margin-bottom:20px">🚀</div><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:12px">Scale</h3><p style="color:#6b7280;line-height:1.6">Grow without limits or constraints</p></div></div></div></section>"""
    },
    {
        "component_id": "product_comparison_v1",
        "name": "Product Comparison Table",
        "category": "products",
        "type": "comparison",
        "description": "Side-by-side product comparison",
        "tags": ["comparison", "table", "pricing", "features"],
        "responsive": True,
        "customization_points": ["products", "features"],
        "html": """<section style="padding:100px 40px;background:#f9fafb"><div style="max-width:1200px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">Compare Plans</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px"><div style="background:#fff;padding:40px;border-radius:16px;border:2px solid #e5e7eb"><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:8px">Basic</h3><div style="font-size:2.5rem;font-weight:900;margin-bottom:20px">$9<span style="font-size:1rem;color:#6b7280">/mo</span></div><ul style="list-style:none;padding:0"><li style="padding:8px 0;color:#1a1a1a">✓ 10 Projects</li><li style="padding:8px 0;color:#1a1a1a">✓ Basic Support</li><li style="padding:8px 0;color:#9ca3af">✗ Advanced Features</li></ul></div><div style="background:#667eea;color:#fff;padding:40px;border-radius:16px;transform:scale(1.05);box-shadow:0 20px 40px rgba(102,126,234,0.3)"><div style="background:rgba(255,255,255,0.2);padding:4px 12px;border-radius:12px;display:inline-block;margin-bottom:12px;font-size:0.875rem">POPULAR</div><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:8px">Pro</h3><div style="font-size:2.5rem;font-weight:900;margin-bottom:20px">$29<span style="font-size:1rem;opacity:0.8">/mo</span></div><ul style="list-style:none;padding:0"><li style="padding:8px 0">✓ Unlimited Projects</li><li style="padding:8px 0">✓ Priority Support</li><li style="padding:8px 0">✓ Advanced Features</li></ul></div><div style="background:#fff;padding:40px;border-radius:16px;border:2px solid #e5e7eb"><h3 style="font-size:1.5rem;font-weight:700;margin-bottom:8px">Enterprise</h3><div style="font-size:2.5rem;font-weight:900;margin-bottom:20px">$99<span style="font-size:1rem;color:#6b7280">/mo</span></div><ul style="list-style:none;padding:0"><li style="padding:8px 0;color:#1a1a1a">✓ Custom Everything</li><li style="padding:8px 0;color:#1a1a1a">✓ Dedicated Support</li><li style="padding:8px 0;color:#1a1a1a">✓ SLA Guarantee</li></ul></div></div></div></section>"""
    },
    {
        "component_id": "feature_bento_v1",
        "name": "Bento Box Features",
        "category": "features",
        "type": "bento",
        "description": "Modern bento-style feature layout",
        "tags": ["bento", "grid", "modern", "creative"],
        "responsive": True,
        "customization_points": ["features"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(2,250px);gap:16px"><div style="grid-column:span 2;grid-row:span 2;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:24px;padding:40px;color:#fff;display:flex;flex-direction:column;justify-content:center"><h3 style="font-size:2.5rem;font-weight:800;margin-bottom:16px">Main Feature</h3><p style="font-size:1.125rem;opacity:0.95">The centerpiece of your product offering</p></div><div style="grid-column:span 2;background:#f9fafb;border-radius:24px;padding:32px;display:flex;flex-direction:column;justify-content:center"><h4 style="font-size:1.5rem;font-weight:700;margin-bottom:12px">Feature Two</h4><p style="color:#6b7280">Supporting feature description</p></div><div style="background:#f9fafb;border-radius:24px;padding:32px;display:flex;flex-direction:column;justify-content:center"><h4 style="font-weight:700;margin-bottom:8px">Quick</h4><p style="color:#6b7280;font-size:0.9375rem">Fast</p></div><div style="background:#f9fafb;border-radius:24px;padding:32px;display:flex;flex-direction:column;justify-content:center"><h4 style="font-weight:700;margin-bottom:8px">Secure</h4><p style="color:#6b7280;font-size:0.9375rem">Safe</p></div></div></section>"""
    },
    {
        "component_id": "product_carousel_v1",
        "name": "Product Carousel",
        "category": "products",
        "type": "carousel",
        "description": "Horizontal scrolling product showcase",
        "tags": ["carousel", "slider", "products", "modern"],
        "responsive": True,
        "customization_points": ["section_title", "products"],
        "html": """<section style="padding:100px 40px;background:#fff;overflow:hidden"><div style="max-width:1400px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">{{ section_title }}</h2><div style="display:flex;gap:24px;overflow-x:auto;padding-bottom:20px"><div style="min-width:300px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden"><div style="height:300px;background:linear-gradient(135deg,#667eea,#764ba2)"></div><div style="padding:24px"><h3 style="font-weight:700;margin-bottom:8px">Product One</h3><p style="color:#6b7280;font-size:0.9375rem">Description here</p></div></div><div style="min-width:300px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden"><div style="height:300px;background:linear-gradient(135deg,#f093fb,#f5576c)"></div><div style="padding:24px"><h3 style="font-weight:700;margin-bottom:8px">Product Two</h3><p style="color:#6b7280;font-size:0.9375rem">Description here</p></div></div><div style="min-width:300px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden"><div style="height:300px;background:linear-gradient(135deg,#4facfe,#00f2fe)"></div><div style="padding:24px"><h3 style="font-weight:700;margin-bottom:8px">Product Three</h3><p style="color:#6b7280;font-size:0.9375rem">Description here</p></div></div></div></div></section>"""
    },

    # ==================== CALL-TO-ACTION BLOCKS (5 variants) ====================
    {
        "component_id": "cta_centered_v1",
        "name": "Centered CTA",
        "category": "cta",
        "type": "cta_block",
        "description": "Centered call-to-action section",
        "tags": ["centered", "simple", "clean"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="padding:100px 40px;background:linear-gradient(135deg,#667eea,#764ba2);text-align:center"><div style="max-width:800px;margin:0 auto;color:#fff"><h2 style="font-size:3.5rem;font-weight:900;margin-bottom:24px">{{ headline }}</h2><p style="font-size:1.25rem;margin-bottom:40px;opacity:0.95">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:18px 50px;border-radius:12px;text-decoration:none;font-weight:700;font-size:1.125rem">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "cta_split_v1",
        "name": "Split CTA",
        "category": "cta",
        "type": "cta_block",
        "description": "Two-column CTA with text and form",
        "tags": ["split", "form", "newsletter"],
        "responsive": True,
        "customization_points": ["headline", "description", "cta_text"],
        "html": """<section style="padding:100px 40px;background:#f9fafb"><div style="max-width:1200px;margin:0 auto;background:#fff;border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.1);overflow:hidden;display:grid;grid-template-columns:1fr 1fr;align-items:center"><div style="padding:60px"><h2 style="font-size:3rem;font-weight:800;margin-bottom:20px">{{ headline }}</h2><p style="font-size:1.125rem;color:#6b7280">{{ description }}</p></div><div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:60px;color:#fff"><input type="email" placeholder="Enter your email" style="width:100%;padding:16px;border-radius:8px;border:none;margin-bottom:16px;font-size:1rem"><button style="width:100%;background:#fff;color:#667eea;padding:16px;border-radius:8px;border:none;font-weight:700;font-size:1rem;cursor:pointer">{{ cta_text }}</button></div></div></section>"""
    },
    {
        "component_id": "cta_banner_v1",
        "name": "Banner CTA",
        "category": "cta",
        "type": "cta_banner",
        "description": "Full-width banner style CTA",
        "tags": ["banner", "wide", "bold"],
        "responsive": True,
        "customization_points": ["headline", "cta_text"],
        "html": """<section style="padding:60px 40px;background:#1a1a1a;color:#fff"><div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center"><div><h3 style="font-size:2.5rem;font-weight:800;margin-bottom:12px">{{ headline }}</h3><p style="font-size:1.125rem;opacity:0.9">Get started today with no credit card required</p></div><a href="#" style="background:#fff;color:#1a1a1a;padding:18px 40px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1.125rem;white-space:nowrap">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "cta_card_v1",
        "name": "Card CTA",
        "category": "cta",
        "type": "cta_card",
        "description": "CTA in a floating card design",
        "tags": ["card", "floating", "modern"],
        "responsive": True,
        "customization_points": ["headline", "subheadline", "cta_text"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:800px;margin:0 auto;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:24px;padding:80px;text-align:center;color:#fff;box-shadow:0 30px 60px rgba(102,126,234,0.3)"><h2 style="font-size:3.5rem;font-weight:900;margin-bottom:20px">{{ headline }}</h2><p style="font-size:1.25rem;margin-bottom:40px;opacity:0.95">{{ subheadline }}</p><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:18px 50px;border-radius:12px;text-decoration:none;font-weight:700;font-size:1.125rem">{{ cta_text }}</a></div></section>"""
    },
    {
        "component_id": "cta_minimal_v1",
        "name": "Minimal CTA",
        "category": "cta",
        "type": "cta_block",
        "description": "Subtle minimal call-to-action",
        "tags": ["minimal", "subtle", "clean"],
        "responsive": True,
        "customization_points": ["headline", "cta_text"],
        "html": """<section style="padding:80px 40px;background:#fff;border-top:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb"><div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center"><h3 style="font-size:2rem;font-weight:700">{{ headline }}</h3><a href="#" style="background:#1a1a1a;color:#fff;padding:16px 32px;border-radius:8px;text-decoration:none;font-weight:600">{{ cta_text }}</a></div></section>"""
    },

    # ==================== FORMS (5 variants) ====================
    {
        "component_id": "form_contact_v1",
        "name": "Contact Form",
        "category": "forms",
        "type": "contact",
        "description": "Standard contact form with fields",
        "tags": ["contact", "form", "input"],
        "responsive": True,
        "customization_points": ["form_title", "submit_text"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:600px;margin:0 auto"><h2 style="font-size:3rem;font-weight:800;margin-bottom:40px;text-align:center">{{ form_title }}</h2><form style="display:flex;flex-direction:column;gap:20px"><input type="text" placeholder="Your Name" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><input type="email" placeholder="Your Email" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><textarea placeholder="Your Message" rows="5" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem;resize:vertical"></textarea><button type="submit" style="background:#1a1a1a;color:#fff;padding:16px;border-radius:8px;border:none;font-weight:700;font-size:1rem;cursor:pointer">{{ submit_text }}</button></form></div></section>"""
    },
    {
        "component_id": "form_newsletter_v1",
        "name": "Newsletter Form",
        "category": "forms",
        "type": "newsletter",
        "description": "Email newsletter subscription form",
        "tags": ["newsletter", "email", "subscribe"],
        "responsive": True,
        "customization_points": ["title", "description", "button_text"],
        "html": """<section style="padding:80px 40px;background:#f9fafb"><div style="max-width:600px;margin:0 auto;text-align:center"><h3 style="font-size:2rem;font-weight:700;margin-bottom:16px">{{ title }}</h3><p style="color:#6b7280;margin-bottom:32px">{{ description }}</p><form style="display:flex;gap:12px"><input type="email" placeholder="Enter your email" style="flex:1;padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><button type="submit" style="background:#1a1a1a;color:#fff;padding:16px 32px;border-radius:8px;border:none;font-weight:700;cursor:pointer">{{ button_text }}</button></form></div></section>"""
    },
    {
        "component_id": "form_login_v1",
        "name": "Login Form",
        "category": "forms",
        "type": "login",
        "description": "User login form",
        "tags": ["login", "auth", "authentication"],
        "responsive": True,
        "customization_points": ["form_title", "login_button"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f9fafb;padding:40px"><div style="background:#fff;padding:60px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08);width:100%;max-width:450px"><h2 style="font-size:2rem;font-weight:800;margin-bottom:32px;text-align:center">{{ form_title }}</h2><form style="display:flex;flex-direction:column;gap:20px"><input type="email" placeholder="Email address" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><input type="password" placeholder="Password" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><button type="submit" style="background:#1a1a1a;color:#fff;padding:16px;border-radius:8px;border:none;font-weight:700;font-size:1rem;cursor:pointer">{{ login_button }}</button></form><p style="text-align:center;margin-top:20px;color:#6b7280;font-size:0.9375rem">Don't have an account? <a href="#" style="color:#667eea;text-decoration:none;font-weight:600">Sign up</a></p></div></section>"""
    },
    {
        "component_id": "form_signup_v1",
        "name": "Signup Form",
        "category": "forms",
        "type": "signup",
        "description": "User registration form",
        "tags": ["signup", "register", "auth"],
        "responsive": True,
        "customization_points": ["form_title", "signup_button"],
        "html": """<section style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);padding:40px"><div style="background:#fff;padding:60px;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.2);width:100%;max-width:500px"><h2 style="font-size:2rem;font-weight:800;margin-bottom:32px;text-align:center">{{ form_title }}</h2><form style="display:flex;flex-direction:column;gap:16px"><input type="text" placeholder="Full Name" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><input type="email" placeholder="Email address" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><input type="password" placeholder="Password" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><input type="password" placeholder="Confirm Password" style="padding:16px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem"><button type="submit" style="background:#667eea;color:#fff;padding:16px;border-radius:8px;border:none;font-weight:700;font-size:1rem;cursor:pointer;margin-top:8px">{{ signup_button }}</button></form></div></section>"""
    },
    {
        "component_id": "form_search_v1",
        "name": "Search Form",
        "category": "forms",
        "type": "search",
        "description": "Search bar component",
        "tags": ["search", "find", "filter"],
        "responsive": True,
        "customization_points": ["placeholder", "button_text"],
        "html": """<div style="max-width:600px;margin:0 auto;padding:40px"><form style="display:flex;gap:12px;background:#fff;padding:8px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1)"><input type="text" placeholder="{{ placeholder }}" style="flex:1;padding:16px;border:none;font-size:1rem;outline:none"><button type="submit" style="background:#1a1a1a;color:#fff;padding:16px 32px;border-radius:8px;border:none;font-weight:700;cursor:pointer">{{ button_text }}</button></form></div>"""
    },

    # ==================== TESTIMONIALS (5 variants) ====================
    {
        "component_id": "testimonial_cards_v1",
        "name": "Testimonial Cards",
        "category": "testimonials",
        "type": "testimonial_grid",
        "description": "Grid of testimonial cards",
        "tags": ["testimonials", "reviews", "social-proof"],
        "responsive": True,
        "customization_points": ["section_title", "testimonials"],
        "html": """<section style="padding:100px 40px;background:#f9fafb"><div style="max-width:1200px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">{{ section_title }}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px"><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:20px;font-size:1.25rem">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"This product completely transformed how we work. Highly recommended!"</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%"></div><div><div style="font-weight:700">Sarah Johnson</div><div style="color:#6b7280;font-size:0.875rem">CEO, TechCorp</div></div></div></div><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:20px;font-size:1.25rem">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"Amazing experience from start to finish. The team was incredibly helpful."</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:50%"></div><div><div style="font-weight:700">Michael Chen</div><div style="color:#6b7280;font-size:0.875rem">Founder, StartupXYZ</div></div></div></div><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:20px;font-size:1.25rem">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"Best investment we've made this year. Results exceeded expectations."</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:50%"></div><div><div style="font-weight:700">Emily Davis</div><div style="color:#6b7280;font-size:0.875rem">Director, Agency Co</div></div></div></div></div></div></section>"""
    },
    {
        "component_id": "testimonial_featured_v1",
        "name": "Featured Testimonial",
        "category": "testimonials",
        "type": "featured_testimonial",
        "description": "Large featured testimonial",
        "tags": ["testimonial", "featured", "highlight"],
        "responsive": True,
        "customization_points": ["quote", "author", "role", "company"],
        "html": """<section style="padding:100px 40px;background:#fff"><div style="max-width:1000px;margin:0 auto;text-align:center"><div style="font-size:4rem;color:#667eea;margin-bottom:32px">"</div><p style="font-size:2rem;font-weight:600;line-height:1.5;color:#1a1a1a;margin-bottom:40px">{{ quote }}</p><div style="width:80px;height:80px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;margin:0 auto 20px"></div><div style="font-size:1.25rem;font-weight:700;margin-bottom:4px">{{ author }}</div><div style="color:#6b7280">{{ role }}, {{ company }}</div></div></section>"""
    },
    {
        "component_id": "testimonial_slider_v1",
        "name": "Testimonial Slider",
        "category": "testimonials",
        "type": "testimonial_carousel",
        "description": "Horizontal scrolling testimonials",
        "tags": ["slider", "carousel", "testimonials"],
        "responsive": True,
        "customization_points": ["testimonials"],
        "html": """<section style="padding:100px 40px;background:#f9fafb;overflow:hidden"><div style="max-width:1400px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">What Our Customers Say</h2><div style="display:flex;gap:32px;overflow-x:auto;padding-bottom:20px"><div style="min-width:400px;background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:16px">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"Outstanding service and product quality."</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:#667eea;border-radius:50%"></div><div><div style="font-weight:700">Alex Turner</div><div style="color:#6b7280;font-size:0.875rem">Product Manager</div></div></div></div><div style="min-width:400px;background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:16px">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"Exactly what we needed for our business."</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:#10b981;border-radius:50%"></div><div><div style="font-weight:700">Rachel Green</div><div style="color:#6b7280;font-size:0.875rem">Marketing Lead</div></div></div></div><div style="min-width:400px;background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.05)"><div style="color:#fbbf24;margin-bottom:16px">★★★★★</div><p style="color:#1a1a1a;margin-bottom:24px;line-height:1.6">"Incredible results in just a few weeks."</p><div style="display:flex;align-items:center;gap:12px"><div style="width:48px;height:48px;background:#f59e0b;border-radius:50%"></div><div><div style="font-weight:700">David Lee</div><div style="color:#6b7280;font-size:0.875rem">Growth Manager</div></div></div></div></div></div></section>"""
    },
    {
        "component_id": "testimonial_minimal_v1",
        "name": "Minimal Testimonial",
        "category": "testimonials",
        "type": "testimonial_simple",
        "description": "Simple minimal testimonial",
        "tags": ["minimal", "simple", "clean"],
        "responsive": True,
        "customization_points": ["quote", "author"],
        "html": """<section style="padding:80px 40px;background:#fff;border-top:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb"><div style="max-width:800px;margin:0 auto;text-align:center"><p style="font-size:1.5rem;font-style:italic;color:#1a1a1a;margin-bottom:24px">"{{ quote }}"</p><div style="font-weight:700">— {{ author }}</div></div></section>"""
    },
    {
        "component_id": "testimonial_video_v1",
        "name": "Video Testimonial",
        "category": "testimonials",
        "type": "testimonial_video",
        "description": "Testimonial with video placeholder",
        "tags": ["video", "testimonial", "multimedia"],
        "responsive": True,
        "customization_points": ["section_title", "video_url"],
        "html": """<section style="padding:100px 40px;background:#f9fafb"><div style="max-width:1000px;margin:0 auto"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">{{ section_title }}</h2><div style="background:#1a1a1a;aspect-ratio:16/9;border-radius:16px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:4rem">▶️</div><div style="margin-top:32px;text-align:center"><p style="font-size:1.25rem;color:#1a1a1a;margin-bottom:16px">"Working with this team changed everything for us."</p><div style="font-weight:700">Jennifer Brown, VP of Operations</div></div></div></section>"""
    },

    # ==================== FOOTERS (7 variants) ====================
    {
        "component_id": "footer_minimal_v1",
        "name": "Minimal Footer",
        "category": "footer",
        "type": "footer",
        "description": "Clean minimal footer",
        "tags": ["minimal", "simple", "clean"],
        "responsive": True,
        "customization_points": ["company_name", "links"],
        "html": """<footer style="background:#fff;border-top:1px solid #e5e7eb;padding:60px 40px"><div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center"><div style="font-weight:700;font-size:1.125rem">{{ company_name }}</div><div style="display:flex;gap:32px"><a href="#" style="color:#6b7280;text-decoration:none;font-size:0.9375rem">About</a><a href="#" style="color:#6b7280;text-decoration:none;font-size:0.9375rem">Privacy</a><a href="#" style="color:#6b7280;text-decoration:none;font-size:0.9375rem">Terms</a><a href="#" style="color:#6b7280;text-decoration:none;font-size:0.9375rem">Contact</a></div></div><div style="max-width:1200px;margin:32px auto 0;text-align:center;color:#9ca3af;font-size:0.875rem">© 2025 {{ company_name }}. All rights reserved.</div></footer>"""
    },
    {
        "component_id": "footer_comprehensive_v1",
        "name": "Comprehensive Footer",
        "category": "footer",
        "type": "footer",
        "description": "Multi-column footer with links",
        "tags": ["comprehensive", "multi-column", "detailed"],
        "responsive": True,
        "customization_points": ["company_name", "columns"],
        "html": """<footer style="background:#1a1a1a;color:#fff;padding:80px 40px 40px"><div style="max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:60px;margin-bottom:60px"><div><div style="font-size:1.5rem;font-weight:800;margin-bottom:20px">{{ company_name }}</div><p style="color:#9ca3af;line-height:1.6">Building the future of technology, one innovation at a time.</p></div><div><h4 style="font-weight:700;margin-bottom:20px">Product</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#9ca3af;text-decoration:none">Features</a><a href="#" style="color:#9ca3af;text-decoration:none">Pricing</a><a href="#" style="color:#9ca3af;text-decoration:none">Documentation</a></div></div><div><h4 style="font-weight:700;margin-bottom:20px">Company</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#9ca3af;text-decoration:none">About</a><a href="#" style="color:#9ca3af;text-decoration:none">Careers</a><a href="#" style="color:#9ca3af;text-decoration:none">Blog</a></div></div><div><h4 style="font-weight:700;margin-bottom:20px">Legal</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#9ca3af;text-decoration:none">Privacy</a><a href="#" style="color:#9ca3af;text-decoration:none">Terms</a><a href="#" style="color:#9ca3af;text-decoration:none">Security</a></div></div></div><div style="max-width:1200px;margin:0 auto;padding-top:40px;border-top:1px solid #374151;text-align:center;color:#6b7280">© 2025 {{ company_name }}. All rights reserved.</div></footer>"""
    },
    {
        "component_id": "footer_newsletter_v1",
        "name": "Newsletter Footer",
        "category": "footer",
        "type": "footer",
        "description": "Footer with newsletter signup",
        "tags": ["newsletter", "subscription", "email"],
        "responsive": True,
        "customization_points": ["company_name", "newsletter_cta"],
        "html": """<footer style="background:#f9fafb;padding:80px 40px 40px"><div style="max-width:1200px;margin:0 auto"><div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;margin-bottom:60px"><div><h3 style="font-size:2rem;font-weight:800;margin-bottom:16px">{{ newsletter_cta }}</h3><p style="color:#6b7280;margin-bottom:24px">Get the latest updates and news delivered to your inbox.</p><form style="display:flex;gap:12px"><input type="email" placeholder="Your email" style="flex:1;padding:14px;border:1px solid #d1d5db;border-radius:8px"><button type="submit" style="background:#1a1a1a;color:#fff;padding:14px 28px;border-radius:8px;border:none;font-weight:700;cursor:pointer">Subscribe</button></form></div><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:40px"><div><h4 style="font-weight:700;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#6b7280;text-decoration:none">Features</a><a href="#" style="color:#6b7280;text-decoration:none">Pricing</a></div></div><div><h4 style="font-weight:700;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#6b7280;text-decoration:none">About</a><a href="#" style="color:#6b7280;text-decoration:none">Contact</a></div></div></div></div><div style="text-align:center;padding-top:40px;border-top:1px solid #e5e7eb;color:#6b7280">© 2025 {{ company_name }}. All rights reserved.</div></div></footer>"""
    },
    {
        "component_id": "footer_social_v1",
        "name": "Social Media Footer",
        "category": "footer",
        "type": "footer",
        "description": "Footer with social media links",
        "tags": ["social", "media", "icons"],
        "responsive": True,
        "customization_points": ["company_name", "social_links"],
        "html": """<footer style="background:#1a1a1a;color:#fff;padding:60px 40px"><div style="max-width:1200px;margin:0 auto"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:40px"><div style="font-size:1.5rem;font-weight:800">{{ company_name }}</div><div style="display:flex;gap:16px"><a href="#" style="width:40px;height:40px;background:#374151;border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff">📘</a><a href="#" style="width:40px;height:40px;background:#374151;border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff">🐦</a><a href="#" style="width:40px;height:40px;background:#374151;border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff">📷</a><a href="#" style="width:40px;height:40px;background:#374151;border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff">💼</a></div></div><div style="text-align:center;padding-top:40px;border-top:1px solid #374151;color:#6b7280">© 2025 {{ company_name }}. All rights reserved.</div></div></footer>"""
    },
    {
        "component_id": "footer_centered_v1",
        "name": "Centered Footer",
        "category": "footer",
        "type": "footer",
        "description": "Centered layout footer",
        "tags": ["centered", "simple", "clean"],
        "responsive": True,
        "customization_points": ["company_name", "tagline"],
        "html": """<footer style="background:#fff;border-top:1px solid #e5e7eb;padding:80px 40px"><div style="max-width:800px;margin:0 auto;text-align:center"><div style="font-size:1.5rem;font-weight:800;margin-bottom:16px">{{ company_name }}</div><p style="color:#6b7280;margin-bottom:32px">{{ tagline }}</p><div style="display:flex;justify-content:center;gap:32px;margin-bottom:40px"><a href="#" style="color:#6b7280;text-decoration:none">About</a><a href="#" style="color:#6b7280;text-decoration:none">Features</a><a href="#" style="color:#6b7280;text-decoration:none">Pricing</a><a href="#" style="color:#6b7280;text-decoration:none">Contact</a></div><div style="color:#9ca3af;font-size:0.875rem">© 2025 {{ company_name }}. All rights reserved.</div></div></footer>"""
    },
    {
        "component_id": "footer_dark_v1",
        "name": "Dark Footer",
        "category": "footer",
        "type": "footer",
        "description": "Dark mode footer design",
        "tags": ["dark", "modern", "sleek"],
        "responsive": True,
        "customization_points": ["company_name", "cta"],
        "html": """<footer style="background:#0f172a;color:#fff;padding:100px 40px 40px"><div style="max-width:1200px;margin:0 auto"><div style="background:#1e293b;border-radius:16px;padding:60px;text-align:center;margin-bottom:60px"><h3 style="font-size:2.5rem;font-weight:800;margin-bottom:16px">{{ cta }}</h3><p style="color:#cbd5e1;margin-bottom:32px;font-size:1.125rem">Join thousands of satisfied customers</p><a href="#" style="display:inline-block;background:#3b82f6;color:#fff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:700">Get Started Free</a></div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:60px;margin-bottom:60px"><div><h4 style="font-weight:700;margin-bottom:20px">Product</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#94a3b8;text-decoration:none">Features</a><a href="#" style="color:#94a3b8;text-decoration:none">Pricing</a></div></div><div><h4 style="font-weight:700;margin-bottom:20px">Company</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#94a3b8;text-decoration:none">About</a><a href="#" style="color:#94a3b8;text-decoration:none">Blog</a></div></div><div><h4 style="font-weight:700;margin-bottom:20px">Support</h4><div style="display:flex;flex-direction:column;gap:12px"><a href="#" style="color:#94a3b8;text-decoration:none">Help Center</a><a href="#" style="color:#94a3b8;text-decoration:none">Contact</a></div></div></div><div style="text-align:center;padding-top:40px;border-top:1px solid #1e293b;color:#64748b">© 2025 {{ company_name }}. All rights reserved.</div></div></footer>"""
    },
    {
        "component_id": "footer_gradient_v1",
        "name": "Gradient Footer",
        "category": "footer",
        "type": "footer",
        "description": "Footer with gradient background",
        "tags": ["gradient", "colorful", "modern"],
        "responsive": True,
        "customization_points": ["company_name", "cta"],
        "html": """<footer style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:80px 40px 40px"><div style="max-width:1200px;margin:0 auto"><div style="text-align:center;margin-bottom:60px"><h3 style="font-size:3rem;font-weight:900;margin-bottom:16px">{{ cta }}</h3><p style="font-size:1.25rem;margin-bottom:32px;opacity:0.95">Start your journey today</p><a href="#" style="display:inline-block;background:#fff;color:#667eea;padding:18px 40px;border-radius:12px;text-decoration:none;font-weight:700">Get Started</a></div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:40px;margin-bottom:60px"><div><h4 style="font-weight:700;margin-bottom:16px;opacity:0.95">Product</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Features</a><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Pricing</a></div></div><div><h4 style="font-weight:700;margin-bottom:16px;opacity:0.95">Company</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">About</a><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Careers</a></div></div><div><h4 style="font-weight:700;margin-bottom:16px;opacity:0.95">Resources</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Blog</a><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Docs</a></div></div><div><h4 style="font-weight:700;margin-bottom:16px;opacity:0.95">Legal</h4><div style="display:flex;flex-direction:column;gap:8px"><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Privacy</a><a href="#" style="color:#fff;text-decoration:none;opacity:0.8">Terms</a></div></div></div><div style="text-align:center;padding-top:40px;border-top:1px solid rgba(255,255,255,0.2);opacity:0.8">© 2025 {{ company_name }}. All rights reserved.</div></div></footer>"""
    }
]

# Additional Specialized Templates (11-25)
TEMPLATES.extend([
    # E-COMMERCE TEMPLATE 3 - Boutique/Artisan
    {
        "template_id": "ecom_boutique_v1",
        "name": "Boutique Artisan Store",
        "category": "ecommerce",
        "style": "artisan",
        "description": "Handcrafted, artisan e-commerce for unique products",
        "tags": ["ecommerce", "boutique", "artisan", "handmade", "craft", "unique"],
        "features": ["product_story", "craft_showcase", "cart", "about_maker"],
        "color_scheme": {"primary": "#8b4513", "secondary": "#d2691e", "accent": "#f4a460", "background": "#faf8f3", "text": "#3e2723"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["headline", "story", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Lato',sans-serif;color:{{ color.text }};background:{{ color.background }}}.nav{position:fixed;top:0;width:100%;background:rgba(250,248,243,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid {{ color.accent }};z-index:1000}.logo{font-family:'Cormorant Garamond',serif;font-size:1.75rem;font-weight:700;color:{{ color.primary }}}.hero{min-height:90vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(rgba(139,69,19,0.05),rgba(139,69,19,0.05)),url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><rect fill="%23f4a460" opacity="0.05" width="80" height="80"/></svg>')}.hero-content{max-width:1200px;margin:0 auto;text-align:center}.hero h1{font-family:'Cormorant Garamond',serif;font-size:4rem;font-weight:700;color:{{ color.primary }};margin-bottom:24px}.hero p{font-size:1.25rem;color:#5d4037;margin-bottom:40px;max-width:700px;margin-left:auto;margin-right:auto}.btn{display:inline-block;padding:16px 40px;background:{{ color.primary }};color:#fff;text-decoration:none;font-weight:600;border-radius:4px;transition:all 0.3s}.btn:hover{background:{{ color.secondary }};transform:translateY(-2px)}.products{padding:100px 40px;max-width:1400px;margin:0 auto}.product-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px}.product-card{background:#fff;border:1px solid #e0d5c7;padding:24px;border-radius:8px;transition:all 0.3s}.product-card:hover{box-shadow:0 8px 30px rgba(139,69,19,0.15)}.product-image{width:100%;height:300px;background:#f5f5f5;margin-bottom:20px;border-radius:4px}.product-card h3{font-family:'Cormorant Garamond',serif;font-size:1.5rem;margin-bottom:12px}.product-card p{color:#6d4c41;margin-bottom:16px}.product-price{font-size:1.375rem;font-weight:700;color:{{ color.primary }};margin-bottom:16px}.footer{background:{{ color.primary }};color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.product-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div></nav><section class="hero"><div class="hero-content"><h1>{{ hero.headline }}</h1><p>{{ hero.story }}</p><a href="#shop" class="btn">{{ hero.cta }}</a></div></section><section class="products" id="shop"><h2 style="font-family:'Cormorant Garamond',serif;font-size:3rem;text-align:center;margin-bottom:60px;color:{{ color.primary }}">Handcrafted Collection</h2><div class="product-grid"><div class="product-card"><div class="product-image"></div><h3>Artisan Product</h3><p>Handcrafted with care and attention to detail</p><div class="product-price">$89</div><button class="btn">Add to Cart</button></div><div class="product-card"><div class="product-image"></div><h3>Unique Piece</h3><p>One-of-a-kind creation</p><div class="product-price">$129</div><button class="btn">Add to Cart</button></div><div class="product-card"><div class="product-image"></div><h3>Custom Made</h3><p>Crafted to perfection</p><div class="product-price">$159</div><button class="btn">Add to Cart</button></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    },
    
    # SAAS TEMPLATE 4 - Analytics Dashboard
    {
        "template_id": "saas_analytics_v1",
        "name": "Analytics Platform",
        "category": "saas",
        "style": "data",
        "description": "Data analytics and business intelligence platform",
        "tags": ["saas", "analytics", "data", "dashboard", "insights", "metrics"],
        "features": ["dashboard_preview", "metrics", "integrations", "api"],
        "color_scheme": {"primary": "#4f46e5", "secondary": "#6366f1", "accent": "#06b6d4", "background": "#ffffff", "text": "#0f172a"},
        "use_count": 0,
        "lighthouse_score": 95,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["headline", "description", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);padding:16px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;z-index:1000}.logo{font-size:1.5rem;font-weight:800;color:{{ color.primary }}}.btn{background:{{ color.primary }};color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600}.hero{min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%)}.hero-content{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center;color:#fff}.hero-text h1{font-size:3.5rem;font-weight:800;line-height:1.1;margin-bottom:24px}.hero-text p{font-size:1.25rem;opacity:0.9;margin-bottom:32px}.hero-btn{background:{{ color.accent }};color:#0f172a;padding:16px 32px;border-radius:8px;text-decoration:none;font-weight:700;display:inline-block}.dashboard-preview{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:24px;backdrop-filter:blur(10px)}.features{padding:100px 40px;max-width:1200px;margin:0 auto}.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.feature{background:#f8fafc;padding:40px;border-radius:12px;border:1px solid #e2e8f0}.feature-icon{width:60px;height:60px;background:{{ color.primary }};border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px}.feature h3{font-size:1.25rem;font-weight:700;margin-bottom:12px}.feature p{color:#64748b;line-height:1.6}.cta{padding:100px 40px;background:{{ color.primary }};color:#fff;text-align:center}.cta h2{font-size:3rem;font-weight:800;margin-bottom:24px}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero-content{grid-template-columns:1fr}.hero-text h1{font-size:2.5rem}.features-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div><a href="#demo" class="btn">Get Started</a></nav><section class="hero"><div class="hero-content"><div class="hero-text"><h1>{{ hero.headline }}</h1><p>{{ hero.description }}</p><a href="#demo" class="hero-btn">{{ hero.cta }}</a></div><div class="dashboard-preview"><div style="height:400px;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,0.6)">Dashboard Preview</div></div></div></section><section class="features"><h2 style="text-align:center;font-size:2.5rem;font-weight:800;margin-bottom:60px">Powerful Analytics</h2><div class="features-grid"><div class="feature"><div class="feature-icon">📊</div><h3>Real-time Data</h3><p>Live dashboard updates as data flows in</p></div><div class="feature"><div class="feature-icon">🔄</div><h3>Easy Integration</h3><p>Connect your tools in minutes</p></div><div class="feature"><div class="feature-icon">📈</div><h3>Custom Reports</h3><p>Build reports tailored to your needs</p></div></div></section><section class="cta"><h2>Start Analyzing Today</h2><p style="font-size:1.25rem;margin-bottom:32px">Join thousands of data-driven teams</p><a href="#demo" class="hero-btn">Start Free Trial</a></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    },
    
    # AGENCY TEMPLATE
    {
        "template_id": "agency_creative_v1",
        "name": "Creative Agency",
        "category": "agency",
        "style": "creative",
        "description": "Bold creative agency and design studio",
        "tags": ["agency", "studio", "creative", "design", "marketing", "digital"],
        "features": ["portfolio", "services", "team", "contact"],
        "color_scheme": {"primary": "#000000", "secondary": "#ff3366", "accent": "#00ffff", "background": "#ffffff", "text": "#1a1a1a"},
        "use_count": 0,
        "lighthouse_score": 93,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["agency_name", "tagline", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.agency_name }}</title><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Space Grotesk',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:{{ color.primary }};color:#fff;padding:24px 40px;display:flex;justify-content:space-between;align-items:center;z-index:1000}.logo{font-size:1.5rem;font-weight:800}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:#fff;text-decoration:none;font-weight:500}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:{{ color.primary }};color:#fff}.hero h1{font-size:5rem;font-weight:800;line-height:1;margin-bottom:24px;letter-spacing:-2px}.hero h1 span{color:{{ color.secondary }}}.hero p{font-size:1.5rem;margin-bottom:40px}.hero-btn{display:inline-block;padding:20px 40px;background:{{ color.secondary }};color:#fff;text-decoration:none;font-weight:700;border-radius:50px;transition:all 0.3s}.hero-btn:hover{transform:scale(1.05)}.services{padding:100px 40px;max-width:1200px;margin:0 auto}.services-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.service{padding:40px;border:2px solid {{ color.primary }};border-radius:16px;transition:all 0.3s}.service:hover{background:{{ color.primary }};color:#fff;transform:translateY(-8px)}.service h3{font-size:1.5rem;font-weight:700;margin-bottom:16px}.service p{line-height:1.6}.footer{background:{{ color.primary }};color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:3rem}.services-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.agency_name }}</div><ul class="nav-links"><li><a href="#work">Work</a></li><li><a href="#services">Services</a></li><li><a href="#contact">Contact</a></li></ul></nav><section class="hero"><div><h1>{{ hero.agency_name }}<br><span>Studio</span></h1><p>{{ hero.tagline }}</p><a href="#contact" class="hero-btn">{{ hero.cta }}</a></div></section><section class="services" id="services"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">What We Do</h2><div class="services-grid"><div class="service"><h3>Brand Strategy</h3><p>Building memorable brands that stand out</p></div><div class="service"><h3>Digital Design</h3><p>Crafting beautiful digital experiences</p></div><div class="service"><h3>Development</h3><p>Bringing designs to life with code</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.agency_name }}</p></footer></body></html>"""
    },
    
    # RESTAURANT TEMPLATE
    {
        "template_id": "restaurant_elegant_v1",
        "name": "Restaurant Elegant",
        "category": "restaurant",
        "style": "elegant",
        "description": "Elegant restaurant and dining experience",
        "tags": ["restaurant", "food", "dining", "menu", "reservation", "culinary"],
        "features": ["menu", "reservation", "gallery", "contact"],
        "color_scheme": {"primary": "#2d1810", "secondary": "#8b4513", "accent": "#d4af37", "background": "#faf8f5", "text": "#2d1810"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["restaurant_name", "tagline", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.restaurant_name }}</title><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Lato:wght@300;400&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Lato',sans-serif;color:{{ color.text }};background:{{ color.background }}}.nav{position:fixed;top:0;width:100%;background:rgba(250,248,245,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid {{ color.accent }};z-index:1000}.logo{font-family:'Playfair Display',serif;font-size:1.75rem;font-weight:700;color:{{ color.primary }}}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:{{ color.text }};text-decoration:none;font-weight:400}.hero{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:linear-gradient(rgba(45,24,16,0.7),rgba(45,24,16,0.7)),url('{{ image_1 }}') center/cover}.hero-content{color:#fff}.hero h1{font-family:'Playfair Display',serif;font-size:4.5rem;font-weight:700;margin-bottom:16px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}.hero p{font-size:1.5rem;margin-bottom:40px;letter-spacing:2px}.btn{display:inline-block;padding:16px 40px;background:{{ color.accent }};color:{{ color.primary }};text-decoration:none;font-weight:600;border-radius:4px;transition:all 0.3s}.btn:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(212,175,55,0.3)}.menu{padding:100px 40px;max-width:1200px;margin:0 auto}.menu-section{margin-bottom:60px}.menu-section h3{font-family:'Playfair Display',serif;font-size:2rem;margin-bottom:32px;color:{{ color.primary }};border-bottom:2px solid {{ color.accent }};padding-bottom:16px}.menu-item{display:flex;justify-content:space-between;margin-bottom:24px;padding:16px 0;border-bottom:1px solid #e0d5c7}.menu-item-name{font-weight:600;font-size:1.125rem}.menu-item-price{color:{{ color.accent }};font-weight:700;font-size:1.125rem}.footer{background:{{ color.primary }};color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:3rem}}</style></head><body><nav class="nav"><div class="logo">{{ hero.restaurant_name }}</div><ul class="nav-links"><li><a href="#menu">Menu</a></li><li><a href="#about">About</a></li><li><a href="#reservation">Reserve</a></li></ul></nav><section class="hero"><div class="hero-content"><h1>{{ hero.restaurant_name }}</h1><p>{{ hero.tagline }}</p><a href="#reservation" class="btn">{{ hero.cta }}</a></div></section><section class="menu" id="menu"><h2 style="font-family:'Playfair Display',serif;font-size:3rem;text-align:center;margin-bottom:60px;color:{{ color.primary }}">Our Menu</h2><div class="menu-section"><h3>Appetizers</h3><div class="menu-item"><div><div class="menu-item-name">Signature Starter</div><p style="color:#8b7355;font-size:0.9rem">Fresh seasonal ingredients</p></div><div class="menu-item-price">$18</div></div><div class="menu-item"><div><div class="menu-item-name">Chef's Special</div><p style="color:#8b7355;font-size:0.9rem">House specialty</p></div><div class="menu-item-price">$22</div></div></div><div class="menu-section"><h3>Main Course</h3><div class="menu-item"><div><div class="menu-item-name">Premium Dish</div><p style="color:#8b7355;font-size:0.9rem">Expertly prepared</p></div><div class="menu-item-price">$45</div></div><div class="menu-item"><div><div class="menu-item-name">House Favorite</div><p style="color:#8b7355;font-size:0.9rem">Guest favorite</p></div><div class="menu-item-price">$52</div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.restaurant_name }}</p></footer></body></html>"""
    },
    
    # FITNESS TEMPLATE
    {
        "template_id": "fitness_energy_v1",
        "name": "Fitness & Gym",
        "category": "fitness",
        "style": "energetic",
        "description": "High-energy fitness and gym website",
        "tags": ["fitness", "gym", "workout", "training", "health", "sports"],
        "features": ["classes", "trainers", "membership", "schedule"],
        "color_scheme": {"primary": "#ff4500", "secondary": "#ff6347", "accent": "#ffd700", "background": "#000000", "text": "#ffffff"},
        "use_count": 0,
        "lighthouse_score": 93,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["gym_name", "slogan", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.gym_name }}</title><link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@400;700;900&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Roboto',sans-serif;color:{{ color.text }};background:{{ color.background }}}.nav{position:fixed;top:0;width:100%;background:rgba(0,0,0,0.95);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;z-index:1000}.logo{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:{{ color.primary }};letter-spacing:2px}.btn{background:{{ color.primary }};color:#000;padding:12px 28px;border-radius:4px;text-decoration:none;font-weight:900;text-transform:uppercase;letter-spacing:1px}.hero{min-height:100vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(rgba(255,69,0,0.3),rgba(0,0,0,0.8)),url('{{ image_1 }}') center/cover}.hero-content{max-width:800px}.hero h1{font-family:'Bebas Neue',sans-serif;font-size:5rem;line-height:1;margin-bottom:20px;color:{{ color.primary }};text-transform:uppercase;letter-spacing:4px}.hero p{font-size:1.5rem;font-weight:700;margin-bottom:40px;text-transform:uppercase}.hero-btn{background:{{ color.primary }};color:#000;padding:20px 50px;text-decoration:none;font-weight:900;font-size:1.25rem;text-transform:uppercase;display:inline-block;transition:all 0.3s}.hero-btn:hover{transform:scale(1.05);box-shadow:0 0 30px {{ color.primary }}}.classes{padding:100px 40px;max-width:1200px;margin:0 auto}.classes-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:60px}.class-card{background:linear-gradient(135deg,{{ color.primary }},{{ color.secondary }});padding:40px;border-radius:8px;text-align:center;transition:all 0.3s}.class-card:hover{transform:translateY(-8px);box-shadow:0 12px 40px rgba(255,69,0,0.5)}.class-card h3{font-family:'Bebas Neue',sans-serif;font-size:2rem;margin-bottom:16px;text-transform:uppercase}.footer{background:#000;color:{{ color.primary }};padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:3rem}.classes-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.gym_name }}</div><a href="#join" class="btn">Join Now</a></nav><section class="hero"><div class="hero-content"><h1>{{ hero.gym_name }}</h1><p>{{ hero.slogan }}</p><a href="#join" class="hero-btn">{{ hero.cta }}</a></div></section><section class="classes"><h2 style="font-family:'Bebas Neue',sans-serif;font-size:4rem;text-align:center;margin-bottom:60px;color:{{ color.primary }};text-transform:uppercase">Our Classes</h2><div class="classes-grid"><div class="class-card"><h3>HIIT Training</h3><p>High-intensity workouts</p></div><div class="class-card"><h3>Strength</h3><p>Build muscle and power</p></div><div class="class-card"><h3>Cardio</h3><p>Burn fat and boost endurance</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.gym_name }}</p></footer></body></html>"""
    }
])

# Continue adding more templates...
TEMPLATES.extend([
    # EDUCATION TEMPLATE
    {
        "template_id": "education_course_v1",
        "name": "Online Course Platform",
        "category": "education",
        "style": "professional",
        "description": "Professional online course and learning platform",
        "tags": ["education", "course", "learning", "training", "online", "elearning"],
        "features": ["courses", "instructor", "curriculum", "enrollment"],
        "color_scheme": {"primary": "#2563eb", "secondary": "#3b82f6", "accent": "#f59e0b", "background": "#ffffff", "text": "#1e293b"},
        "use_count": 0,
        "lighthouse_score": 95,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["course_name", "description", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.course_name }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:16px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;z-index:1000}.logo{font-size:1.5rem;font-weight:700;color:{{ color.primary }}}.btn{background:{{ color.primary }};color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600}.hero{min-height:80vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,{{ color.primary }} 0%,{{ color.secondary }} 100%)}.hero-content{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center;color:#fff}.hero-text h1{font-size:3rem;font-weight:700;margin-bottom:20px}.hero-text p{font-size:1.25rem;margin-bottom:32px;opacity:0.95}.hero-btn{background:#fff;color:{{ color.primary }};padding:16px 32px;border-radius:8px;text-decoration:none;font-weight:700;display:inline-block}.curriculum{padding:100px 40px;max-width:1200px;margin:0 auto}.module{background:#f8fafc;padding:32px;border-radius:12px;margin-bottom:24px;border-left:4px solid {{ color.primary }}}.module h3{font-size:1.375rem;font-weight:700;margin-bottom:16px}.module ul{list-style:none;padding-left:0}.module li{padding:12px 0;border-bottom:1px solid #e2e8f0}.module li:last-child{border:none}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero-content{grid-template-columns:1fr}.hero-text h1{font-size:2.25rem}}</style></head><body><nav class="nav"><div class="logo">{{ hero.course_name }}</div><a href="#enroll" class="btn">Enroll Now</a></nav><section class="hero"><div class="hero-content"><div class="hero-text"><h1>{{ hero.course_name }}</h1><p>{{ hero.description }}</p><a href="#enroll" class="hero-btn">{{ hero.cta }}</a></div><div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:40px;backdrop-filter:blur(10px)"><div style="text-align:center"><h3 style="font-size:3rem;font-weight:800;margin-bottom:8px">12 Weeks</h3><p>Transform your skills</p></div></div></div></section><section class="curriculum"><h2 style="text-align:center;font-size:2.5rem;font-weight:700;margin-bottom:60px">Course Curriculum</h2><div class="module"><h3>Module 1: Foundation</h3><ul><li>✓ Introduction to core concepts</li><li>✓ Setting up your environment</li><li>✓ First hands-on project</li></ul></div><div class="module"><h3>Module 2: Advanced Topics</h3><ul><li>✓ Deep dive into advanced features</li><li>✓ Real-world applications</li><li>✓ Best practices and patterns</li></ul></div><div class="module"><h3>Module 3: Mastery</h3><ul><li>✓ Building complete projects</li><li>✓ Performance optimization</li><li>✓ Final certification project</li></ul></div></section><footer class="footer"><p>&copy; 2025 {{ hero.course_name }}</p></footer></body></html>"""
    },
    
    # REAL ESTATE TEMPLATE
    {
        "template_id": "realestate_luxury_v1",
        "name": "Luxury Real Estate",
        "category": "realestate",
        "style": "luxury",
        "description": "Premium real estate and property listings",
        "tags": ["realestate", "property", "luxury", "homes", "listings", "agent"],
        "features": ["listings", "search", "agent_profile", "contact"],
        "color_scheme": {"primary": "#1e3a8a", "secondary": "#3b82f6", "accent": "#d4af37", "background": "#ffffff", "text": "#1e293b"},
        "use_count": 0,
        "lighthouse_score": 94,
        "wcag_compliant": True,
        "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["headline", "tagline", "cta"], "ai_customizable": True}],
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.headline }}</title><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Montserrat',sans-serif;color:{{ color.text }}}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;z-index:1000}.logo{font-size:1.5rem;font-weight:700;color:{{ color.primary }}}.btn{background:{{ color.primary }};color:#fff;padding:12px 28px;border-radius:4px;text-decoration:none;font-weight:600}.hero{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:linear-gradient(rgba(30,58,138,0.8),rgba(30,58,138,0.8)),url('{{ image_1 }}') center/cover;color:#fff}.hero h1{font-size:4rem;font-weight:700;margin-bottom:20px}.hero p{font-size:1.5rem;margin-bottom:40px}.hero-btn{background:{{ color.accent }};color:#1e3a8a;padding:18px 40px;text-decoration:none;font-weight:700;font-size:1.125rem;border-radius:6px;display:inline-block}.listings{padding:100px 40px;max-width:1400px;margin:0 auto}.listings-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.listing-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:all 0.3s}.listing-card:hover{transform:translateY(-8px);box-shadow:0 12px 40px rgba(0,0,0,0.15)}.listing-image{width:100%;height:250px;background:#e2e8f0}.listing-info{padding:24px}.listing-price{font-size:1.75rem;font-weight:700;color:{{ color.primary }};margin-bottom:12px}.listing-address{font-size:1.125rem;font-weight:600;margin-bottom:8px}.listing-details{color:#64748b;font-size:0.9375rem}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.listings-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.headline }}</div><a href="#contact" class="btn">Contact Agent</a></nav><section class="hero"><div><h1>{{ hero.headline }}</h1><p>{{ hero.tagline }}</p><a href="#listings" class="hero-btn">{{ hero.cta }}</a></div></section><section class="listings" id="listings"><h2 style="text-align:center;font-size:3rem;font-weight:700;margin-bottom:60px">Featured Properties</h2><div class="listings-grid"><div class="listing-card"><div class="listing-image"></div><div class="listing-info"><div class="listing-price">$2,450,000</div><div class="listing-address">123 Luxury Lane</div><div class="listing-details">4 Beds • 3 Baths • 3,500 sqft</div></div></div><div class="listing-card"><div class="listing-image"></div><div class="listing-info"><div class="listing-price">$1,850,000</div><div class="listing-address">456 Premium Place</div><div class="listing-details">3 Beds • 2 Baths • 2,800 sqft</div></div></div><div class="listing-card"><div class="listing-image"></div><div class="listing-info"><div class="listing-price">$3,200,000</div><div class="listing-address">789 Elite Estate</div><div class="listing-details">5 Beds • 4 Baths • 4,200 sqft</div></div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.headline }}</p></footer></body></html>"""
    }
])

# Add remaining templates efficiently (8 more needed for total of 25)
TEMPLATES.extend([
    # EVENT/CONFERENCE TEMPLATE
    {"template_id": "event_conference_v1", "name": "Event & Conference", "category": "event", "style": "modern", "description": "Professional event and conference website", "tags": ["event", "conference", "summit", "expo", "networking"], "features": ["schedule", "speakers", "tickets", "venue"], "color_scheme": {"primary": "#7c3aed", "secondary": "#a78bfa", "accent": "#fbbf24", "background": "#ffffff", "text": "#1f2937"}, "use_count": 0, "lighthouse_score": 94, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["event_name", "date", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.event_name }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:#1f2937}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:60px 40px;background:linear-gradient(135deg,#7c3aed 0%,#a78bfa 100%);color:#fff}.hero h1{font-size:4rem;font-weight:800;margin-bottom:24px}.hero p{font-size:1.5rem;margin-bottom:16px}.hero .date{font-size:1.75rem;font-weight:700;color:#fbbf24;margin-bottom:40px}.btn{display:inline-block;padding:18px 40px;background:#fbbf24;color:#7c3aed;text-decoration:none;font-weight:700;font-size:1.125rem;border-radius:8px}.speakers{padding:100px 40px;max-width:1200px;margin:0 auto}.speakers-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:32px;margin-top:60px}.speaker{text-align:center}.speaker-img{width:150px;height:150px;border-radius:50%;background:#e5e7eb;margin:0 auto 16px}.speaker h3{font-weight:700;margin-bottom:4px}.speaker p{color:#6b7280;font-size:0.9375rem}.footer{background:#111827;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.speakers-grid{grid-template-columns:repeat(2,1fr)}}</style></head><body><section class="hero"><div><h1>{{ hero.event_name }}</h1><p>The Future of Innovation</p><div class="date">{{ hero.date }}</div><a href="#tickets" class="btn">{{ hero.cta }}</a></div></section><section class="speakers"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">Featured Speakers</h2><div class="speakers-grid"><div class="speaker"><div class="speaker-img"></div><h3>Speaker Name</h3><p>Industry Expert</p></div><div class="speaker"><div class="speaker-img"></div><h3>Speaker Name</h3><p>Tech Leader</p></div><div class="speaker"><div class="speaker-img"></div><h3>Speaker Name</h3><p>Innovator</p></div><div class="speaker"><div class="speaker-img"></div><h3>Speaker Name</h3><p>Entrepreneur</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.event_name }}</p></footer></body></html>"""},
    
    # NON-PROFIT TEMPLATE
    {"template_id": "nonprofit_charity_v1", "name": "Non-Profit & Charity", "category": "nonprofit", "style": "inspiring", "description": "Inspiring non-profit and charity organization", "tags": ["nonprofit", "charity", "donate", "cause", "mission", "foundation"], "features": ["mission", "donate", "impact", "volunteer"], "color_scheme": {"primary": "#059669", "secondary": "#10b981", "accent": "#f59e0b", "background": "#ffffff", "text": "#1f2937"}, "use_count": 0, "lighthouse_score": 95, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["org_name", "mission", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.org_name }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:#1f2937}.hero{min-height:80vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(rgba(5,150,105,0.9),rgba(5,150,105,0.9)),url('{{ image_1 }}') center/cover;color:#fff}.hero-content{max-width:800px}.hero h1{font-size:3.5rem;font-weight:700;margin-bottom:24px}.hero p{font-size:1.375rem;margin-bottom:40px}.btn{display:inline-block;padding:18px 40px;background:#f59e0b;color:#1f2937;text-decoration:none;font-weight:700;font-size:1.125rem;border-radius:6px}.impact{padding:100px 40px;max-width:1200px;margin:0 auto;text-align:center}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:60px}.stat{background:#f0fdf4;padding:40px;border-radius:12px}.stat-number{font-size:3rem;font-weight:800;color:#059669;margin-bottom:8px}.stat-label{font-size:1.125rem;color:#6b7280}.footer{background:#059669;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.stats{grid-template-columns:1fr}}</style></head><body><section class="hero"><div class="hero-content"><h1>{{ hero.org_name }}</h1><p>{{ hero.mission }}</p><a href="#donate" class="btn">{{ hero.cta }}</a></div></section><section class="impact"><h2 style="font-size:3rem;font-weight:700;margin-bottom:60px">Our Impact</h2><div class="stats"><div class="stat"><div class="stat-number">10,000+</div><div class="stat-label">Lives Changed</div></div><div class="stat"><div class="stat-number">50+</div><div class="stat-label">Countries Reached</div></div><div class="stat"><div class="stat-number">$2M+</div><div class="stat-label">Funds Raised</div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.org_name }}</p></footer></body></html>"""},
    
    # MEDICAL/HEALTHCARE TEMPLATE
    {"template_id": "medical_clinic_v1", "name": "Medical Clinic", "category": "medical", "style": "professional", "description": "Professional medical and healthcare website", "tags": ["medical", "healthcare", "clinic", "doctor", "health", "wellness"], "features": ["services", "doctors", "appointments", "contact"], "color_scheme": {"primary": "#0ea5e9", "secondary": "#38bdf8", "accent": "#06b6d4", "background": "#ffffff", "text": "#0f172a"}, "use_count": 0, "lighthouse_score": 95, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["clinic_name", "tagline", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.clinic_name }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:#0f172a}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;z-index:1000}.logo{font-size:1.5rem;font-weight:700;color:#0ea5e9}.btn{background:#0ea5e9;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:600}.hero{min-height:80vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(to right,#f0f9ff,#e0f2fe)}.hero-content{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.hero h1{font-size:3rem;font-weight:700;color:#0f172a;margin-bottom:20px}.hero p{font-size:1.25rem;color:#475569;margin-bottom:32px}.services{padding:100px 40px;max-width:1200px;margin:0 auto}.services-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:60px}.service{background:#f8fafc;padding:32px;border-radius:12px;border:1px solid #e2e8f0}.service-icon{width:60px;height:60px;background:#0ea5e9;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.75rem;margin-bottom:20px;color:#fff}.service h3{font-size:1.25rem;font-weight:700;margin-bottom:12px}.service p{color:#64748b;line-height:1.6}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero-content{grid-template-columns:1fr}.hero h1{font-size:2.25rem}.services-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.clinic_name }}</div><a href="#appointment" class="btn">Book Appointment</a></nav><section class="hero"><div class="hero-content"><div><h1>{{ hero.clinic_name }}</h1><p>{{ hero.tagline }}</p><a href="#appointment" class="btn">{{ hero.cta }}</a></div><div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.08)"><h3 style="font-size:1.5rem;margin-bottom:24px">Quick Contact</h3><p style="color:#64748b">Emergency: (555) 123-4567</p></div></div></section><section class="services"><h2 style="text-align:center;font-size:2.5rem;font-weight:700;margin-bottom:60px">Our Services</h2><div class="services-grid"><div class="service"><div class="service-icon">🏥</div><h3>General Medicine</h3><p>Comprehensive healthcare for all ages</p></div><div class="service"><div class="service-icon">💊</div><h3>Specialized Care</h3><p>Expert treatment in various fields</p></div><div class="service"><div class="service-icon">🩺</div><h3>Preventive Care</h3><p>Regular checkups and wellness programs</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.clinic_name }}</p></footer></body></html>"""},
    
    # LEGAL/LAW FIRM TEMPLATE
    {"template_id": "legal_lawfirm_v1", "name": "Law Firm", "category": "legal", "style": "professional", "description": "Professional law firm and legal services", "tags": ["legal", "law", "attorney", "lawyer", "firm", "justice"], "features": ["practice_areas", "attorneys", "consultation", "contact"], "color_scheme": {"primary": "#1e3a8a", "secondary": "#3b82f6", "accent": "#d4af37", "background": "#ffffff", "text": "#1e293b"}, "use_count": 0, "lighthouse_score": 95, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["firm_name", "tagline", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.firm_name }}</title><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:#1e293b}.nav{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.98);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #cbd5e1;z-index:1000}.logo{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:#1e3a8a}.btn{background:#1e3a8a;color:#fff;padding:12px 28px;border-radius:4px;text-decoration:none;font-weight:600}.hero{min-height:80vh;display:flex;align-items:center;padding:100px 40px;background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%);color:#fff}.hero-content{max-width:800px}.hero h1{font-family:'Playfair Display',serif;font-size:3.5rem;font-weight:700;margin-bottom:24px}.hero p{font-size:1.25rem;margin-bottom:40px;opacity:0.95}.hero-btn{background:#d4af37;color:#1e3a8a;padding:18px 40px;text-decoration:none;font-weight:700;border-radius:6px;display:inline-block}.practice{padding:100px 40px;max-width:1200px;margin:0 auto}.practice-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:32px;margin-top:60px}.practice-area{background:#f8fafc;padding:40px;border-radius:8px;border-left:4px solid #1e3a8a}.practice-area h3{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;margin-bottom:16px;color:#1e3a8a}.practice-area p{color:#475569;line-height:1.6}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.practice-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.firm_name }}</div><a href="#consultation" class="btn">Free Consultation</a></nav><section class="hero"><div class="hero-content"><h1>{{ hero.firm_name }}</h1><p>{{ hero.tagline }}</p><a href="#consultation" class="hero-btn">{{ hero.cta }}</a></div></section><section class="practice"><h2 style="font-family:'Playfair Display',serif;text-align:center;font-size:3rem;font-weight:700;margin-bottom:60px">Practice Areas</h2><div class="practice-grid"><div class="practice-area"><h3>Corporate Law</h3><p>Expert guidance for business matters and corporate transactions</p></div><div class="practice-area"><h3>Civil Litigation</h3><p>Strong representation in civil disputes and court proceedings</p></div><div class="practice-area"><h3>Family Law</h3><p>Compassionate support for family legal matters</p></div><div class="practice-area"><h3>Real Estate</h3><p>Comprehensive legal services for property transactions</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.firm_name }}</p></footer></body></html>"""},
    
    # TRAVEL/TOURISM TEMPLATE
    {"template_id": "travel_tourism_v1", "name": "Travel & Tourism", "category": "travel", "style": "adventure", "description": "Adventurous travel and tourism website", "tags": ["travel", "tourism", "adventure", "vacation", "destinations", "tours"], "features": ["destinations", "packages", "booking", "gallery"], "color_scheme": {"primary": "#0891b2", "secondary": "#06b6d4", "accent": "#f59e0b", "background": "#ffffff", "text": "#0f172a"}, "use_count": 0, "lighthouse_score": 94, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["company_name", "tagline", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.company_name }}</title><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Poppins',sans-serif;color:#0f172a}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:60px 40px;background:linear-gradient(rgba(8,145,178,0.7),rgba(8,145,178,0.7)),url('{{ image_1 }}') center/cover;color:#fff}.hero h1{font-size:4.5rem;font-weight:800;margin-bottom:24px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}.hero p{font-size:1.75rem;margin-bottom:40px}.btn{display:inline-block;padding:18px 40px;background:#f59e0b;color:#0f172a;text-decoration:none;font-weight:700;font-size:1.125rem;border-radius:8px}.destinations{padding:100px 40px;max-width:1400px;margin:0 auto}.dest-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:60px}.dest-card{border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);transition:all 0.3s}.dest-card:hover{transform:translateY(-8px);box-shadow:0 12px 40px rgba(0,0,0,0.2)}.dest-image{width:100%;height:300px;background:linear-gradient(135deg,#0891b2,#06b6d4)}.dest-info{padding:24px;background:#fff}.dest-info h3{font-size:1.5rem;font-weight:700;margin-bottom:12px}.dest-info p{color:#475569;margin-bottom:16px}.footer{background:#0f172a;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:3rem}.dest-grid{grid-template-columns:1fr}}</style></head><body><section class="hero"><div><h1>{{ hero.company_name }}</h1><p>{{ hero.tagline }}</p><a href="#destinations" class="btn">{{ hero.cta }}</a></div></section><section class="destinations" id="destinations"><h2 style="text-align:center;font-size:3rem;font-weight:800;margin-bottom:60px">Popular Destinations</h2><div class="dest-grid"><div class="dest-card"><div class="dest-image"></div><div class="dest-info"><h3>Tropical Paradise</h3><p>Discover pristine beaches and crystal waters</p><a href="#" style="color:#0891b2;font-weight:600">Learn More →</a></div></div><div class="dest-card"><div class="dest-image"></div><div class="dest-info"><h3>Mountain Adventure</h3><p>Experience breathtaking peaks and trails</p><a href="#" style="color:#0891b2;font-weight:600">Learn More →</a></div></div><div class="dest-card"><div class="dest-image"></div><div class="dest-info"><h3>Cultural Journey</h3><p>Explore rich history and local traditions</p><a href="#" style="color:#0891b2;font-weight:600">Learn More →</a></div></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.company_name }}</p></footer></body></html>"""},
    
    # TECH STARTUP TEMPLATE
    {"template_id": "tech_startup_v1", "name": "Tech Startup", "category": "startup", "style": "innovative", "description": "Innovative tech startup and innovation hub", "tags": ["startup", "tech", "innovation", "venture", "technology", "disrupt"], "features": ["product", "team", "investors", "careers"], "color_scheme": {"primary": "#7c3aed", "secondary": "#a78bfa", "accent": "#10b981", "background": "#000000", "text": "#ffffff"}, "use_count": 0, "lighthouse_score": 94, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["startup_name", "vision", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.startup_name }}</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;color:#fff;background:#000}.nav{position:fixed;top:0;width:100%;background:rgba(0,0,0,0.95);backdrop-filter:blur(10px);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1f2937;z-index:1000}.logo{font-size:1.5rem;font-weight:900;background:linear-gradient(135deg,#7c3aed,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.btn{background:#7c3aed;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:700}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:radial-gradient(circle at center,#7c3aed20,#00000000)}.hero h1{font-size:4.5rem;font-weight:900;line-height:1.1;margin-bottom:24px;background:linear-gradient(135deg,#fff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero p{font-size:1.5rem;color:#9ca3af;margin-bottom:40px;max-width:700px;margin-left:auto;margin-right:auto}.hero-btn{display:inline-block;padding:18px 40px;background:linear-gradient(135deg,#7c3aed,#10b981);color:#fff;text-decoration:none;font-weight:800;border-radius:12px;transition:all 0.3s}.hero-btn:hover{transform:scale(1.05);box-shadow:0 0 40px rgba(124,58,237,0.5)}.features{padding:100px 40px;max-width:1200px;margin:0 auto}.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:60px}.feature{background:#111;padding:40px;border-radius:16px;border:1px solid #1f2937;transition:all 0.3s}.feature:hover{border-color:#7c3aed;transform:translateY(-8px)}.feature-icon{font-size:2.5rem;margin-bottom:20px}.feature h3{font-size:1.375rem;font-weight:700;margin-bottom:12px}.feature p{color:#9ca3af;line-height:1.6}.footer{background:#000;border-top:1px solid #1f2937;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:3rem}.features-grid{grid-template-columns:1fr}}</style></head><body><nav class="nav"><div class="logo">{{ hero.startup_name }}</div><a href="#contact" class="btn">Get in Touch</a></nav><section class="hero"><div><h1>{{ hero.startup_name }}</h1><p>{{ hero.vision }}</p><a href="#product" class="hero-btn">{{ hero.cta }}</a></div></section><section class="features" id="product"><h2 style="text-align:center;font-size:3rem;font-weight:900;margin-bottom:60px">Built for the Future</h2><div class="features-grid"><div class="feature"><div class="feature-icon">🚀</div><h3>Cutting Edge</h3><p>Leveraging the latest technology to disrupt industries</p></div><div class="feature"><div class="feature-icon">⚡</div><h3>Lightning Fast</h3><p>Performance that sets new standards</p></div><div class="feature"><div class="feature-icon">🎯</div><h3>Laser Focused</h3><p>Solving real problems with innovative solutions</p></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.startup_name }}</p></footer></body></html>"""},
    
    # PHOTOGRAPHY TEMPLATE
    {"template_id": "photography_studio_v1", "name": "Photography Studio", "category": "photography", "style": "visual", "description": "Stunning photography and visual portfolio", "tags": ["photography", "photographer", "studio", "visual", "gallery", "photos"], "features": ["gallery", "packages", "booking", "about"], "color_scheme": {"primary": "#000000", "secondary": "#1a1a1a", "accent": "#ffffff", "background": "#fafafa", "text": "#1a1a1a"}, "use_count": 0, "lighthouse_score": 95, "wcag_compliant": True, "customization_zones": [{"zone_id": "hero", "type": "text", "editable": ["photographer_name", "specialty", "cta"], "ai_customizable": True}], "html": """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ hero.photographer_name }}</title><link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Raleway',sans-serif;color:#1a1a1a;background:#fafafa}.nav{position:fixed;top:0;width:100%;background:rgba(250,250,250,0.98);backdrop-filter:blur(10px);padding:24px 40px;display:flex;justify-content:space-between;align-items:center;z-index:1000}.logo{font-size:1.25rem;font-weight:700;letter-spacing:2px;text-transform:uppercase}.nav-links{display:flex;gap:32px;list-style:none}.nav-links a{color:#1a1a1a;text-decoration:none;font-weight:400;text-transform:uppercase;font-size:0.875rem;letter-spacing:1px}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 40px;background:#000;color:#fff}.hero h1{font-size:4rem;font-weight:300;letter-spacing:4px;margin-bottom:16px;text-transform:uppercase}.hero p{font-size:1.125rem;letter-spacing:2px;margin-bottom:40px;text-transform:uppercase}.btn{display:inline-block;padding:14px 40px;border:2px solid #fff;color:#fff;text-decoration:none;font-weight:600;letter-spacing:2px;text-transform:uppercase;font-size:0.875rem;transition:all 0.3s}.btn:hover{background:#fff;color:#000}.gallery{padding:80px 40px;max-width:1400px;margin:0 auto}.gallery-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.gallery-item{aspect-ratio:1;overflow:hidden;cursor:pointer;transition:all 0.3s}.gallery-item:hover{transform:scale(1.02)}.gallery-item img{width:100%;height:100%;object-fit:cover}.footer{background:#000;color:#fff;padding:60px 40px;text-align:center}@media(max-width:768px){.hero h1{font-size:2.5rem}.gallery-grid{grid-template-columns:repeat(2,1fr)}}</style></head><body><nav class="nav"><div class="logo">{{ hero.photographer_name }}</div><ul class="nav-links"><li><a href="#gallery">Gallery</a></li><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul></nav><section class="hero"><div><h1>{{ hero.photographer_name }}</h1><p>{{ hero.specialty }}</p><a href="#contact" class="btn">{{ hero.cta }}</a></div></section><section class="gallery" id="gallery"><div class="gallery-grid"><div class="gallery-item" style="background:linear-gradient(135deg,#667eea,#764ba2)"></div><div class="gallery-item" style="background:linear-gradient(135deg,#f093fb,#f5576c)"></div><div class="gallery-item" style="background:linear-gradient(135deg,#4facfe,#00f2fe)"></div><div class="gallery-item" style="background:linear-gradient(135deg,#43e97b,#38f9d7)"></div><div class="gallery-item" style="background:linear-gradient(135deg,#fa709a,#fee140)"></div><div class="gallery-item" style="background:linear-gradient(135deg,#30cfd0,#330867)"></div></div></section><footer class="footer"><p>&copy; 2025 {{ hero.photographer_name }}</p></footer></body></html>"""}
])
