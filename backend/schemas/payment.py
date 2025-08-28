"""Payment-related Pydantic models"""

from pydantic import BaseModel
from typing import Optional

class CheckoutSessionRequest(BaseModel):
    amount: Optional[float] = None  # Legacy field - kept for backward compatibility
    amount_pence: Optional[int] = None  # CRITICAL FIX: New field for precise pence amounts
    template_id: str
    brand: str
    model: str
    color: str
    design_image: Optional[str] = None
    order_id: Optional[str] = None

class PaymentSuccessRequest(BaseModel):
    session_id: str
    order_data: dict