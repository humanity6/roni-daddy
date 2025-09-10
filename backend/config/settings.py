"""Application settings and configuration"""

import os
from dotenv import load_dotenv

# Load environment variables - check multiple locations
load_dotenv()  # Current directory
load_dotenv("image gen/.env")  # Image gen subdirectory
load_dotenv(".env")  # Explicit current directory

# API Configuration
API_TITLE = "PimpMyCase API - Database Edition"
API_VERSION = "2.0.0"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required for production")

# Database Configuration (imported from existing database.py)
DATABASE_URL = os.getenv("DATABASE_URL")

# Chinese API Configuration
CHINESE_API_BASE_URL = os.getenv('CHINESE_API_BASE_URL', 'https://api.inkele.net/mobileShell/en')
CHINESE_API_ACCOUNT = os.getenv('CHINESE_API_ACCOUNT', 'taharizvi.ai@gmail.com')
CHINESE_API_PASSWORD = os.getenv('CHINESE_API_PASSWORD', 'EN112233')
CHINESE_API_SYSTEM_NAME = os.getenv('CHINESE_API_SYSTEM_NAME', 'mobileShell')
CHINESE_API_FIXED_KEY = os.getenv('CHINESE_API_FIXED_KEY', 'shfoa3sfwoehnf3290rqefiz4efd')
CHINESE_API_DEVICE_ID = os.getenv('CHINESE_API_DEVICE_ID', '1CBRONIQRWQQ')
CHINESE_API_TIMEOUT = int(os.getenv('CHINESE_API_TIMEOUT', '30'))

# File Storage Configuration
GENERATED_IMAGES_DIR = "generated-images"
UK_HOSTED_BASE_URL = "https://pimpmycase.onrender.com"  # UK-hosted Render deployment

# Image Processing Configuration
MAX_IMAGE_DIMENSION = 1024
DEFAULT_IMAGE_QUALITY = "low"
DEFAULT_IMAGE_SIZE = "1024x1536"

# Security Configuration
DEFAULT_SESSION_TIMEOUT_MINUTES = 30
MAX_PAYMENT_AMOUNT = 10000  # Maximum £10,000 for safety
DEFAULT_TOKEN_EXPIRY_HOURS = 24