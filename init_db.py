"""Initialize database with sample data"""

import sys
import os
from database import engine, create_tables, SessionLocal
from models import *
from sqlalchemy.exc import IntegrityError

def init_brands():
    """Initialize phone brands"""
    db = SessionLocal()
    try:
        brands_data = [
            {
                "id": "iphone",
                "name": "iPhone",
                "display_name": "IPHONE",
                "frame_color": "#007AFF",
                "button_color": "#007AFF",
                "is_available": True,
                "display_order": 1,
                "subtitle": "The most popular choice"
            },
            {
                "id": "samsung",
                "name": "Samsung",
                "display_name": "SAMSUNG",
                "frame_color": "#1D72AA",
                "button_color": "#1D72AA",
                "is_available": True,
                "display_order": 2,
                "subtitle": "Galaxy series"
            },
            {
                "id": "google",
                "name": "Google",
                "display_name": "GOOGLE",
                "frame_color": "#4285F4",
                "button_color": "#4285F4",
                "is_available": False,
                "display_order": 3,
                "subtitle": "Coming soon!"
            }
        ]

        for brand_data in brands_data:
            existing = db.query(Brand).filter(Brand.id == brand_data["id"]).first()
            if not existing:
                brand = Brand(**brand_data)
                db.add(brand)
        
        db.commit()
        print("✅ Brands initialized")
    except Exception as e:
        print(f"❌ Error initializing brands: {e}")
        db.rollback()
    finally:
        db.close()

def init_phone_models():
    """Initialize phone models"""
    db = SessionLocal()
    try:
        iphone_models = [
            {"name": "iPhone 16 Pro Max", "display_order": 1},
            {"name": "iPhone 16 Pro", "display_order": 2},
            {"name": "iPhone 16 Plus", "display_order": 3},
            {"name": "iPhone 16", "display_order": 4},
            {"name": "iPhone 15 Pro Max", "display_order": 5},
            {"name": "iPhone 15 Pro", "display_order": 6},
            {"name": "iPhone 15 Plus", "display_order": 7},
            {"name": "iPhone 15", "display_order": 8},
            {"name": "iPhone 14 Pro Max", "display_order": 9},
            {"name": "iPhone 14 Pro", "display_order": 10},
            {"name": "iPhone 14 Plus", "display_order": 11},
            {"name": "iPhone 14", "display_order": 12},
            {"name": "iPhone 13 Pro Max", "display_order": 13},
            {"name": "iPhone 13 Pro", "display_order": 14},
            {"name": "iPhone 13", "display_order": 15},
            {"name": "iPhone 13 mini", "display_order": 16},
            {"name": "iPhone 12 Pro Max", "display_order": 17},
            {"name": "iPhone 12 Pro", "display_order": 18},
            {"name": "iPhone 12", "display_order": 19},
            {"name": "iPhone 12 mini", "display_order": 20},
        ]

        samsung_models = [
            {"name": "Galaxy S24 Ultra", "display_order": 1},
            {"name": "Galaxy S24 Plus", "display_order": 2},
            {"name": "Galaxy S24", "display_order": 3},
            {"name": "Galaxy S23 Ultra", "display_order": 4},
            {"name": "Galaxy S23 Plus", "display_order": 5},
            {"name": "Galaxy S23", "display_order": 6},
            {"name": "Galaxy S22 Ultra", "display_order": 7},
            {"name": "Galaxy S22 Plus", "display_order": 8},
            {"name": "Galaxy S22", "display_order": 9},
            {"name": "Galaxy S21 Ultra", "display_order": 10},
            {"name": "Galaxy S21 Plus", "display_order": 11},
            {"name": "Galaxy S21", "display_order": 12},
            {"name": "Galaxy Z Fold 6", "display_order": 13},
            {"name": "Galaxy Z Fold 5", "display_order": 14},
            {"name": "Galaxy Z Fold 4", "display_order": 15},
            {"name": "Galaxy Z Flip 6", "display_order": 16},
            {"name": "Galaxy Z Flip 5", "display_order": 17},
            {"name": "Galaxy Z Flip 4", "display_order": 18},
            {"name": "Galaxy A55", "display_order": 19},
            {"name": "Galaxy A35", "display_order": 20},
            {"name": "Galaxy A25", "display_order": 21},
        ]

        google_models = [
            {"name": "Pixel 9 Pro XL", "display_order": 1},
            {"name": "Pixel 9 Pro", "display_order": 2},
            {"name": "Pixel 9", "display_order": 3},
            {"name": "Pixel 8 Pro", "display_order": 4},
            {"name": "Pixel 8", "display_order": 5},
            {"name": "Pixel 8a", "display_order": 6},
            {"name": "Pixel 7 Pro", "display_order": 7},
            {"name": "Pixel 7", "display_order": 8},
            {"name": "Pixel 7a", "display_order": 9},
            {"name": "Pixel 6 Pro", "display_order": 10},
            {"name": "Pixel 6", "display_order": 11},
            {"name": "Pixel 6a", "display_order": 12},
            {"name": "Pixel 5", "display_order": 13},
            {"name": "Pixel 5a", "display_order": 14},
            {"name": "Pixel 4 XL", "display_order": 15},
            {"name": "Pixel 4", "display_order": 16},
            {"name": "Pixel 4a", "display_order": 17},
        ]

        all_models = [
            ("iphone", iphone_models),
            ("samsung", samsung_models),
            ("google", google_models)
        ]

        for brand_id, models in all_models:
            for model_data in models:
                model_id = f"{brand_id}-{model_data['name'].lower().replace(' ', '-')}"
                existing = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
                if not existing:
                    phone_model = PhoneModel(
                        id=model_id,
                        brand_id=brand_id,
                        name=model_data["name"],
                        display_name=model_data["name"],
                        price=19.99,
                        stock=100,
                        is_available=True,
                        display_order=model_data["display_order"],
                        release_year=2024
                    )
                    db.add(phone_model)

        db.commit()
        print("✅ Phone models initialized")
    except Exception as e:
        print(f"❌ Error initializing phone models: {e}")
        db.rollback()
    finally:
        db.close()

