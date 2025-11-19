from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ReportStatus(str, Enum):
    pending = "pending"
    under_review = "under_review"
    resolved = "resolved"
    dismissed = "dismissed"


class ReportType(str, Enum):
    review = "review"
    user = "user"
    movie = "movie"
    comment = "comment"


class ReportBase(BaseModel):
    type: ReportType = Field(..., description="What is being reported")
    reported_id: str = Field(..., description="ID of the item or user being reported")
    reason: str = Field(..., description="Short explanation for the report")

    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class ReportCreate(ReportBase):
    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class ReportUpdate(BaseModel):
    status: ReportStatus
    moderator_notes: Optional[str] = None

    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class Report(BaseModel):
    report_id: str
    reporter_id: str
    reported_id: str
    type: ReportType
    reason: str
    status: ReportStatus
    created_at: datetime
    resolved_at: Optional[str] = None
    moderator_id: Optional[str] = None
    moderator_notes: Optional[str] = None

    model_config = ConfigDict(
        validate_by_name=True,
        use_enum_values=True,
        from_attributes=True, 
        extra="forbid",
    )


class ReportSummary(BaseModel):
    total_reports: int
    pending: int
    under_review: int
    resolved: int
    dismissed: int

    model_config = ConfigDict(
        validate_by_name=True,
        extra="forbid",
    )
