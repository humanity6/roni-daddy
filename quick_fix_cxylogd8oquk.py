#!/usr/bin/env python3
"""
QUICK FIX for CXYLOGD8OQUK session limit exceeded error

This script immediately cleans up all expired/inactive sessions 
for machine CXYLOGD8OQUK and resets the session counter.

Usage: python quick_fix_cxylogd8oquk.py
"""

import sys
import os
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_fix():
    """Immediate fix for session limit exceeded error"""
    
    print("🔧 QUICK FIX: Resolving session limit exceeded error for CXYLOGD8OQUK")
    print("=" * 70)
    
    try:
        from database import get_db
        from models import VendingMachineSession
        from sqlalchemy.orm import Session
        
        # Get database session
        db = next(get_db())
        machine_id = "CXYLOGD8OQUK"
        
        try:
            # Find sessions to clean up
            current_time = datetime.now(timezone.utc)
            
            # Get all sessions for this machine
            all_sessions = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id
            ).all()
            
            print(f"📊 Found {len(all_sessions)} total sessions for {machine_id}")
            
            # Identify sessions to clean up
            sessions_to_delete = []
            for session in all_sessions:
                # Handle timezone-aware comparison
                expires_at = session.expires_at
                if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                # Delete if expired or in terminal status
                if (current_time > expires_at or 
                    session.status in ['expired', 'cancelled', 'payment_completed']):
                    sessions_to_delete.append(session)
            
            print(f"🧹 Cleaning up {len(sessions_to_delete)} expired/inactive sessions")
            
            # Delete expired sessions
            for session in sessions_to_delete:
                print(f"  ❌ Deleting: {session.session_id} (status: {session.status})")
                db.delete(session)
            
            # Commit changes
            db.commit()
            print(f"✅ Deleted {len(sessions_to_delete)} sessions from database")
            
            # Reset in-memory session counter
            from security_middleware import security_manager
            old_count = security_manager.machine_sessions.get(machine_id, 0)
            security_manager.machine_sessions[machine_id] = 0
            
            print(f"🔄 Reset in-memory session counter: {old_count} → 0")
            
            # Check remaining active sessions
            remaining_sessions = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id,
                VendingMachineSession.status == "active",
                VendingMachineSession.expires_at > current_time
            ).count()
            
            print(f"📈 Remaining active sessions: {remaining_sessions}")
            print()
            print("🎉 SUCCESS! Machine CXYLOGD8OQUK should now be able to create new sessions.")
            print()
            print("Next steps:")
            print("1. Try creating a new session - it should work now")
            print("2. If you still get errors, run this script again")
            print("3. For more detailed management, use: python cleanup_cxylogd8oquk_sessions.py")
            
        except Exception as e:
            db.rollback()
            print(f"❌ ERROR: {str(e)}")
            raise
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("Make sure you're running this script from the correct directory")
        print("Required files: database.py, models.py, security_middleware.py")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("Starting quick fix...")
    success = quick_fix()
    
    if success:
        print("\n✨ Fix completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Fix failed - check errors above")
        sys.exit(1)