def init_templates():
    """Initialize templates"""
    db = SessionLocal()
    try:
        templates_data = [
            # Basic Templates
            {
                "id": "classic",
                "name": "Classic",
                "description": "Single photo classic design",
                "price": 19.99,
                "category": "basic",
                "image_count": 1,
                "features": ["Single photo", "Simple layout", "High quality print"],
                "display_price": "£19.99",
                "display_order": 1
            },
            {
                "id": "2-in-1",
                "name": "2-in-1",
                "description": "Two photos side by side",
                "price": 19.99,
                "category": "basic",
                "image_count": 2,
                "features": ["Two photos", "Side-by-side layout", "Perfect for couples"],
                "display_price": "£19.99",
                "display_order": 2
            },
            {
                "id": "3-in-1",
                "name": "3-in-1",
                "description": "Three photos in creative layout",
                "price": 19.99,
                "category": "basic",
                "image_count": 3,
                "features": ["Three photos", "Creative layout", "Perfect for groups"],
                "display_price": "£19.99",
                "display_order": 3
            },
            {
                "id": "4-in-1",
                "name": "4-in-1",
                "description": "Four photos in grid layout",
                "price": 19.99,
                "category": "basic",
                "image_count": 4,
                "features": ["Four photos", "Grid layout", "Maximum memories"],
                "display_price": "£19.99",
                "display_order": 4
            },
            {
                "id": "film-strip-3",
                "name": "Film Strip",
                "description": "Vintage film strip style",
                "price": 19.99,
                "category": "film",
                "image_count": 3,
                "features": ["Film strip style", "Vintage aesthetic", "Three photo sequence"],
                "display_price": "£19.99",
                "display_order": 5
            },
            # AI Templates
            {
                "id": "funny-toon",
                "name": "Funny Toon",
                "description": "Transform into cartoon character",
                "price": 21.99,
                "category": "ai",
                "image_count": 1,
                "features": ["AI cartoon transformation", "Multiple styles", "Funny and unique"],
                "display_price": "£21.99",
                "display_order": 6
            },
            {
                "id": "retro-remix",
                "name": "Retro Remix",
                "description": "Vintage retro effects",
                "price": 21.99,
                "category": "ai",
                "image_count": 1,
                "features": ["Retro styling", "Vintage effects", "Nostalgic feel"],
                "display_price": "£21.99",
                "display_order": 7
            },
            {
                "id": "cover-shoot",
                "name": "Cover Shoot",
                "description": "Professional magazine cover style",
                "price": 21.99,
                "category": "ai",
                "image_count": 1,
                "features": ["Magazine quality", "Professional styling", "Glamorous effects"],
                "display_price": "£21.99",
                "display_order": 8
            },
            {
                "id": "glitch-pro",
                "name": "Glitch Pro",
                "description": "Digital glitch effects",
                "price": 21.99,
                "category": "ai",
                "image_count": 1,
                "features": ["Digital glitch effects", "Cyberpunk style", "Modern aesthetic"],
                "display_price": "£21.99",
                "display_order": 9
            },
        ]

        for template_data in templates_data:
            existing = db.query(Template).filter(Template.id == template_data["id"]).first()
            if not existing:
                template = Template(**template_data)
                db.add(template)

        db.commit()
        print("✅ Templates initialized")
    except Exception as e:
        print(f"❌ Error initializing templates: {e}")
        db.rollback()
    finally:
        db.close()

