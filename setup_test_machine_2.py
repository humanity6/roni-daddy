#!/usr/bin/env python3
"""
Create a second test vending machine for testing when the first one hits session limits
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_server import get_db, VendingMachine
    from sqlalchemy.orm import Session
    
    def create_test_machine_2():
        """Create a second test vending machine"""
        
        db = next(get_db())
        
        try:
            # Check if second test machine already exists
            existing_machine = db.query(VendingMachine).filter(
                VendingMachine.id == "VM_TEST_002"
            ).first()
            
            if existing_machine:
                print("Test vending machine 2 already exists:")
                print(f"   ID: {existing_machine.id}")
                print(f"   Name: {existing_machine.name}")
                print(f"   Location: {existing_machine.location}")
                print(f"   Active: {existing_machine.is_active}")
                return
            
            # Create new test vending machine
            test_machine = VendingMachine(
                id="VM_TEST_002",
                name="Test Vending Machine 2",
                location="Test Location 2 - Shopping Center",
                is_active=True,
                qr_config={
                    "base_url": "https://pimpmycase.shop",
                    "test_mode": True
                }
            )
            
            db.add(test_machine)
            db.commit()
            
            print("Test vending machine 2 created successfully!")
            print(f"   ID: {test_machine.id}")
            print(f"   Name: {test_machine.name}")
            print(f"   Location: {test_machine.location}")
            print(f"   Active: {test_machine.is_active}")
            
        except Exception as e:
            db.rollback()
            print(f"Error creating test machine 2: {e}")
            raise
        finally:
            db.close()
    
    if __name__ == "__main__":
        create_test_machine_2()
        print("\nNow you can use machine_id=VM_TEST_002 for testing!")

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)