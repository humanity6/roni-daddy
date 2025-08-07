"""Vending machine-related Pydantic models"""

from pydantic import BaseModel
from typing import Optional

class CreateSessionRequest(BaseModel):
    machine_id: str
    location: Optional[str] = None
    session_timeout_minutes: Optional[int] = 30
    metadata: Optional[dict] = {}

class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    user_progress: str
    order_id: Optional[str] = None
    payment_amount: Optional[float] = None
    expires_at: str
    created_at: str
    last_activity: str

class OrderSummaryRequest(BaseModel):
    session_id: str
    order_data: dict
    payment_amount: float
    currency: str = "GBP"

class VendingPaymentConfirmRequest(BaseModel):
    session_id: str
    payment_method: str  # 'card', 'cash', 'contactless'
    payment_amount: float
    transaction_id: str
    payment_data: Optional[dict] = {}

class QRParametersRequest(BaseModel):
    machine_id: str
    session_id: str
    location: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None