def init_fonts():
    """Initialize fonts"""
    db = SessionLocal()
    try:
        fonts_data = [
            {"name": "Arial", "css_style": "Arial, sans-serif", "display_order": 1},
            {"name": "Inter", "css_style": "Inter, sans-serif", "is_google_font": True, "display_order": 2},
            {"name": "Georgia", "css_style": "Georgia, serif", "display_order": 3},
            {"name": "Helvetica", "css_style": "Helvetica, Arial, sans-serif", "display_order": 4},
            {"name": "Roboto", "css_style": "Roboto, sans-serif", "is_google_font": True, "display_order": 5},
            {"name": "Open Sans", "css_style": "Open Sans, sans-serif", "is_google_font": True, "display_order": 6},
            {"name": "Montserrat", "css_style": "Montserrat, sans-serif", "is_google_font": True, "display_order": 7},
            {"name": "Lato", "css_style": "Lato, sans-serif", "is_google_font": True, "display_order": 8},
            {"name": "Oswald", "css_style": "Oswald, sans-serif", "is_google_font": True, "display_order": 9},
            {"name": "Source Sans Pro", "css_style": "Source Sans Pro, sans-serif", "is_google_font": True, "display_order": 10},
            {"name": "Raleway", "css_style": "Raleway, sans-serif", "is_google_font": True, "display_order": 11},
            {"name": "PT Sans", "css_style": "PT Sans, sans-serif", "is_google_font": True, "display_order": 12},
            {"name": "Ubuntu", "css_style": "Ubuntu, sans-serif", "is_google_font": True, "display_order": 13},
            {"name": "Nunito", "css_style": "Nunito, sans-serif", "is_google_font": True, "display_order": 14},
            {"name": "Poppins", "css_style": "Poppins, sans-serif", "is_google_font": True, "display_order": 15},
            {"name": "Merriweather", "css_style": "Merriweather, serif", "is_google_font": True, "display_order": 16},
        ]

        for font_data in fonts_data:
            existing = db.query(Font).filter(Font.name == font_data["name"]).first()
            if not existing:
                font = Font(**font_data)
                db.add(font)

        db.commit()
        print("✅ Fonts initialized")
    except Exception as e:
        print(f"❌ Error initializing fonts: {e}")
        db.rollback()
    finally:
        db.close()

def init_colors():
    """Initialize colors"""
    db = SessionLocal()
    try:
        background_colors = [
            {"name": "White", "hex_value": "#FFFFFF", "css_classes": {"bg": "bg-white", "border": "border-gray-300"}},
            {"name": "Light Gray", "hex_value": "#F3F4F6", "css_classes": {"bg": "bg-gray-100", "border": "border-gray-300"}},
            {"name": "Dark Gray", "hex_value": "#6B7280", "css_classes": {"bg": "bg-gray-500", "border": "border-gray-600"}},
            {"name": "Black", "hex_value": "#000000", "css_classes": {"bg": "bg-black", "border": "border-gray-800"}},
            {"name": "Red", "hex_value": "#EF4444", "css_classes": {"bg": "bg-red-500", "border": "border-red-600"}},
            {"name": "Orange", "hex_value": "#F97316", "css_classes": {"bg": "bg-orange-500", "border": "border-orange-600"}},
            {"name": "Yellow", "hex_value": "#EAB308", "css_classes": {"bg": "bg-yellow-500", "border": "border-yellow-600"}},
            {"name": "Green", "hex_value": "#22C55E", "css_classes": {"bg": "bg-green-500", "border": "border-green-600"}},
            {"name": "Blue", "hex_value": "#3B82F6", "css_classes": {"bg": "bg-blue-500", "border": "border-blue-600"}},
            {"name": "Purple", "hex_value": "#A855F7", "css_classes": {"bg": "bg-purple-500", "border": "border-purple-600"}},
            {"name": "Pink", "hex_value": "#EC4899", "css_classes": {"bg": "bg-pink-500", "border": "border-pink-600"}},
            {"name": "Indigo", "hex_value": "#6366F1", "css_classes": {"bg": "bg-indigo-500", "border": "border-indigo-600"}},
        ]

        text_colors = [
            {"name": "Black", "hex_value": "#000000", "css_classes": {"text": "text-black"}},
            {"name": "White", "hex_value": "#FFFFFF", "css_classes": {"text": "text-white"}},
            {"name": "Gray", "hex_value": "#6B7280", "css_classes": {"text": "text-gray-500"}},
            {"name": "Red", "hex_value": "#DC2626", "css_classes": {"text": "text-red-600"}},
            {"name": "Orange", "hex_value": "#EA580C", "css_classes": {"text": "text-orange-600"}},
            {"name": "Yellow", "hex_value": "#CA8A04", "css_classes": {"text": "text-yellow-600"}},
            {"name": "Green", "hex_value": "#16A34A", "css_classes": {"text": "text-green-600"}},
            {"name": "Blue", "hex_value": "#2563EB", "css_classes": {"text": "text-blue-600"}},
            {"name": "Purple", "hex_value": "#9333EA", "css_classes": {"text": "text-purple-600"}},
            {"name": "Pink", "hex_value": "#DB2777", "css_classes": {"text": "text-pink-600"}},
            {"name": "Indigo", "hex_value": "#4F46E5", "css_classes": {"text": "text-indigo-600"}},
        ]

        for i, color_data in enumerate(background_colors):
            existing = db.query(Color).filter(
                Color.name == color_data["name"], 
                Color.color_type == "background"
            ).first()
            if not existing:
                color = Color(
                    name=color_data["name"],
                    hex_value=color_data["hex_value"],
                    css_classes=color_data["css_classes"],
                    color_type="background",
                    display_order=i + 1
                )
                db.add(color)

        for i, color_data in enumerate(text_colors):
            existing = db.query(Color).filter(
                Color.name == color_data["name"], 
                Color.color_type == "text"
            ).first()
            if not existing:
                color = Color(
                    name=color_data["name"],
                    hex_value=color_data["hex_value"],
                    css_classes=color_data["css_classes"],
                    color_type="text",
                    display_order=i + 1
                )
                db.add(color)

        db.commit()
        print("✅ Colors initialized")
    except Exception as e:
        print(f"❌ Error initializing colors: {e}")
        db.rollback()
    finally:
        db.close()


