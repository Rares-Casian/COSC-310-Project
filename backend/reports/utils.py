import uuid
from datetime import datetime
from typing import List, Optional
from backend.core.paths import REPORTS_FILE
from backend.core.jsonio import load_json, save_json
from backend.reports import schemas


def _load() -> List[dict]:
    return load_json(REPORTS_FILE, default=[])


def _save(data: List[dict]) -> None:
    save_json(REPORTS_FILE, data)


def load_reports() -> List[schemas.Report]:
    return [schemas.Report(**r) for r in _load()]


def get_report(report_id: str) -> Optional[schemas.Report]:
    for r in _load():
        if r.get("report_id") == report_id:
            return schemas.Report(**r)
    return None


def create_report(reporter_id: str, reported_id: str, type: schemas.ReportType, reason: str) -> schemas.Report:
    data = _load()
    new = schemas.Report(
        report_id=str(uuid.uuid4()),
        reporter_id=reporter_id,
        reported_id=reported_id,
        type=type,
        reason=reason,
        status=schemas.ReportStatus.pending,
        created_at=datetime.utcnow(),
        resolved_at=None,
        moderator_id=None,
        moderator_notes=None,
    )
    data.append(new.dict())
    _save(data)
    return new


def update_report_status(report_id: str, update: schemas.ReportUpdate, moderator_id: str) -> Optional[schemas.Report]:
    data = _load()
    for r in data:
        if r.get("report_id") == report_id:
            r["status"] = update.status
            r["moderator_id"] = moderator_id
            r["moderator_notes"] = update.moderator_notes
            if update.status in [schemas.ReportStatus.resolved, schemas.ReportStatus.dismissed]:
                r["resolved_at"] = datetime.utcnow().isoformat()
            _save(data)
            return schemas.Report(**r)
    return None


def delete_report(report_id: str) -> bool:
    data = _load()
    updated = [r for r in data if r.get("report_id") != report_id]
    if len(updated) == len(data):
        return False
    _save(updated)
    return True


def filter_reports_by_status(status: schemas.ReportStatus) -> List[schemas.Report]:
    return [schemas.Report(**r) for r in _load() if r.get("status") == status]


def get_summary() -> schemas.ReportSummary:
    data = _load()
    total = len(data)
    return schemas.ReportSummary(
        total_reports=total,
        pending=sum(1 for r in data if r.get("status") == schemas.ReportStatus.pending),
        under_review=sum(1 for r in data if r.get("status") == schemas.ReportStatus.under_review),
        resolved=sum(1 for r in data if r.get("status") == schemas.ReportStatus.resolved),
        dismissed=sum(1 for r in data if r.get("status") == schemas.ReportStatus.dismissed),
    )
