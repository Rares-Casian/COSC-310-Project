from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.reports import utils, schemas
from backend.authentication.security import get_current_user
from backend.core.authz import require_role, block_if_penalized

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=schemas.ReportSummary)
def get_summary(current_user=Depends(get_current_user)):
    require_role(current_user, ["moderator", "administrator"])
    return utils.get_summary()


@router.post("/", response_model=schemas.Report)
@block_if_penalized(["report_ban", "posting_ban", "suspension"])
async def submit_report(report: schemas.ReportCreate, current_user=Depends(get_current_user)):
    require_role(current_user, ["member", "critic"])
    return utils.create_report(
        reporter_id=current_user.user_id,
        reported_id=report.reported_id,
        type=report.type,
        reason=report.reason,
    )


@router.get("/", response_model=List[schemas.Report])
def get_all_reports(current_user=Depends(get_current_user)):
    require_role(current_user, ["moderator", "administrator"])
    return utils.load_reports()


@router.get("/{report_id}", response_model=schemas.Report)
def get_report(report_id: str, current_user=Depends(get_current_user)):
    require_role(current_user, ["moderator", "administrator"])
    report = utils.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@router.patch("/{report_id}", response_model=schemas.Report)
def update_report(report_id: str, update: schemas.ReportUpdate, current_user=Depends(get_current_user)):
    require_role(current_user, ["moderator", "administrator"])
    updated = utils.update_report_status(report_id, update, moderator_id=current_user.user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found.")
    return updated


@router.delete("/{report_id}")
def delete_report(report_id: str, current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    if not utils.delete_report(report_id):
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"message": f"Report {report_id} deleted successfully."}
