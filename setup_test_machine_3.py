#!/usr/bin/env python3
"""
Create a third test vending machine with no underscores in the machine ID
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_server import get_db, VendingMachine
    from sqlalchemy.orm import Session
    
    def create_test_machine_3():
        """Create a third test vending machine with proper ID format"""
        
        db = next(get_db())
        
        try:
            # Check if third test machine already exists
            existing_machine = db.query(VendingMachine).filter(
                VendingMachine.id == "VMTEST003"
            ).first()
            
            if existing_machine:
                print("Test vending machine 3 already exists:")
                print(f"   ID: {existing_machine.id}")
                print(f"   Name: {existing_machine.name}")
                print(f"   Location: {existing_machine.location}")
                print(f"   Active: {existing_machine.is_active}")
                return
            
            # Create new test vending machine with no underscores
            test_machine = VendingMachine(
                id="VMTEST003",
                name="Test Vending Machine 3",
                location="Test Location 3 - Mall",
                is_active=True,
                qr_config={
                    "base_url": "https://pimpmycase.shop",
                    "test_mode": True
                }
            )
            
            db.add(test_machine)
            db.commit()
            
            print("Test vending machine 3 created successfully!")
            print(f"   ID: {test_machine.id}")
            print(f"   Name: {test_machine.name}")
            print(f"   Location: {test_machine.location}")
            print(f"   Active: {test_machine.is_active}")
            print()
            print("This machine ID has no underscores and should work with session validation!")
            
        except Exception as e:
            db.rollback()
            print(f"Error creating test machine 3: {e}")
            raise
        finally:
            db.close()
    
    if __name__ == "__main__":
        create_test_machine_3()
        print("\nNow you can use machine_id=VMTEST003 for testing!")
        print("Session IDs will be: VMTEST003_20250807_HHMMSS_RANDOM")

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)