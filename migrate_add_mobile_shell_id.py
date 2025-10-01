#!/usr/bin/env python3
"""
Database migration script to add mobile_shell_id field to PhoneModel model
This handles the case where the database is on render.com or any remote location
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from database import get_db, engine
from models import PhoneModel

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False

def add_mobile_shell_id_column():
    """Add mobile_shell_id column to phone_models table if it doesn't exist"""
    try:
        # Check if column already exists
        if check_column_exists('phone_models', 'mobile_shell_id'):
            print("✅ mobile_shell_id column already exists in phone_models table")
            return True

        print("🔄 Adding mobile_shell_id column to phone_models table...")

        # Add the column using raw SQL
        with engine.connect() as connection:
            connection.execute(text(
                "ALTER TABLE phone_models ADD COLUMN mobile_shell_id VARCHAR(100)"
            ))
            connection.commit()

        print("✅ Successfully added mobile_shell_id column to phone_models table")
        return True

    except Exception as e:
        print(f"❌ Failed to add mobile_shell_id column: {e}")
        return False

def add_index_on_mobile_shell_id():
    """Add index on mobile_shell_id column for faster lookups"""
    try:
        print("🔄 Adding index on mobile_shell_id column...")

        with engine.connect() as connection:
            # Check if index already exists
            result = connection.execute(text(
                "SELECT indexname FROM pg_indexes WHERE tablename = 'phone_models' AND indexname = 'idx_phone_models_mobile_shell_id'"
            ))
            if result.fetchone():
                print("✅ Index idx_phone_models_mobile_shell_id already exists")
                return True

            # Create the index
            connection.execute(text(
                "CREATE INDEX idx_phone_models_mobile_shell_id ON phone_models(mobile_shell_id)"
            ))
            connection.commit()

        print("✅ Successfully added index on mobile_shell_id column")
        return True

    except Exception as e:
        print(f"❌ Failed to add index on mobile_shell_id: {e}")
        return False

def add_index_on_chinese_model_id():
    """Add index on chinese_model_id column for faster lookups (if not exists)"""
    try:
        print("🔄 Adding index on chinese_model_id column...")

        with engine.connect() as connection:
            # Check if index already exists
            result = connection.execute(text(
                "SELECT indexname FROM pg_indexes WHERE tablename = 'phone_models' AND indexname = 'idx_phone_models_chinese_model_id'"
            ))
            if result.fetchone():
                print("✅ Index idx_phone_models_chinese_model_id already exists")
                return True

            # Create the index
            connection.execute(text(
                "CREATE INDEX idx_phone_models_chinese_model_id ON phone_models(chinese_model_id)"
            ))
            connection.commit()

        print("✅ Successfully added index on chinese_model_id column")
        return True

    except Exception as e:
        print(f"❌ Failed to add index on chinese_model_id: {e}")
        return False

def main():
    """Run the migration"""
    print("🚀 Starting database migration for mobile_shell_id...")
    print(f"Database URL: {engine.url}")

    # Step 1: Add the column
    if not add_mobile_shell_id_column():
        print("❌ Migration failed at step 1")
        return False

    # Step 2: Add index on mobile_shell_id
    if not add_index_on_mobile_shell_id():
        print("⚠️ Migration completed but index creation failed")
        return True  # Column was added successfully

    # Step 3: Add index on chinese_model_id (if not exists)
    if not add_index_on_chinese_model_id():
        print("⚠️ chinese_model_id index creation failed (might already exist)")

    print("🎉 Migration completed successfully!")
    print("")
    print("📋 Next steps:")
    print("1. Restart the application to load the new schema")
    print("2. The mobile_shell_id will be automatically populated from Chinese API on next sync")
    print("3. Verify with: SELECT name, chinese_model_id, mobile_shell_id FROM phone_models WHERE chinese_model_id IS NOT NULL;")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
