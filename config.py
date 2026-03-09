import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for Financial Intelligence API"""
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://default:5FNkXvCnviJ52rk8c2KDGDqGqUYmx16B@redis-15283.c264.ap-south-1-1.ec2.cloud.redislabs.com:15283")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/banking_db")
    
    # Backend API
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3000")
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "Financial Expense Intelligence API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Production detection
    @property
    def is_production(self):
        return "redis-15283" in self.REDIS_URL
    
    @property
    def is_development(self):
        return not self.is_production