def init_vending_machines():
    """Initialize test vending machines for Chinese manufacturers"""
    db = SessionLocal()
    try:
        vending_machines_data = [
            {
                "id": "VM001",
                "name": "Test Mall Kiosk 1",
                "location": "Westfield Shopping Centre - Level 2",
                "qr_config": {
                    "base_url": "https://pimpmycase.shop",
                    "session_timeout_minutes": 30,
                    "max_concurrent_sessions": 5,
                    "chinese_device_id": "TEST_DEVICE_001"
                },
                "is_active": True
            },
            {
                "id": "VM002", 
                "name": "Test Mall Kiosk 2",
                "location": "Stratford Shopping Centre - Ground Floor",
                "qr_config": {
                    "base_url": "https://pimpmycase.shop",
                    "session_timeout_minutes": 30,
                    "max_concurrent_sessions": 5,
                    "chinese_device_id": "TEST_DEVICE_002"
                },
                "is_active": True
            },
            {
                "id": "VM_LONDON_01",
                "name": "London Oxford Street Station",
                "location": "Oxford Street Underground Station - Platform Level",
                "qr_config": {
                    "base_url": "https://pimpmycase.shop",
                    "session_timeout_minutes": 25,
                    "max_concurrent_sessions": 10,
                    "chinese_device_id": "LONDON_DEVICE_001"
                },
                "is_active": True
            },
            {
                "id": "VM_TEST_MANUFACTURER",
                "name": "Chinese Manufacturer Test Unit",
                "location": "API Testing Environment",
                "qr_config": {
                    "base_url": "https://pimpmycase.shop",
                    "session_timeout_minutes": 60,
                    "max_concurrent_sessions": 3,
                    "chinese_device_id": "MANUFACTURER_TEST_001"
                },
                "is_active": True
            },
            {
                "id": "VM_DEMO",
                "name": "Demo Presentation Machine",
                "location": "Sales Demo Environment",
                "qr_config": {
                    "base_url": "https://pimpmycase.shop",
                    "session_timeout_minutes": 15,
                    "max_concurrent_sessions": 2,
                    "chinese_device_id": "DEMO_DEVICE_001"
                },
                "is_active": True
            }
        ]

        for machine_data in vending_machines_data:
            existing = db.query(VendingMachine).filter(VendingMachine.id == machine_data["id"]).first()
            if not existing:
                machine = VendingMachine(**machine_data)
                db.add(machine)

        db.commit()
        print("✅ Test vending machines initialized (5 machines)")
    except Exception as e:
        print(f"❌ Error initializing vending machines: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Initialize the entire database"""
    print("🚀 Initializing database...")
    
    # Create all tables
    print("📊 Creating database tables...")
    create_tables()
    print("✅ Database tables created")
    
    # Initialize data
    init_brands()
    init_phone_models()
    init_templates()
    init_fonts()
    init_colors()
    init_vending_machines()
    
    print("🎉 Database initialization complete!")

if __name__ == "__main__":
    main()