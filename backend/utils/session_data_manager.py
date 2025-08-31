"""
Centralized Session Data Management Utility

This module provides guaranteed session_data persistence with proper SQLAlchemy 
JSON field handling, verification, and error recovery.
"""

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from decimal import Decimal
import time
import logging
import json

logger = logging.getLogger(__name__)

def decimal_json_serializer(obj):
    """
    Custom JSON serializer that handles Decimal objects and other non-serializable types
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def safe_json_dumps(data):
    """
    Safely serialize data to JSON, handling Decimal objects
    """
    try:
        return json.dumps(data, default=decimal_json_serializer)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        # Fallback: convert problematic values to strings
        def fallback_serializer(obj):
            if isinstance(obj, (Decimal, datetime)):
                return str(obj)
            return str(obj)
        return json.dumps(data, default=fallback_serializer)

class SessionDataManager:
    """Centralized utility for guaranteed session_data persistence"""
    
    @staticmethod
    def update_session_data(
        db: Session,
        session_object: Any,  # VendingMachineSession object
        updates: Dict[str, Any],
        merge_strategy: str = "update",  # "update" or "replace"
        max_retries: int = 3,
        verify_persistence: bool = True
    ) -> bool:
        """
        Update session_data with guaranteed persistence
        
        Args:
            db: SQLAlchemy database session
            session_object: VendingMachineSession instance
            updates: Dictionary of updates to apply to session_data
            merge_strategy: "update" (merge with existing) or "replace" (replace entirely)
            max_retries: Maximum number of retry attempts
            verify_persistence: Whether to verify data was actually persisted
            
        Returns:
            bool: True if successful, False otherwise
        """
        original_session_data = session_object.session_data or {}
        session_id = session_object.session_id
        
        logger.info(f"🔄 SessionDataManager: Updating session_data for {session_id}")
        logger.info(f"   - Updates: {list(updates.keys())}")
        logger.info(f"   - Merge strategy: {merge_strategy}")
        
        for attempt in range(max_retries):
            try:
                # Prepare new session_data
                if merge_strategy == "update":
                    new_session_data = original_session_data.copy()
                    new_session_data.update(updates)
                elif merge_strategy == "replace":
                    new_session_data = updates.copy()
                else:
                    raise ValueError(f"Invalid merge_strategy: {merge_strategy}")
                
                # Log what we're about to store
                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}: Storing session_data")
                logger.info(f"   - Original keys: {list(original_session_data.keys())}")
                logger.info(f"   - New keys: {list(new_session_data.keys())}")
                
                # Apply updates to session object with safe JSON serialization
                # Convert any Decimal objects to float before storing
                safe_session_data = json.loads(safe_json_dumps(new_session_data))
                session_object.session_data = safe_session_data
                session_object.last_activity = datetime.now(timezone.utc)
                
                # Critical: Mark JSON field as modified
                flag_modified(session_object, 'session_data')
                
                # Log SQLAlchemy state
                logger.info(f"   - SQLAlchemy dirty objects: {len(db.dirty)}")
                logger.info(f"   - Session object in dirty set: {session_object in db.dirty}")
                
                # Commit changes
                db.commit()
                logger.info(f"✅ Session data committed successfully")
                
                # Verify persistence if requested
                if verify_persistence:
                    if SessionDataManager._verify_persistence(db, session_id, new_session_data):
                        logger.info(f"✅ SessionDataManager: Persistence verified for {session_id}")
                        return True
                    else:
                        logger.error(f"❌ SessionDataManager: Persistence verification failed for {session_id}")
                        if attempt < max_retries - 1:
                            logger.info(f"🔄 Retrying attempt {attempt + 2}/{max_retries}")
                            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                            continue
                        else:
                            return False
                else:
                    return True
                    
            except SQLAlchemyError as e:
                logger.error(f"❌ SQLAlchemy error in attempt {attempt + 1}/{max_retries}: {str(e)}")
                db.rollback()
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error in attempt {attempt + 1}/{max_retries}: {str(e)}")
                db.rollback()
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    return False
        
        return False
    
    @staticmethod
    def _verify_persistence(
        db: Session, 
        session_id: str, 
        expected_session_data: Dict[str, Any]
    ) -> bool:
        """
        Verify that session_data was actually persisted to database
        
        Args:
            db: SQLAlchemy database session
            session_id: Session ID to verify
            expected_session_data: Expected session_data content
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            from models import VendingMachineSession
            
            # Query fresh session from database
            fresh_session = db.query(VendingMachineSession).filter(
                VendingMachineSession.session_id == session_id
            ).first()
            
            if not fresh_session:
                logger.error(f"❌ Verification: Session {session_id} not found in database")
                return False
            
            if not fresh_session.session_data:
                logger.error(f"❌ Verification: session_data is None/empty for {session_id}")
                return False
            
            stored_data = fresh_session.session_data
            
            # Check that all expected keys are present
            for key, expected_value in expected_session_data.items():
                if key not in stored_data:
                    logger.error(f"❌ Verification: Missing key '{key}' in stored session_data")
                    return False
                
                stored_value = stored_data[key]
                
                # Special handling for nested dictionaries
                if isinstance(expected_value, dict) and isinstance(stored_value, dict):
                    for nested_key, nested_expected in expected_value.items():
                        if nested_key not in stored_value:
                            logger.error(f"❌ Verification: Missing nested key '{key}.{nested_key}'")
                            return False
                        if stored_value[nested_key] != nested_expected:
                            logger.error(f"❌ Verification: Value mismatch for '{key}.{nested_key}'")
                            logger.error(f"   Expected: {nested_expected}")
                            logger.error(f"   Stored: {stored_value[nested_key]}")
                            return False
                elif stored_value != expected_value:
                    # For non-dict values, direct comparison
                    # Allow some flexibility for datetime strings and similar
                    if not SessionDataManager._values_equivalent(expected_value, stored_value):
                        logger.error(f"❌ Verification: Value mismatch for key '{key}'")
                        logger.error(f"   Expected: {expected_value}")
                        logger.error(f"   Stored: {stored_value}")
                        return False
            
            logger.info(f"✅ Verification: All expected data found in database for {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification error for {session_id}: {str(e)}")
            return False
    
    @staticmethod
    def _values_equivalent(expected: Any, stored: Any) -> bool:
        """Check if two values are equivalent with some flexibility"""
        if expected == stored:
            return True
        
        # Handle string representations of numbers
        try:
            if isinstance(expected, (int, float)) and isinstance(stored, str):
                return float(expected) == float(stored)
            if isinstance(expected, str) and isinstance(stored, (int, float)):
                return float(expected) == float(stored)
        except (ValueError, TypeError):
            pass
        
        return False
    
    @staticmethod
    def add_payment_data(
        db: Session,
        session_object: Any,
        third_id: str,
        payment_amount: float,
        mobile_model_id: str,
        device_id: str,
        mobile_shell_id: Optional[str] = None,
        pay_type: int = 5
    ) -> bool:
        """
        Specialized method for adding payment data to session
        
        Args:
            db: SQLAlchemy database session
            session_object: VendingMachineSession instance
            third_id: Payment third_id
            payment_amount: Payment amount
            mobile_model_id: Mobile model ID
            device_id: Device ID
            mobile_shell_id: Mobile shell ID (optional)
            pay_type: Payment type (5 for vending, 12 for app)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure payment_amount is JSON serializable (convert Decimal to float)
        safe_payment_amount = float(payment_amount) if isinstance(payment_amount, Decimal) else payment_amount
        
        payment_updates = {
            "payment_data": {
                "third_id": third_id,
                "amount": safe_payment_amount,
                "mobile_model_id": mobile_model_id,
                "device_id": device_id,
                "pay_type": pay_type,
                "payment_initiated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        if mobile_shell_id:
            payment_updates["payment_data"]["mobile_shell_id"] = mobile_shell_id
        
        # Also store chinese_third_id at root level for compatibility
        payment_updates["chinese_third_id"] = third_id
        
        logger.info(f"🔄 SessionDataManager: Adding payment data for third_id {third_id}")
        
        return SessionDataManager.update_session_data(
            db=db,
            session_object=session_object,
            updates=payment_updates,
            merge_strategy="update",
            verify_persistence=True
        )
    
    @staticmethod
    def get_session_payment_data(session_object: Any) -> Optional[Dict[str, Any]]:
        """
        Safely extract payment data from session
        
        Args:
            session_object: VendingMachineSession instance
            
        Returns:
            Dict with payment data or None if not found
        """
        if not session_object or not session_object.session_data:
            return None
        
        session_data = session_object.session_data
        if not isinstance(session_data, dict):
            return None
        
        payment_data = session_data.get('payment_data', {})
        if not isinstance(payment_data, dict):
            return None
        
        return payment_data
    
    @staticmethod
    def find_session_by_third_id(db: Session, third_id: str) -> Optional[Any]:
        """
        Find vending session by third_id with comprehensive search
        
        Args:
            db: SQLAlchemy database session
            third_id: Third ID to search for
            
        Returns:
            VendingMachineSession object or None
        """
        from models import VendingMachineSession
        
        logger.info(f"🔍 SessionDataManager: Searching for session with third_id {third_id}")
        
        # Get all active/payment_pending sessions
        sessions = db.query(VendingMachineSession).filter(
            VendingMachineSession.status.in_(["active", "payment_pending"])
        ).all()
        
        logger.info(f"📊 Found {len(sessions)} sessions to search")
        
        for session in sessions:
            if not session.session_data or not isinstance(session.session_data, dict):
                continue
            
            # Check payment_data.third_id
            payment_data = session.session_data.get('payment_data', {})
            if isinstance(payment_data, dict) and payment_data.get('third_id') == third_id:
                logger.info(f"✅ Found session {session.session_id} by payment_data.third_id")
                return session
            
            # Check chinese_third_id (compatibility)
            if session.session_data.get('chinese_third_id') == third_id:
                logger.info(f"✅ Found session {session.session_id} by chinese_third_id")
                return session
        
        logger.warning(f"❌ No session found for third_id {third_id}")
        return None