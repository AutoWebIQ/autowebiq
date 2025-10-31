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
COMPONENTS = []
