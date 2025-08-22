#!/usr/bin/env python3
"""
Database migration script to add chinese_brand_id field to Brand model
This handles the case where the database is on render.com or any remote location
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from database import get_db, engine
from models import Brand

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False

def add_chinese_brand_id_column():
    """Add chinese_brand_id column to brands table if it doesn't exist"""
    try:
        # Check if column already exists
        if check_column_exists('brands', 'chinese_brand_id'):
            print("✅ chinese_brand_id column already exists in brands table")
            return True
        
        print("🔄 Adding chinese_brand_id column to brands table...")
        
        # Add the column using raw SQL
        with engine.connect() as connection:
            connection.execute(text(
                "ALTER TABLE brands ADD COLUMN chinese_brand_id VARCHAR(100)"
            ))
            connection.commit()
        
        print("✅ Successfully added chinese_brand_id column to brands table")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add chinese_brand_id column: {e}")
        return False

def update_existing_brands_with_known_mappings():
    """Update existing brands with known Chinese brand IDs"""
    try:
        db = next(get_db())
        
        # Known mappings from api_test_results.json
        known_mappings = {
            "Apple": "BR20250111000002",
            "SAMSUNG": "BR020250120000001", 
            "HUAWEI": "BR102504010001",
            "VIVO": "BR102504020002",
            "HONOR": "BR102504070001",
            "Xiaomi": "BR20250111000001",
            "Redmi": "BR102504060001",
            "OPPO": "BR102504020001"
        }
        
        updated_count = 0
        for brand_name, chinese_id in known_mappings.items():
            brand = db.query(Brand).filter(Brand.name == brand_name).first()
            if brand and not brand.chinese_brand_id:
                brand.chinese_brand_id = chinese_id
                updated_count += 1
                print(f"✅ Updated {brand_name} with Chinese ID: {chinese_id}")
        
        db.commit()
        print(f"✅ Updated {updated_count} brands with Chinese IDs")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update brands with Chinese IDs: {e}")
        return False

def main():
    """Run the migration"""
    print("🚀 Starting database migration...")
    print(f"Database URL: {engine.url}")
    
    # Step 1: Add the column
    if not add_chinese_brand_id_column():
        print("❌ Migration failed at step 1")
        return False
    
    # Step 2: Update existing brands
    if not update_existing_brands_with_known_mappings():
        print("⚠️ Migration completed but brand updates failed")
        return True  # Column was added successfully
    
    print("🎉 Migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)