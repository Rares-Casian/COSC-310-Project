"""Penalty data models and helpers for expiry/time remaining."""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

PenaltyType = Literal[
    "review_ban",
    "report_ban",
    "posting_ban",
    "suspension",
    "warning"
]

PenaltySeverity = Literal["minor", "moderate", "severe"]
PenaltyStatus = Literal["active", "resolved", "expired"]


class PenaltyStatusEnum(str, Enum):
    active = "active"
    expired = "expired"
    resolved = "resolved"


class PenaltyTypeEnum(str, Enum):
    suspension = "suspension"
    review_ban = "review_ban"
    report_ban = "report_ban"
    posting_ban = "posting_ban"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"



class PenaltyBase(BaseModel):
    user_id: str
    type: PenaltyType
    severity: PenaltySeverity = "minor"
    reason: str
    notes: Optional[str] = None

    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class PenaltyCreate(BaseModel):
    user_id: str
    type: PenaltyTypeEnum
    severity: Severity
    reason: str
    duration_days: Optional[int] = Field(
        None,
        ge=1,
        description="If None, treat as indefinite until resolved"
    )

    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class Penalty(BaseModel):
    penalty_id: str
    user_id: str
    type: PenaltyTypeEnum
    severity: Severity
    reason: str
    issued_by: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: PenaltyStatusEnum = PenaltyStatusEnum.active
    notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )

    
    def has_expired(self) -> bool:
        """Return True if this penalty's expiry date has passed."""
        if not self.expires_at:
            return False
        try:
            return datetime.utcnow() > (
                self.expires_at if isinstance(self.expires_at, datetime)
                else datetime.fromisoformat(self.expires_at)
            )
        except Exception:
            return False

    @property
    def time_remaining(self) -> Optional[str]:
        if not self.expires_at:
            return None
        try:
            expires = (
                self.expires_at if isinstance(self.expires_at, datetime)
                else datetime.fromisoformat(self.expires_at)
            )
            remaining = expires - datetime.utcnow()
            if remaining.total_seconds() <= 0:
                return "Expired"

            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60

            if days > 0:
                return f"{days}d {hours}h remaining"
            if hours > 0:
                return f"{hours}h {minutes}m remaining"
            return f"{minutes}m remaining"

        except Exception:
            return None

    @property
    def time_remaining_seconds(self) -> Optional[int]:
        """Exact seconds remaining until expiry."""
        if not self.expires_at:
            return None
        try:
            expires = (
                self.expires_at if isinstance(self.expires_at, datetime)
                else datetime.fromisoformat(self.expires_at)
            )
            remaining = expires - datetime.utcnow()
            return max(0, int(remaining.total_seconds()))
        except Exception:
            return None

def calculate_expiry(
    p_type: PenaltyType,
    severity: PenaltySeverity,
    duration_days: Optional[int] = None
) -> Optional[str]:
    now = datetime.utcnow()

    if duration_days and duration_days > 0:
        return (now + timedelta(days=duration_days)).isoformat()

    if p_type == "warning":
        return None

    if severity == "minor":
        return (now + timedelta(days=3)).isoformat()
    if severity == "moderate":
        return (now + timedelta(days=7)).isoformat()
    if severity == "severe":
        if p_type == "suspension":
            return (now + timedelta(days=30)).isoformat()
        return (now + timedelta(days=14)).isoformat()

    return (now + timedelta(days=7)).isoformat()
