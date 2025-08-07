#!/usr/bin/env python3
"""
Script to clean up old test vending machine sessions that may be blocking new sessions
"""

import sys
import os
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_server import get_db, VendingMachineSession
    from sqlalchemy.orm import Session
    
    def cleanup_test_sessions():
        """Clean up old vending machine sessions for VM_TEST_001"""
        
        # Get database session
        db = next(get_db())
        
        try:
            # Find all sessions for the test machine
            test_sessions = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == "VM_TEST_001"
            ).all()
            
            print(f"Found {len(test_sessions)} sessions for VM_TEST_001")
            
            if not test_sessions:
                print("No sessions to clean up")
                return
            
            # Show current sessions
            print("\nCurrent sessions:")
            for session in test_sessions:
                status = "EXPIRED" if datetime.now(timezone.utc) > session.expires_at else "ACTIVE"
                print(f"  {session.session_id} - {session.status} - {status}")
            
            # Delete all test sessions
            deleted_count = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == "VM_TEST_001"
            ).delete()
            
            db.commit()
            
            print(f"\nDeleted {deleted_count} test sessions")
            print("Test machine is now ready for new sessions")
            
        except Exception as e:
            db.rollback()
            print(f"Error cleaning up sessions: {e}")
            raise
        finally:
            db.close()
    
    def main():
        print("Cleaning up test vending machine sessions...")
        print("=" * 50)
        
        try:
            cleanup_test_sessions()
            print("\nCleanup complete!")
            print("\nYou can now:")
            print("1. Generate a new test link: python generate_vending_test_link.py")
            print("2. Test the vending machine payment flow")
            
        except Exception as e:
            print(f"Cleanup failed: {e}")
            sys.exit(1)

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)