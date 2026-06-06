from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class RewardCreate(BaseModel):
    """Create a reward"""
    name: str
    description: str
    points_required: int
    category: str  # "food", "bottle", "other"
    image_url: Optional[str] = None
    quantity_available: Optional[int] = None  # None = unlimited


class RewardUpdate(BaseModel):
    """Update a reward"""
    name: Optional[str] = None
    description: Optional[str] = None
    points_required: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    quantity_available: Optional[int] = None


class RewardResponse(BaseModel):
    """Reward details"""
    id: str
    name: str
    description: str
    points_required: int
    category: str
    image_url: Optional[str] = None
    quantity_available: Optional[int] = None
    quantity_redeemed: Optional[int] = 0
    created_at: datetime


class RewardRedemptionRequest(BaseModel):
    """Request to redeem a reward"""
    reward_id: str


class RewardRedemptionResponse(BaseModel):
    """Reward redemption response"""
    id: str
    user_id: str
    reward_id: str
    reward_name: str
    user_email: str
    user_name: str
    points_deducted: int
    redemption_code: str
    pickup_deadline: datetime
    redeemed_at: datetime
    status: str  # "pending", "confirmed", "collected"
    message: str


class RewardRedemptionDetail(BaseModel):
    """Detailed reward redemption record"""
    id: str
    user_id: str
    user_email: str
    user_name: str
    reward_id: str
    reward_name: str
    points_deducted: int
    redemption_code: str
    pickup_deadline: datetime
    status: str  # "pending", "confirmed", "collected"
    email_sent_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    redeemed_at: datetime
