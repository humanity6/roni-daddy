#!/usr/bin/env python3
"""
Script to set up a test vending machine in the database for testing purposes.
This creates a test machine that can be used with the vending machine payment flow.
"""

import sys
import os

# Add the current directory to Python path to import from api_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_server import get_db, VendingMachine
    from sqlalchemy.orm import Session
    from datetime import datetime, timezone
    
    def create_test_vending_machine():
        """Create a test vending machine in the database"""
        
        # Get database session
        db = next(get_db())
        
        try:
            # Check if test machine already exists
            existing_machine = db.query(VendingMachine).filter(
                VendingMachine.id == "VM_TEST_001"
            ).first()
            
            if existing_machine:
                print("Test vending machine already exists:")
                print(f"   ID: {existing_machine.id}")
                print(f"   Name: {existing_machine.name}")
                print(f"   Location: {existing_machine.location}")
                print(f"   Active: {existing_machine.is_active}")
                return
            
            # Create new test vending machine
            test_machine = VendingMachine(
                id="VM_TEST_001",
                name="Test Vending Machine",
                location="Test Location - Shopping Mall",
                is_active=True,
                qr_config={
                    "base_url": "https://pimpmycase.shop",
                    "test_mode": True
                }
            )
            
            # Add to database
            db.add(test_machine)
            db.commit()
            
            print("Test vending machine created successfully!")
            print(f"   ID: {test_machine.id}")
            print(f"   Name: {test_machine.name}")
            print(f"   Location: {test_machine.location}")
            print(f"   Active: {test_machine.is_active}")
            print()
            print("You can now use this machine_id in your test URLs:")
            print("   machine_id=VM_TEST_001")
            
        except Exception as e:
            db.rollback()
            print(f"Error creating test vending machine: {e}")
            raise
        finally:
            db.close()
    
    def main():
        print("Setting up test vending machine...")
        print("=" * 50)
        
        try:
            create_test_vending_machine()
            print()
            print("Test setup complete!")
            print()
            print("Next steps:")
            print("1. Use the test link generator: python generate_vending_test_link.py")
            print("2. The generated URL will now work with the vending machine payment flow")
            print("3. The frontend will create a session and register properly")
            
        except Exception as e:
            print(f"Setup failed: {e}")
            print()
            print("Make sure:")
            print("1. The database is running and accessible")
            print("2. All database tables are created")
            print("3. You have the correct database permissions")
            sys.exit(1)

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print()
    print("Make sure you're running this script from the correct directory and that")
    print("all required dependencies are installed:")
    print("   pip install -r requirements-api.txt")
    sys.exit(1)