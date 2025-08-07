"""Payment service for handling Stripe payments"""

import stripe
from backend.config.settings import STRIPE_SECRET_KEY

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

def initialize_stripe():
    """Initialize Stripe configuration"""
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe