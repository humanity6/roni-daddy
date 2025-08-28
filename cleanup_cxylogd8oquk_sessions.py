#!/usr/bin/env python3
"""
Script to manage vending machine sessions for CXYLOGD8OQUK
Resolves "session limit exceeded" errors by cleaning up old/expired sessions
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import get_db
    from models import VendingMachineSession, VendingMachine
    from sqlalchemy.orm import Session
    
    def list_machine_sessions(machine_id: str = "CXYLOGD8OQUK"):
        """List all sessions for the specified machine"""
        
        # Get database session
        db = next(get_db())
        
        try:
            # Find all sessions for the machine
            sessions = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id
            ).order_by(VendingMachineSession.created_at.desc()).all()
            
            print(f"Found {len(sessions)} sessions for machine {machine_id}")
            
            if not sessions:
                print("No sessions found")
                return []
            
            print(f"\n{'Session ID':<50} {'Status':<15} {'Created':<20} {'Expires':<20} {'Active/Expired'}")
            print("=" * 120)
            
            current_time = datetime.now(timezone.utc)
            active_sessions = []
            expired_sessions = []
            
            for session in sessions:
                # Handle timezone-aware comparison
                expires_at = session.expires_at
                if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                is_expired = current_time > expires_at
                status_display = "EXPIRED" if is_expired else "ACTIVE"
                
                created_str = session.created_at.strftime("%Y-%m-%d %H:%M:%S") if session.created_at else "Unknown"
                expires_str = expires_at.strftime("%Y-%m-%d %H:%M:%S") if expires_at else "Unknown"
                
                print(f"{session.session_id:<50} {session.status:<15} {created_str:<20} {expires_str:<20} {status_display}")
                
                if is_expired or session.status in ['expired', 'cancelled']:
                    expired_sessions.append(session)
                else:
                    active_sessions.append(session)
            
            print(f"\nSummary:")
            print(f"  Active sessions: {len(active_sessions)}")
            print(f"  Expired/inactive sessions: {len(expired_sessions)}")
            
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            raise
        finally:
            db.close()
    
    def cleanup_expired_sessions(machine_id: str = "CXYLOGD8OQUK", force_all: bool = False):
        """Clean up expired sessions for the specified machine"""
        
        # Get database session
        db = next(get_db())
        
        try:
            current_time = datetime.now(timezone.utc)
            
            if force_all:
                # Delete ALL sessions for the machine (use with caution)
                sessions_to_delete = db.query(VendingMachineSession).filter(
                    VendingMachineSession.machine_id == machine_id
                ).all()
                
                print(f"WARNING: Deleting ALL {len(sessions_to_delete)} sessions for machine {machine_id}")
            else:
                # Only delete expired sessions or inactive ones
                sessions_to_delete = db.query(VendingMachineSession).filter(
                    VendingMachineSession.machine_id == machine_id
                ).filter(
                    (VendingMachineSession.expires_at < current_time) |
                    (VendingMachineSession.status.in_(['expired', 'cancelled', 'payment_completed']))
                ).all()
                
                print(f"Found {len(sessions_to_delete)} expired/inactive sessions to delete")
            
            if not sessions_to_delete:
                print("No sessions to delete")
                return 0
            
            # Show what will be deleted
            print("\nSessions to be deleted:")
            for session in sessions_to_delete:
                print(f"  {session.session_id} - {session.status} - Created: {session.created_at}")
            
            # Confirm deletion
            if not force_all:
                confirm = input("\nProceed with deletion? (y/N): ")
                if confirm.lower() != 'y':
                    print("Deletion cancelled")
                    return 0
            
            # Delete sessions
            deleted_count = len(sessions_to_delete)
            for session in sessions_to_delete:
                db.delete(session)
            
            db.commit()
            
            print(f"\nDeleted {deleted_count} sessions")
            print(f"Machine {machine_id} should now be able to create new sessions")
            
            return deleted_count
            
        except Exception as e:
            db.rollback()
            print(f"Error cleaning up sessions: {e}")
            raise
        finally:
            db.close()
    
    def check_machine_info(machine_id: str = "CXYLOGD8OQUK"):
        """Check if the vending machine exists and its configuration"""
        
        # Get database session
        db = next(get_db())
        
        try:
            machine = db.query(VendingMachine).filter(
                VendingMachine.id == machine_id
            ).first()
            
            if machine:
                print(f"Machine {machine_id} found:")
                print(f"  Name: {machine.name}")
                print(f"  Location: {machine.location}")
                print(f"  Active: {machine.is_active}")
                print(f"  Created: {machine.created_at}")
                print(f"  Last Heartbeat: {machine.last_heartbeat}")
                print(f"  QR Config: {machine.qr_config}")
            else:
                print(f"Machine {machine_id} not found in database")
                print("This machine will be auto-created when a session is requested")
            
        except Exception as e:
            print(f"Error checking machine info: {e}")
            raise
        finally:
            db.close()
    
    def reset_machine_session_count():
        """Reset the in-memory session count for security manager"""
        try:
            from security_middleware import security_manager
            machine_id = "CXYLOGD8OQUK"
            
            print(f"Current session count for {machine_id}: {security_manager.machine_sessions.get(machine_id, 0)}")
            security_manager.machine_sessions[machine_id] = 0
            print(f"Reset session count for {machine_id} to 0")
            
        except Exception as e:
            print(f"Error resetting session count: {e}")
    
    def main():
        machine_id = "CXYLOGD8OQUK"
        
        print(f"Vending Machine Session Manager for {machine_id}")
        print("=" * 60)
        
        while True:
            print(f"\nOptions:")
            print("1. List all sessions")
            print("2. Clean up expired/inactive sessions")
            print("3. Force delete ALL sessions (DANGER!)")
            print("4. Check machine information")
            print("5. Reset in-memory session count")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ")
            
            try:
                if choice == '1':
                    list_machine_sessions(machine_id)
                
                elif choice == '2':
                    deleted = cleanup_expired_sessions(machine_id, force_all=False)
                    if deleted > 0:
                        reset_machine_session_count()
                
                elif choice == '3':
                    print("\n⚠️  WARNING: This will delete ALL sessions for the machine!")
                    confirm = input("Type 'DELETE ALL' to confirm: ")
                    if confirm == 'DELETE ALL':
                        deleted = cleanup_expired_sessions(machine_id, force_all=True)
                        reset_machine_session_count()
                    else:
                        print("Operation cancelled")
                
                elif choice == '4':
                    check_machine_info(machine_id)
                
                elif choice == '5':
                    reset_machine_session_count()
                
                elif choice == '6':
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please select 1-6.")
            
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the correct directory")
    print("Required files: database.py, models.py, security_middleware.py")
    sys.exit(1)