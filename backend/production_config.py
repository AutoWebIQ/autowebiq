"""
Production Configuration for AutoWebIQ
Security, performance, and production settings
"""
import os
from typing import List

class ProductionConfig:
    """Production environment configuration"""
    
    # Environment
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Domain Configuration
    DOMAIN = os.environ.get('DOMAIN', 'autowebiq.com')
    FRONTEND_URL = f"https://{DOMAIN}"
    API_URL = f"https://api.{DOMAIN}"
    
    # Security
    JWT_SECRET = os.environ.get('JWT_SECRET')
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # CORS
    CORS_ORIGINS = [
        f"https://{DOMAIN}",
        f"https://www.{DOMAIN}",
        f"https://api.{DOMAIN}"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # Database
    MONGO_URL = os.environ.get('MONGO_URL')
    DB_NAME = os.environ.get('DB_NAME', 'autowebiq_production')
    
    # Caching
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Performance
    MAX_WORKERS = 4
    WORKER_TIMEOUT = 300  # 5 minutes
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # File Upload
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    
    # API Configuration
    API_PREFIX = "/api"
    API_VERSION = "v1"
    
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        errors = []
        
        if not cls.JWT_SECRET:
            errors.append("JWT_SECRET not set")
        
        if not cls.MONGO_URL:
            errors.append("MONGO_URL not set")
        
        if cls.DEBUG:
            errors.append("DEBUG mode enabled in production")
        
        if errors:
            raise ValueError(f"Production config errors: {', '.join(errors)}")
        
        return True

# Validate on import
ProductionConfig.validate()
