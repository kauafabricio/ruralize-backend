from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PointsTransactionCreate(BaseModel):
    """Create a points transaction"""
    user_id: str
    amount: int
    transaction_type: str  # "event_attendance", "reward_redemption", "manual_award"
    description: str
    related_id: Optional[str] = None  # event_id or reward_id


class PointsTransactionResponse(BaseModel):
    """Points transaction record"""
    id: str
    user_id: str
    amount: int
    transaction_type: str
    description: str
    related_id: Optional[str] = None
    created_at: datetime


class PointsHistoryResponse(BaseModel):
    """Points transaction history"""
    transactions: list[PointsTransactionResponse]
    total: int


class PointsBalanceResponse(BaseModel):
    """Current user's points balance"""
    user_id: str
    balance: int
    total_earned: int
    total_spent: int
