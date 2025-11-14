"""
Handles report creation, retrieval, and moderation actions.
Routes are protected by role-based access (member/critic vs moderator/admin).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from backend.reports import utils, schemas
from backend.authentication.security import get_current_user
from backend.penalties import utils as penalty_utils

router = APIRouter(prefix="/reports", tags=["Reports"])

# --- MODERATOR/ADMIN: Summary endpoint ---
@router.get("/summary", response_model=schemas.ReportSummary)
def get_summary(user=Depends(get_current_user)):
    """Retrieve a summary of report statuses for dashboard analytics."""
    if user.role not in ["moderator", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    return utils.get_summary()

# --- MODERATOR/ADMIN: View all reports ---
@router.get("/", response_model=List[schemas.Report])
def get_all_reports(user=Depends(get_current_user)):
    """Retrieve all reports (moderator/admin only)."""
    if user.role not in ["moderator", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    return utils.load_reports()


# --- MODERATOR/ADMIN: View single report ---
@router.get("/{report_id}", response_model=schemas.Report)
def get_report(report_id: str, user=Depends(get_current_user)):
    """Retrieve a specific report (moderator/admin only)."""
    if user.role not in ["moderator", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    report = utils.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report

# --- ADMIN: Delete report ---
@router.delete("/{report_id}")
def delete_report(report_id: str, user=Depends(get_current_user)):
    """Delete a report (admin only)."""
    if user.role != "administrator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only.")
    deleted = utils.delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"message": f"Report {report_id} deleted."}
