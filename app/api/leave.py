from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentEmployee, CurrentEmployeeId, DbSession
from app.models.enums import LeaveRequestStatus
from app.schemas.leave import (
    ApplyLeaveIn,
    CancelLeaveOut,
    LeaveBalanceOut,
    LeaveRequestDetail,
    LeaveRequestOut,
    LeaveTypeOut,
)
from app.services.exceptions import (
    ForbiddenError,
    HRMSError,
    NotFoundError,
    ValidationError,
)
from app.services.leave import (
    apply_leave,
    cancel_leave_request,
    get_leave_balances,
    get_leave_request,
    list_leave_requests,
    list_leave_types,
)

router = APIRouter(prefix="/leave", tags=["leave"])


def _http_error(exc: HRMSError) -> HTTPException:
    if isinstance(exc, NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ForbiddenError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValidationError):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=exc.message)


@router.get("/types", response_model=list[LeaveTypeOut])
def read_leave_types(db: DbSession, employee: CurrentEmployee) -> list[LeaveTypeOut]:
    return list_leave_types(db, employee.organization_id)


@router.get("/balances", response_model=list[LeaveBalanceOut])
def read_leave_balances(
    db: DbSession,
    employee_id: CurrentEmployeeId,
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> list[LeaveBalanceOut]:
    return get_leave_balances(db, employee_id, year or date.today().year)


@router.get("/requests", response_model=list[LeaveRequestOut])
def read_leave_requests(
    db: DbSession,
    employee_id: CurrentEmployeeId,
    status_filter: LeaveRequestStatus | None = Query(
        default=None,
        alias="status",
        description="Optional status filter",
    ),
) -> list[LeaveRequestOut]:
    return list_leave_requests(db, employee_id, status_filter)


@router.get("/requests/{request_id}", response_model=LeaveRequestDetail)
def read_leave_request(
    request_id: UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LeaveRequestDetail:
    try:
        return get_leave_request(db, employee_id, request_id)
    except HRMSError as exc:
        raise _http_error(exc) from exc


@router.post(
    "/requests",
    response_model=LeaveRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_leave_request(
    payload: ApplyLeaveIn,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> LeaveRequestOut:
    try:
        return apply_leave(db, employee_id, payload)
    except HRMSError as exc:
        raise _http_error(exc) from exc


@router.post("/requests/{request_id}/cancel", response_model=CancelLeaveOut)
def cancel_request(
    request_id: UUID,
    db: DbSession,
    employee_id: CurrentEmployeeId,
) -> CancelLeaveOut:
    try:
        return cancel_leave_request(db, employee_id, request_id)
    except HRMSError as exc:
        raise _http_error(exc) from exc
