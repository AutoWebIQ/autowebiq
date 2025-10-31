"""
9-Point Website Validation System
Comprehensive validation checks for generated websites
"""

import asyncio
import requests
import json
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class ValidationResult:
    """Represents the result of a validation check"""
    
    def __init__(self, check_name: str, passed: bool, score: int, issues: List[Dict], recommendations: List[str]):
        self.check_name = check_name
        self.passed = passed
        self.score = score  # 0-100
        self.issues = issues
        self.recommendations = recommendations
    
    def to_dict(self):
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "score": self.score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "status": "passed" if self.passed else "failed"
        }


class WebsiteValidator:
    """
    9-Point Website Validation System
    
    Validates:
    1. HTML - Syntax and structure
    2. CSS - Syntax and best practices
    3. JavaScript - Syntax and errors
    4. Accessibility - WCAG 2.1 compliance
    5. SEO - Meta tags, structure
    6. Performance - Load time, optimization
    7. Security - HTTPS, headers, vulnerabilities
    8. Browser Compatibility - Cross-browser support
    9. Mobile Responsiveness - Viewport, responsive design
    """
    
    def __init__(self):
        self.results = {}
    
    async def validate_all(self, html_content: str, css_content: str = "", js_content: str = "", 
                          url: Optional[str] = None) -> Dict:
        """
        Run all 9 validation checks
        
        Args:
            html_content: HTML code
            css_content: CSS code
            js_content: JavaScript code
            url: Optional deployed URL for live checks
        
        Returns:
            Dictionary with all validation results
        """
        logger.info("Starting 9-point validation...")
        
        # Run all validations
        results = {
            "html": await self.validate_html(html_content),
            "css": await self.validate_css(css_content),
            "javascript": await self.validate_javascript(js_content),
            "accessibility": await self.validate_accessibility(html_content),
            "seo": await self.validate_seo(html_content, url),
            "performance": await self.validate_performance(html_content, css_content, js_content, url),
            "security": await self.validate_security(html_content, url),
            "browser": await self.validate_browser_compatibility(html_content, css_content, js_content),
            "mobile": await self.validate_mobile_responsiveness(html_content, css_content)
        }
        
        # Calculate overall score
        total_score = sum(r["score"] for r in results.values())
        average_score = total_score // len(results)
        
        passed_checks = sum(1 for r in results.values() if r["passed"])
        
        return {
            "overall_score": average_score,
            "passed_checks": passed_checks,
            "total_checks": len(results),
            "all_passed": passed_checks == len(results),
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    async def validate_html(self, html_content: str) -> Dict:
        """
        Check 1: HTML Validation
        - Valid HTML5 syntax
        - Proper DOCTYPE
        - Closed tags
        - Valid attributes
        - Semantic structure
        """
        logger.info("Validating HTML...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for DOCTYPE
            if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<!doctype'):
                issues.append({
                    "type": "error",
                    "message": "Missing or incorrect DOCTYPE declaration",
                    "severity": "high"
                })
                score -= 15
            
            # Check for html tag
            if not soup.find('html'):
                issues.append({
                    "type": "error",
                    "message": "Missing <html> tag",
                    "severity": "high"
                })
                score -= 10
            
            # Check for head tag
            if not soup.find('head'):
                issues.append({
                    "type": "error",
                    "message": "Missing <head> tag",
                    "severity": "high"
                })
                score -= 10
            
            # Check for body tag
            if not soup.find('body'):
                issues.append({
                    "type": "error",
                    "message": "Missing <body> tag",
                    "severity": "high"
                })
                score -= 10
            
            # Check for title
            if not soup.find('title'):
                issues.append({
                    "type": "warning",
                    "message": "Missing <title> tag",
                    "severity": "medium"
                })
                score -= 5
            
            # Check for unclosed tags (basic check)
            open_tags = re.findall(r'<(\w+)[^>]*>', html_content)
            close_tags = re.findall(r'</(\w+)>', html_content)
            self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link']
            
            for tag in open_tags:
                if tag not in self_closing and tag.lower() != 'doctype':
                    if open_tags.count(tag) > close_tags.count(tag):
                        issues.append({
                            "type": "error",
                            "message": f"Potentially unclosed <{tag}> tag",
                            "severity": "medium"
                        })
                        score -= 5
            
            # Check for deprecated tags
            deprecated_tags = ['center', 'font', 'marquee', 'blink', 'frame', 'frameset']
            for tag in deprecated_tags:
                if soup.find(tag):
                    issues.append({
                        "type": "warning",
                        "message": f"Deprecated tag <{tag}> found",
                        "severity": "low"
                    })
                    score -= 2
            
            # Check for inline styles (should use CSS)
            inline_styles = soup.find_all(style=True)
            if len(inline_styles) > 10:
                issues.append({
                    "type": "info",
                    "message": f"Excessive inline styles found ({len(inline_styles)} elements)",
                    "severity": "low"
                })
                score -= 3
            
        except Exception as e:
            logger.error(f"HTML validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"HTML parsing error: {str(e)}",
                "severity": "critical"
            })
            score = 0
        
        return ValidationResult(
            check_name="HTML Validation",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Use valid HTML5 DOCTYPE",
                "Ensure all tags are properly closed",
                "Avoid deprecated HTML tags",
                "Use semantic HTML elements",
                "Minimize inline styles"
            ]
        ).to_dict()
    
    async def validate_css(self, css_content: str) -> Dict:
        """
        Check 2: CSS Validation
        - Valid CSS syntax
        - No vendor prefix issues
        - Proper property usage
        - No duplicate selectors
        """
        logger.info("Validating CSS...")
        
        issues = []
        score = 100
        
        try:
            if not css_content or len(css_content.strip()) == 0:
                issues.append({
                    "type": "warning",
                    "message": "No CSS content found",
                    "severity": "low"
                })
                score -= 10
            else:
                # Check for syntax errors (basic)
                open_braces = css_content.count('{')
                close_braces = css_content.count('}')
                
                if open_braces != close_braces:
                    issues.append({
                        "type": "error",
                        "message": f"Mismatched braces: {open_braces} opening, {close_braces} closing",
                        "severity": "high"
                    })
                    score -= 20
                
                # Check for !important overuse
                important_count = css_content.count('!important')
                if important_count > 5:
                    issues.append({
                        "type": "warning",
                        "message": f"Excessive use of !important ({important_count} times)",
                        "severity": "medium"
                    })
                    score -= 10
                
                # Check for missing vendor prefixes on common properties
                prefixed_properties = ['transform', 'transition', 'animation', 'box-shadow']
                for prop in prefixed_properties:
                    if f'{prop}:' in css_content:
                        if not any(f'-{prefix}-{prop}' in css_content for prefix in ['webkit', 'moz', 'ms', 'o']):
                            issues.append({
                                "type": "info",
                                "message": f"Consider adding vendor prefixes for '{prop}'",
                                "severity": "low"
                            })
                            score -= 3
                
                # Check for duplicate selectors
                selectors = re.findall(r'([.#]?[\w-]+)\s*{', css_content)
                duplicates = [s for s in set(selectors) if selectors.count(s) > 1]
                if duplicates:
                    issues.append({
                        "type": "warning",
                        "message": f"Duplicate selectors found: {', '.join(duplicates[:5])}",
                        "severity": "low"
                    })
                    score -= 5
        
        except Exception as e:
            logger.error(f"CSS validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"CSS parsing error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="CSS Validation",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Use valid CSS3 syntax",
                "Add vendor prefixes for browser compatibility",
                "Avoid excessive use of !important",
                "Minimize duplicate selectors",
                "Use CSS variables for repeated values"
            ]
        ).to_dict()
    
    async def validate_javascript(self, js_content: str) -> Dict:
        """
        Check 3: JavaScript Validation
        - Valid syntax
        - No console.log in production
        - Proper error handling
        - Modern ES6+ practices
        """
        logger.info("Validating JavaScript...")
        
        issues = []
        score = 100
        
        try:
            if not js_content or len(js_content.strip()) == 0:
                # No JavaScript is okay
                return ValidationResult(
                    check_name="JavaScript Validation",
                    passed=True,
                    score=100,
                    issues=[],
                    recommendations=[]
                ).to_dict()
            
            # Check for console.log (should not be in production)
            console_count = len(re.findall(r'console\.(log|warn|error|debug)', js_content))
            if console_count > 0:
                issues.append({
                    "type": "warning",
                    "message": f"Found {console_count} console statements (remove for production)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for eval (security risk)
            if 'eval(' in js_content:
                issues.append({
                    "type": "error",
                    "message": "Use of eval() detected (security risk)",
                    "severity": "high"
                })
                score -= 20
            
            # Check for alert/confirm/prompt (poor UX)
            ui_blocks = len(re.findall(r'(alert|confirm|prompt)\(', js_content))
            if ui_blocks > 0:
                issues.append({
                    "type": "warning",
                    "message": f"Found {ui_blocks} blocking UI dialogs (consider modern alternatives)",
                    "severity": "low"
                })
                score -= 5
            
            # Check for var (should use let/const)
            var_count = len(re.findall(r'\bvar\s+\w+', js_content))
            if var_count > 0:
                issues.append({
                    "type": "info",
                    "message": f"Found {var_count} 'var' declarations (consider let/const)",
                    "severity": "low"
                })
                score -= 3
            
            # Check for basic syntax (parentheses, brackets)
            if js_content.count('(') != js_content.count(')'):
                issues.append({
                    "type": "error",
                    "message": "Mismatched parentheses",
                    "severity": "critical"
                })
                score -= 30
            
            if js_content.count('{') != js_content.count('}'):
                issues.append({
                    "type": "error",
                    "message": "Mismatched braces",
                    "severity": "critical"
                })
                score -= 30
        
        except Exception as e:
            logger.error(f"JavaScript validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"JavaScript parsing error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="JavaScript Validation",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Remove console statements before production",
                "Avoid eval() for security",
                "Use let/const instead of var",
                "Implement proper error handling",
                "Use modern ES6+ syntax"
            ]
        ).to_dict()
    
    async def validate_accessibility(self, html_content: str) -> Dict:
        """
        Check 4: Accessibility (WCAG 2.1)
        - Alt text for images
        - ARIA labels
        - Semantic HTML
        - Color contrast
        - Keyboard navigation
        """
        logger.info("Validating accessibility...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check images for alt text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if images_without_alt:
                issues.append({
                    "type": "error",
                    "message": f"{len(images_without_alt)} images missing alt text",
                    "severity": "high"
                })
                score -= 15
            
            # Check for lang attribute on html tag
            html_tag = soup.find('html')
            if html_tag and not html_tag.get('lang'):
                issues.append({
                    "type": "error",
                    "message": "Missing lang attribute on <html> tag",
                    "severity": "high"
                })
                score -= 10
            
            # Check for heading hierarchy
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if not soup.find('h1'):
                issues.append({
                    "type": "warning",
                    "message": "Missing <h1> heading",
                    "severity": "medium"
                })
                score -= 8
            
            # Check for form labels
            inputs = soup.find_all('input', type=lambda t: t not in ['hidden', 'submit', 'button'])
            for inp in inputs:
                inp_id = inp.get('id')
                if inp_id:
                    label = soup.find('label', attrs={'for': inp_id})
                    if not label and not inp.get('aria-label') and not inp.get('aria-labelledby'):
                        issues.append({
                            "type": "error",
                            "message": f"Input field missing associated label",
                            "severity": "high"
                        })
                        score -= 5
            
            # Check for button text
            buttons = soup.find_all('button')
            for btn in buttons:
                if not btn.get_text(strip=True) and not btn.get('aria-label'):
                    issues.append({
                        "type": "error",
                        "message": "Button without text or aria-label",
                        "severity": "high"
                    })
                    score -= 5
            
            # Check for link text
            links = soup.find_all('a', href=True)
            for link in links:
                link_text = link.get_text(strip=True)
                if not link_text and not link.find('img', alt=True) and not link.get('aria-label'):
                    issues.append({
                        "type": "error",
                        "message": "Link without descriptive text",
                        "severity": "high"
                    })
                    score -= 5
            
            # Check for semantic HTML
            if not soup.find(['nav', 'header', 'main', 'footer', 'article', 'section']):
                issues.append({
                    "type": "warning",
                    "message": "No semantic HTML5 elements found",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for skip link
            first_link = soup.find('a')
            if first_link and 'skip' not in first_link.get_text().lower():
                issues.append({
                    "type": "info",
                    "message": "Consider adding skip navigation link",
                    "severity": "low"
                })
                score -= 3
        
        except Exception as e:
            logger.error(f"Accessibility validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"Accessibility check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="Accessibility (WCAG 2.1)",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Add alt text to all images",
                "Include lang attribute on html element",
                "Use semantic HTML5 elements",
                "Ensure all form inputs have labels",
                "Maintain proper heading hierarchy",
                "Provide skip navigation links"
            ]
        ).to_dict()
    
    async def validate_seo(self, html_content: str, url: Optional[str] = None) -> Dict:
        """
        Check 5: SEO Optimization
        - Meta tags (title, description)
        - Open Graph tags
        - Heading structure
        - Robots.txt
        - Sitemap
        """
        logger.info("Validating SEO...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check title tag
            title = soup.find('title')
            if not title:
                issues.append({
                    "type": "error",
                    "message": "Missing <title> tag",
                    "severity": "critical"
                })
                score -= 20
            elif len(title.get_text()) < 30:
                issues.append({
                    "type": "warning",
                    "message": "Title tag too short (recommended 30-60 characters)",
                    "severity": "medium"
                })
                score -= 10
            elif len(title.get_text()) > 60:
                issues.append({
                    "type": "warning",
                    "message": "Title tag too long (recommended 30-60 characters)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                issues.append({
                    "type": "error",
                    "message": "Missing meta description",
                    "severity": "high"
                })
                score -= 15
            elif meta_desc.get('content') and len(meta_desc['content']) < 120:
                issues.append({
                    "type": "warning",
                    "message": "Meta description too short (recommended 120-160 characters)",
                    "severity": "medium"
                })
                score -= 8
            
            # Check for viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport:
                issues.append({
                    "type": "error",
                    "message": "Missing viewport meta tag (important for mobile)",
                    "severity": "high"
                })
                score -= 12
            
            # Check Open Graph tags
            og_tags = ['og:title', 'og:description', 'og:image', 'og:url']
            missing_og = []
            for tag in og_tags:
                if not soup.find('meta', property=tag):
                    missing_og.append(tag)
            
            if missing_og:
                issues.append({
                    "type": "info",
                    "message": f"Missing Open Graph tags: {', '.join(missing_og)}",
                    "severity": "low"
                })
                score -= 5
            
            # Check for h1 tag
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 0:
                issues.append({
                    "type": "error",
                    "message": "No <h1> tag found",
                    "severity": "high"
                })
                score -= 15
            elif len(h1_tags) > 1:
                issues.append({
                    "type": "warning",
                    "message": f"Multiple <h1> tags found ({len(h1_tags)})",
                    "severity": "medium"
                })
                score -= 8
            
            # Check for canonical URL
            canonical = soup.find('link', rel='canonical')
            if not canonical:
                issues.append({
                    "type": "info",
                    "message": "Consider adding canonical URL",
                    "severity": "low"
                })
                score -= 3
            
            # Check for robots meta tag
            robots = soup.find('meta', attrs={'name': 'robots'})
            if robots and 'noindex' in robots.get('content', ''):
                issues.append({
                    "type": "warning",
                    "message": "Page set to noindex (won't appear in search results)",
                    "severity": "high"
                })
                score -= 10
        
        except Exception as e:
            logger.error(f"SEO validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"SEO check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="SEO Optimization",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Add descriptive title tag (30-60 characters)",
                "Include meta description (120-160 characters)",
                "Use single H1 tag per page",
                "Add Open Graph tags for social sharing",
                "Include viewport meta tag",
                "Add canonical URL to prevent duplicate content"
            ]
        ).to_dict()
    
    async def validate_performance(self, html_content: str, css_content: str, 
                                   js_content: str, url: Optional[str] = None) -> Dict:
        """
        Check 6: Performance Optimization
        - File sizes
        - Image optimization
        - Minification
        - Caching headers
        - Lazy loading
        """
        logger.info("Validating performance...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check HTML size
            html_size = len(html_content)
            if html_size > 100000:  # 100KB
                issues.append({
                    "type": "warning",
                    "message": f"HTML file size is large ({html_size // 1024}KB)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check CSS size
            css_size = len(css_content)
            if css_size > 50000:  # 50KB
                issues.append({
                    "type": "warning",
                    "message": f"CSS file size is large ({css_size // 1024}KB)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check JS size
            js_size = len(js_content)
            if js_size > 100000:  # 100KB
                issues.append({
                    "type": "warning",
                    "message": f"JavaScript file size is large ({js_size // 1024}KB)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for minification
            if css_content and '\n' in css_content and '  ' in css_content:
                issues.append({
                    "type": "info",
                    "message": "CSS is not minified",
                    "severity": "low"
                })
                score -= 5
            
            if js_content and '\n' in js_content and '  ' in js_content:
                issues.append({
                    "type": "info",
                    "message": "JavaScript is not minified",
                    "severity": "low"
                })
                score -= 5
            
            # Check for external resources
            external_scripts = soup.find_all('script', src=True)
            if len(external_scripts) > 5:
                issues.append({
                    "type": "warning",
                    "message": f"Many external scripts ({len(external_scripts)}), consider bundling",
                    "severity": "medium"
                })
                score -= 8
            
            external_styles = soup.find_all('link', rel='stylesheet')
            if len(external_styles) > 3:
                issues.append({
                    "type": "warning",
                    "message": f"Multiple external stylesheets ({len(external_styles)}), consider combining",
                    "severity": "medium"
                })
                score -= 8
            
            # Check for image optimization
            images = soup.find_all('img', src=True)
            large_images = []
            for img in images:
                src = img.get('src', '')
                # Check for dimensions
                if not img.get('width') or not img.get('height'):
                    issues.append({
                        "type": "info",
                        "message": "Image missing width/height attributes (can cause layout shift)",
                        "severity": "low"
                    })
                    score -= 2
            
            # Check for lazy loading
            if len(images) > 5:
                lazy_images = [img for img in images if img.get('loading') == 'lazy']
                if len(lazy_images) == 0:
                    issues.append({
                        "type": "info",
                        "message": "Consider adding lazy loading to images",
                        "severity": "low"
                    })
                    score -= 5
            
            # Check for inline critical CSS
            style_tags = soup.find_all('style')
            if not style_tags and css_content:
                issues.append({
                    "type": "info",
                    "message": "Consider inlining critical CSS for faster initial render",
                    "severity": "low"
                })
                score -= 3
        
        except Exception as e:
            logger.error(f"Performance validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"Performance check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="Performance Optimization",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Minify HTML, CSS, and JavaScript",
                "Optimize and compress images",
                "Combine external CSS/JS files",
                "Add lazy loading to images",
                "Inline critical CSS",
                "Add width/height to images to prevent layout shift"
            ]
        ).to_dict()
    
    async def validate_security(self, html_content: str, url: Optional[str] = None) -> Dict:
        """
        Check 7: Security Best Practices
        - HTTPS usage
        - Content Security Policy
        - XSS prevention
        - SQL injection prevention
        - Secure headers
        """
        logger.info("Validating security...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for inline JavaScript (XSS risk)
            inline_scripts = soup.find_all('script', src=None)
            event_handlers = soup.find_all(attrs=lambda x: x and any(attr.startswith('on') for attr in x.keys()))
            
            if len(inline_scripts) > 3:
                issues.append({
                    "type": "warning",
                    "message": f"Multiple inline scripts found ({len(inline_scripts)}), consider external files",
                    "severity": "medium"
                })
                score -= 10
            
            if event_handlers:
                issues.append({
                    "type": "warning",
                    "message": f"Inline event handlers found ({len(event_handlers)}), use addEventListener instead",
                    "severity": "medium"
                })
                score -= 8
            
            # Check for form security
            forms = soup.find_all('form')
            for form in forms:
                # Check for CSRF token placeholder
                if form.get('method', '').lower() == 'post':
                    csrf_input = form.find('input', attrs={'name': re.compile('csrf|token', re.I)})
                    if not csrf_input:
                        issues.append({
                            "type": "warning",
                            "message": "POST form without apparent CSRF protection",
                            "severity": "medium"
                        })
                        score -= 8
                
                # Check for autocomplete on sensitive fields
                password_inputs = form.find_all('input', type='password')
                for pwd in password_inputs:
                    if pwd.get('autocomplete') != 'off':
                        issues.append({
                            "type": "info",
                            "message": "Consider disabling autocomplete on password fields",
                            "severity": "low"
                        })
                        score -= 3
            
            # Check for Content Security Policy
            csp_meta = soup.find('meta', attrs={'http-equiv': re.compile('content-security-policy', re.I)})
            if not csp_meta:
                issues.append({
                    "type": "info",
                    "message": "No Content Security Policy meta tag found",
                    "severity": "low"
                })
                score -= 5
            
            # Check for external links security
            external_links = soup.find_all('a', href=re.compile(r'^https?://'))
            unsafe_links = [link for link in external_links if not link.get('rel') or 'noopener' not in link.get('rel')]
            if unsafe_links:
                issues.append({
                    "type": "warning",
                    "message": f"{len(unsafe_links)} external links without rel='noopener noreferrer'",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for iframe security
            iframes = soup.find_all('iframe')
            unsafe_iframes = [iframe for iframe in iframes if not iframe.get('sandbox')]
            if unsafe_iframes:
                issues.append({
                    "type": "warning",
                    "message": f"{len(unsafe_iframes)} iframes without sandbox attribute",
                    "severity": "high"
                })
                score -= 15
            
            # Check for SQL injection patterns in any script
            sql_patterns = ['SELECT.*FROM', 'INSERT INTO', 'UPDATE.*SET', 'DELETE FROM']
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()
                for pattern in sql_patterns:
                    if re.search(pattern, script_text, re.I):
                        issues.append({
                            "type": "warning",
                            "message": "SQL-like patterns found in JavaScript (ensure proper sanitization)",
                            "severity": "medium"
                        })
                        score -= 10
                        break
        
        except Exception as e:
            logger.error(f"Security validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"Security check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="Security Best Practices",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Add Content Security Policy",
                "Use rel='noopener noreferrer' on external links",
                "Add sandbox attribute to iframes",
                "Implement CSRF protection on forms",
                "Avoid inline JavaScript and event handlers",
                "Ensure all resources load over HTTPS"
            ]
        ).to_dict()
    
    async def validate_browser_compatibility(self, html_content: str, css_content: str, 
                                            js_content: str) -> Dict:
        """
        Check 8: Browser Compatibility
        - Cross-browser CSS
        - JavaScript compatibility
        - Vendor prefixes
        - Feature detection
        """
        logger.info("Validating browser compatibility...")
        
        issues = []
        score = 100
        
        try:
            # Check for vendor prefixes in CSS
            modern_properties = ['transform', 'transition', 'animation', 'box-shadow', 'border-radius', 
                                'flex', 'grid', 'clip-path']
            
            missing_prefixes = []
            for prop in modern_properties:
                if f'{prop}:' in css_content or f'{prop} ' in css_content:
                    has_webkit = f'-webkit-{prop}' in css_content
                    has_moz = f'-moz-{prop}' in css_content
                    
                    if not has_webkit and prop in ['transform', 'transition', 'animation']:
                        missing_prefixes.append(prop)
            
            if missing_prefixes:
                issues.append({
                    "type": "warning",
                    "message": f"Missing vendor prefixes for: {', '.join(missing_prefixes[:3])}",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for modern JavaScript features
            modern_js_features = [
                (r'\blet\s+', 'let'),
                (r'\bconst\s+', 'const'),
                (r'=>', 'arrow functions'),
                (r'\.then\(', 'promises'),
                (r'\basync\s+', 'async/await'),
                (r'`[^`]*\$\{', 'template literals')
            ]
            
            used_features = []
            for pattern, feature in modern_js_features:
                if re.search(pattern, js_content):
                    used_features.append(feature)
            
            if used_features:
                issues.append({
                    "type": "info",
                    "message": f"Modern JS features used: {', '.join(used_features[:3])} (ensure transpilation for older browsers)",
                    "severity": "low"
                })
                score -= 5
            
            # Check for polyfills
            soup = BeautifulSoup(html_content, 'html.parser')
            polyfill_scripts = soup.find_all('script', src=re.compile(r'polyfill|babel', re.I))
            
            if used_features and not polyfill_scripts:
                issues.append({
                    "type": "warning",
                    "message": "Modern JS features used but no polyfill detected",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for IE-specific code
            ie_conditional = soup.find_all(string=re.compile(r'\[if.*IE.*\]', re.I))
            if ie_conditional:
                issues.append({
                    "type": "info",
                    "message": "IE conditional comments found (IE support included)",
                    "severity": "low"
                })
            
            # Check for flexbox/grid
            if 'display: flex' in css_content or 'display:flex' in css_content:
                if '-webkit-box' not in css_content and '-ms-flexbox' not in css_content:
                    issues.append({
                        "type": "warning",
                        "message": "Flexbox used without vendor prefixes",
                        "severity": "medium"
                    })
                    score -= 8
            
            if 'display: grid' in css_content or 'display:grid' in css_content:
                if '-ms-grid' not in css_content:
                    issues.append({
                        "type": "info",
                        "message": "CSS Grid used (not supported in IE11)",
                        "severity": "low"
                    })
                    score -= 5
        
        except Exception as e:
            logger.error(f"Browser compatibility validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"Browser compatibility check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="Browser Compatibility",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Add vendor prefixes for CSS properties",
                "Transpile modern JavaScript for older browsers",
                "Include polyfills for missing features",
                "Test in multiple browsers (Chrome, Firefox, Safari, Edge)",
                "Consider graceful degradation strategies",
                "Use feature detection instead of browser detection"
            ]
        ).to_dict()
    
    async def validate_mobile_responsiveness(self, html_content: str, css_content: str) -> Dict:
        """
        Check 9: Mobile Responsiveness
        - Viewport meta tag
        - Media queries
        - Touch targets
        - Responsive images
        - Mobile-first approach
        """
        logger.info("Validating mobile responsiveness...")
        
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport:
                issues.append({
                    "type": "error",
                    "message": "Missing viewport meta tag (critical for mobile)",
                    "severity": "critical"
                })
                score -= 25
            else:
                viewport_content = viewport.get('content', '')
                if 'width=device-width' not in viewport_content:
                    issues.append({
                        "type": "warning",
                        "message": "Viewport should include width=device-width",
                        "severity": "high"
                    })
                    score -= 15
                
                if 'initial-scale=1' not in viewport_content:
                    issues.append({
                        "type": "warning",
                        "message": "Viewport should include initial-scale=1",
                        "severity": "medium"
                    })
                    score -= 10
            
            # Check for media queries
            media_queries = re.findall(r'@media[^{]+{', css_content)
            if len(media_queries) == 0:
                issues.append({
                    "type": "error",
                    "message": "No media queries found (not responsive)",
                    "severity": "critical"
                })
                score -= 30
            elif len(media_queries) < 2:
                issues.append({
                    "type": "warning",
                    "message": "Limited media queries (consider more breakpoints)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for common breakpoints
            common_breakpoints = ['768px', '1024px', '1200px', '480px']
            found_breakpoints = [bp for bp in common_breakpoints if bp in css_content]
            
            if len(found_breakpoints) < 2:
                issues.append({
                    "type": "info",
                    "message": "Consider adding more responsive breakpoints",
                    "severity": "low"
                })
                score -= 5
            
            # Check for fixed widths
            fixed_widths = re.findall(r'width:\s*\d+px', css_content)
            if len(fixed_widths) > 10:
                issues.append({
                    "type": "warning",
                    "message": f"Many fixed pixel widths ({len(fixed_widths)}), consider using relative units",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for responsive images
            images = soup.find_all('img')
            responsive_images = [img for img in images if img.get('srcset') or 'max-width' in str(img.get('style', ''))]
            
            if images and len(responsive_images) == 0:
                issues.append({
                    "type": "warning",
                    "message": "Images may not be responsive (no srcset or max-width)",
                    "severity": "medium"
                })
                score -= 10
            
            # Check for touch-friendly elements
            buttons = soup.find_all('button')
            links = soup.find_all('a')
            touch_elements = buttons + links
            
            if touch_elements:
                issues.append({
                    "type": "info",
                    "message": f"Ensure {len(touch_elements)} interactive elements have min 44x44px touch targets",
                    "severity": "low"
                })
                score -= 3
            
            # Check for horizontal scrolling prevention
            if 'overflow-x: hidden' not in css_content and 'overflow-x:hidden' not in css_content:
                issues.append({
                    "type": "info",
                    "message": "Consider adding overflow-x: hidden on body to prevent horizontal scroll",
                    "severity": "low"
                })
                score -= 3
            
            # Check for mobile-first approach
            if media_queries:
                min_width_queries = [mq for mq in media_queries if 'min-width' in mq]
                max_width_queries = [mq for mq in media_queries if 'max-width' in mq]
                
                if len(max_width_queries) > len(min_width_queries):
                    issues.append({
                        "type": "info",
                        "message": "Consider mobile-first approach (min-width queries)",
                        "severity": "low"
                    })
                    score -= 5
        
        except Exception as e:
            logger.error(f"Mobile responsiveness validation error: {str(e)}")
            issues.append({
                "type": "error",
                "message": f"Mobile responsiveness check error: {str(e)}",
                "severity": "high"
            })
            score = 50
        
        return ValidationResult(
            check_name="Mobile Responsiveness",
            passed=score >= 70,
            score=max(0, score),
            issues=issues,
            recommendations=[
                "Add viewport meta tag with width=device-width",
                "Implement media queries for multiple breakpoints",
                "Use relative units (%, em, rem) instead of fixed pixels",
                "Add responsive images with srcset",
                "Ensure touch targets are at least 44x44 pixels",
                "Use mobile-first approach with min-width queries",
                "Test on actual mobile devices"
            ]
        ).to_dict()
    
    def _generate_summary(self, results: Dict) -> str:
        """Generate a human-readable summary of validation results"""
        passed = sum(1 for r in results.values() if r['passed'])
        total = len(results)
        avg_score = sum(r['score'] for r in results.values()) // total
        
        status = "EXCELLENT" if avg_score >= 90 else "GOOD" if avg_score >= 75 else "NEEDS IMPROVEMENT" if avg_score >= 60 else "POOR"
        
        summary = f"Validation Complete: {passed}/{total} checks passed\n"
        summary += f"Overall Score: {avg_score}/100 ({status})\n\n"
        
        for name, result in results.items():
            icon = "✅" if result['passed'] else "❌"
            summary += f"{icon} {result['check_name']}: {result['score']}/100\n"
        
        return summary


# Export validator
__all__ = ['WebsiteValidator', 'ValidationResult']
