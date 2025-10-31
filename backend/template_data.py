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
    }
]

# I'll continue with more templates in the next file...
