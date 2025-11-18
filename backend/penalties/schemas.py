"""Penalty data models and helpers for expiry/time remaining."""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field


class PenaltyStatus(str, Enum):
    active = "active"
    expired = "expired"
    resolved = "resolved"


class PenaltyType(str, Enum):
    suspension = "suspension"
    review_ban = "review_ban"
    report_ban = "report_ban"
    posting_ban = "posting_ban"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class PenaltyCreate(BaseModel):
    user_id: str
    type: PenaltyType
    severity: Severity
    reason: str
    duration_days: Optional[int] = Field(None, ge=1, description="If None, treat as indefinite until resolved")


class Penalty(BaseModel):
    penalty_id: str
    user_id: str
    type: PenaltyType
    severity: Severity
    reason: str
    issued_by: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: PenaltyStatus = PenaltyStatus.active
    notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None

    @property
    def time_remaining(self) -> Optional[str]:
        if self.status != PenaltyStatus.active or not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        if delta.total_seconds() <= 0:
            return "0d 0h 0m"
        days = delta.days
        hours = (delta.seconds // 3600)
        minutes = (delta.seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

    def has_expired(self) -> bool:
        return bool(self.expires_at and datetime.utcnow() >= self.expires_at)


def calculate_expiry(p_type: PenaltyType, severity: Severity, duration_days: Optional[int]) -> Optional[datetime]:
    """Compute expiry. If duration_days provided, prefer it; otherwise derive a default window by severity."""
    if duration_days is not None:
        return datetime.utcnow() + timedelta(days=duration_days)
    defaults = {Severity.low: 3, Severity.medium: 7, Severity.high: 30}
    return datetime.utcnow() + timedelta(days=defaults.get(severity, 7))
