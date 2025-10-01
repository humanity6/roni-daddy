"""SQLAlchemy models for the phone case customization platform"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class Brand(Base):
    """Phone brands (iPhone, Samsung, Google, etc.)"""
    __tablename__ = "brands"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # "iPhone"
    display_name = Column(String(100), nullable=False)  # "IPHONE"
    chinese_brand_id = Column(String(100))  # Chinese manufacturer's brand ID (e.g., BR20250111000002)
    frame_color = Column(String(50), default="#007AFF")  # UI frame color
    button_color = Column(String(50), default="#007AFF")  # UI button color
    is_available = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    subtitle = Column(String(200))  # Optional subtitle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    models = relationship("PhoneModel", back_populates="brand", cascade="all, delete-orphan")

class PhoneModel(Base):
    """Individual phone models within each brand"""
    __tablename__ = "phone_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    name = Column(String(200), nullable=False)  # "iPhone 15 Pro Max"
    display_name = Column(String(200), nullable=False)  # Display version
    chinese_model_id = Column(String(100))  # Chinese manufacturer's internal model ID
    mobile_shell_id = Column(String(100))  # Chinese API mobile shell ID for orderData calls (CRITICAL FIX)
    price = Column(DECIMAL(10, 2), nullable=False, default=19.99)
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    release_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="models")
    orders = relationship("Order", back_populates="phone_model")

class Template(Base):
    """AI and basic templates for phone case designs"""
    __tablename__ = "templates"

    id = Column(String, primary_key=True)  # 'funny-toon', 'retro-remix', etc.
    name = Column(String(100), nullable=False)  # "Funny Toon"
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False, default=19.99)
    currency = Column(String(3), default="GBP")
    category = Column(String(50), nullable=False)  # 'basic', 'ai', 'film'
    image_count = Column(Integer, default=1)  # Number of images required
    features = Column(JSON)  # Array of feature descriptions
    preview_image_path = Column(String(500))  # Path to preview image
    display_price = Column(String(20))  # "£19.99"
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="template")
    ai_styles = relationship("AIStyle", back_populates="template", cascade="all, delete-orphan")

class Font(Base):
    """Available fonts for text customization"""
    __tablename__ = "fonts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # "Arial"
    css_style = Column(String(200))  # CSS font-family value
    font_weight = Column(String(20), default="400")
    is_google_font = Column(Boolean, default=False)
    google_font_url = Column(String(500))  # Google Fonts import URL
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Color(Base):
    """Available colors for backgrounds and text"""
    __tablename__ = "colors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # "Deep Blue"
    hex_value = Column(String(7), nullable=False)  # "#1E40AF"
    css_classes = Column(JSON)  # {"bg": "bg-blue-700", "border": "border-blue-700"}
    color_type = Column(String(20), nullable=False)  # 'background' or 'text'
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AIStyle(Base):
    """AI generation styles for templates"""
    __tablename__ = "ai_styles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String, ForeignKey("templates.id"), nullable=False)
    style_name = Column(String(100), nullable=False)  # "Wild and Wacky"
    description = Column(Text)  # Detailed style description/prompt
    prompt_keywords = Column(JSON)  # Additional keywords for AI generation
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("Template", back_populates="ai_styles")

class VendingMachine(Base):
    """Vending machine configurations"""
    __tablename__ = "vending_machines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # "Machine 1"
    location = Column(String(200))  # "Mall of America - Level 2"
    qr_config = Column(JSON)  # QR code generation settings
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="vending_machine")
    sessions = relationship("VendingMachineSession", back_populates="vending_machine", cascade="all, delete-orphan")

class VendingMachineSession(Base):
    """Active sessions between vending machines and user web sessions"""
    __tablename__ = "vending_machine_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(200), unique=True, nullable=False)  # Format: VM001_20240123_143022_ABC123
    machine_id = Column(String, ForeignKey("vending_machines.id"), nullable=False)
    
    # Session state
    status = Column(String(50), default="active")  # active, designing, payment_pending, payment_completed, expired, cancelled
    user_progress = Column(String(50), default="started")  # started, brand_selected, design_complete, payment_reached
    
    # QR and session data
    qr_data = Column(JSON)  # Original QR parameters
    user_agent = Column(String(500))  # Browser/device info
    ip_address = Column(String(45))  # IPv4/IPv6 address
    
    # Order association
    order_id = Column(String, ForeignKey("orders.id"))  # Links to created order
    
    # Payment details
    payment_method = Column(String(50))  # 'app', 'vending_machine', None
    payment_amount = Column(DECIMAL(10, 2))  # Final order amount
    payment_confirmed_at = Column(DateTime(timezone=True))
    
    # Timing
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Session expiration
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional session metadata
    session_data = Column(JSON)  # Store user selections, progress, etc.
    error_log = Column(JSON)  # Track any errors during session
    
    # Relationships
    vending_machine = relationship("VendingMachine", back_populates="sessions")
    order = relationship("Order")

class Order(Base):
    """Customer orders"""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100))  # QR session ID or web session
    
    # User data
    user_data = Column(JSON)  # Store any user preferences/data
    
    # Product selection
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    model_id = Column(String, ForeignKey("phone_models.id"), nullable=False)
    template_id = Column(String, ForeignKey("templates.id"), nullable=False)
    
    # Order details
    status = Column(String(50), default="created")  # created, paid, generating, sent_to_chinese, printing, completed, failed
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="GBP")
    
    # Payment info
    stripe_session_id = Column(String(200))
    stripe_payment_intent_id = Column(String(200))
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    paid_at = Column(DateTime(timezone=True))
    queue_number = Column(String(50))  # Queue number for vending machine display
    
    # Chinese payment tracking
    third_party_payment_id = Column(String(200))  # Chinese third_id from payStatus API
    chinese_payment_id = Column(String(200))  # Chinese payment transaction ID
    chinese_payment_status = Column(Integer, default=1)  # 1=waiting, 2=paying, 3=paid, 4=failed, 5=abnormal
    chinese_order_id = Column(String(200))  # Chinese manufacturer's order ID
    estimated_completion = Column(DateTime(timezone=True))  # Manufacturing completion estimate
    notes = Column(Text)  # Additional notes from Chinese manufacturer
    
    # Machine info
    machine_id = Column(String, ForeignKey("vending_machines.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    brand = relationship("Brand")
    phone_model = relationship("PhoneModel", back_populates="orders")
    template = relationship("Template", back_populates="orders")
    vending_machine = relationship("VendingMachine", back_populates="orders")
    images = relationship("OrderImage", back_populates="order", cascade="all, delete-orphan")

class OrderImage(Base):
    """Generated images for orders"""
    __tablename__ = "order_images"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    image_path = Column(String(500), nullable=False)  # Path to stored image
    image_type = Column(String(50), default="generated")  # generated, uploaded, final
    ai_params = Column(JSON)  # AI generation parameters used
    chinese_image_url = Column(String(500))  # Download URL for Chinese partners
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="images")

class PaymentMapping(Base):
    """Persistent mapping between frontend payment IDs (PYEN...) and Chinese payment IDs (MSPY...)"""
    __tablename__ = "payment_mappings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    third_id = Column(String(100), unique=True, nullable=False)  # Frontend payment ID (PYEN250822067351)
    chinese_payment_id = Column(String(100), nullable=False)  # Chinese API payment ID (MSPY10250822000041)
    device_id = Column(String(100))  # Device that initiated the payment
    mobile_model_id = Column(String(100))  # Phone model for the payment
    pay_amount = Column(DECIMAL(10, 2))  # Payment amount
    pay_type = Column(Integer)  # Payment type (5=vending, 12=app, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminUser(Base):
    """Admin users for the dashboard"""
    __tablename__ = "admin_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), default="admin")  # admin, super_admin, viewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())