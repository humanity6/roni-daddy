"""Admin API routes for session management"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import VendingMachineSession, VendingMachine
from datetime import datetime, timezone
from typing import Optional, List

router = APIRouter(prefix="/api/admin")

@router.get("/machines/{machine_id}/sessions")
async def list_machine_sessions(
    machine_id: str,
    status: Optional[str] = Query(None, description="Filter by status (active, expired, etc.)"),
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    db: Session = Depends(get_db)
):
    """List sessions for a specific vending machine"""
    try:
        # Base query
        query = db.query(VendingMachineSession).filter(
            VendingMachineSession.machine_id == machine_id
        )
        
        # Apply status filter if provided
        if status:
            query = query.filter(VendingMachineSession.status == status)
        
        # Order by creation date (newest first) and limit results
        sessions = query.order_by(
            VendingMachineSession.created_at.desc()
        ).limit(limit).all()
        
        # Format response
        current_time = datetime.now(timezone.utc)
        session_list = []
        
        for session in sessions:
            # Handle timezone-aware comparison
            expires_at = session.expires_at
            if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            is_expired = current_time > expires_at
            
            session_info = {
                "session_id": session.session_id,
                "machine_id": session.machine_id,
                "status": session.status,
                "user_progress": session.user_progress,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                "is_expired": is_expired,
                "payment_amount": float(session.payment_amount) if session.payment_amount else None,
                "payment_method": session.payment_method,
                "order_id": session.order_id,
                "ip_address": session.ip_address
            }
            session_list.append(session_info)
        
        # Count expired sessions
        expired_count = sum(1 for s in session_list if s["is_expired"] or s["status"] in ["expired", "cancelled"])
        active_count = len(session_list) - expired_count
        
        return {
            "machine_id": machine_id,
            "total_sessions": len(session_list),
            "active_sessions": active_count,
            "expired_sessions": expired_count,
            "sessions": session_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.delete("/machines/{machine_id}/sessions/cleanup")
async def cleanup_machine_sessions(
    machine_id: str,
    force: bool = Query(False, description="Force delete all sessions (DANGER)"),
    db: Session = Depends(get_db)
):
    """Clean up expired or inactive sessions for a specific machine"""
    try:
        current_time = datetime.now(timezone.utc)
        
        if force:
            # Delete ALL sessions for the machine
            sessions_to_delete = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id
            ).all()
        else:
            # Only delete expired or inactive sessions
            sessions_to_delete = db.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id
            ).filter(
                (VendingMachineSession.expires_at < current_time) |
                (VendingMachineSession.status.in_(['expired', 'cancelled', 'payment_completed']))
            ).all()
        
        if not sessions_to_delete:
            return {
                "machine_id": machine_id,
                "deleted_count": 0,
                "message": "No sessions to delete"
            }
        
        # Collect session info before deletion
        deleted_sessions = []
        for session in sessions_to_delete:
            deleted_sessions.append({
                "session_id": session.session_id,
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None
            })
            db.delete(session)
        
        db.commit()
        
        # Reset in-memory session count
        from security_middleware import security_manager
        security_manager.machine_sessions[machine_id] = 0
        
        return {
            "machine_id": machine_id,
            "deleted_count": len(deleted_sessions),
            "deleted_sessions": deleted_sessions,
            "message": f"Deleted {len(deleted_sessions)} sessions. Machine can now create new sessions."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_single_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific session by ID"""
    try:
        session = db.query(VendingMachineSession).filter(
            VendingMachineSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        machine_id = session.machine_id
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        # Decrement session count
        from security_middleware import security_manager
        security_manager.decrement_machine_sessions(machine_id)
        
        return {
            "session_id": session_id,
            "machine_id": machine_id,
            "message": "Session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.get("/machines/{machine_id}/info")
async def get_machine_info(
    machine_id: str,
    db: Session = Depends(get_db)
):
    """Get information about a vending machine"""
    try:
        machine = db.query(VendingMachine).filter(
            VendingMachine.id == machine_id
        ).first()
        
        # Count current sessions
        current_time = datetime.now(timezone.utc)
        total_sessions = db.query(VendingMachineSession).filter(
            VendingMachineSession.machine_id == machine_id
        ).count()
        
        active_sessions = db.query(VendingMachineSession).filter(
            VendingMachineSession.machine_id == machine_id,
            VendingMachineSession.status == "active",
            VendingMachineSession.expires_at > current_time
        ).count()
        
        # Get in-memory session count
        from security_middleware import security_manager
        memory_session_count = security_manager.machine_sessions.get(machine_id, 0)
        
        if machine:
            return {
                "machine_id": machine_id,
                "exists": True,
                "name": machine.name,
                "location": machine.location,
                "is_active": machine.is_active,
                "created_at": machine.created_at.isoformat() if machine.created_at else None,
                "last_heartbeat": machine.last_heartbeat.isoformat() if machine.last_heartbeat else None,
                "qr_config": machine.qr_config,
                "session_stats": {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "memory_session_count": memory_session_count,
                    "session_limit": 5  # Default limit
                }
            }
        else:
            return {
                "machine_id": machine_id,
                "exists": False,
                "message": "Machine not found. Will be auto-created on first session request.",
                "session_stats": {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "memory_session_count": memory_session_count,
                    "session_limit": 5
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get machine info: {str(e)}")

@router.post("/machines/{machine_id}/reset-session-count")
async def reset_machine_session_count(
    machine_id: str
):
    """Reset the in-memory session count for a machine"""
    try:
        from security_middleware import security_manager
        
        old_count = security_manager.machine_sessions.get(machine_id, 0)
        security_manager.machine_sessions[machine_id] = 0
        
        return {
            "machine_id": machine_id,
            "old_session_count": old_count,
            "new_session_count": 0,
            "message": "Session count reset successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset session count: {str(e)}")