from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee
from app.models.enums import ApprovalAction, LeaveRequestStatus
from app.models.leave import LeaveApproval, LeaveBalance, LeaveRequest, LeaveType
from app.schemas.leave import (
    ApplyLeaveIn,
    CancelLeaveOut,
    LeaveApprovalOut,
    LeaveBalanceOut,
    LeaveRequestDetail,
    LeaveRequestOut,
    LeaveTypeOut,
)
from app.services.employee import get_employee_by_id
from app.services.exceptions import (
    ForbiddenError,
    InsufficientLeaveBalance,
    InvalidLeaveState,
    NotFoundError,
    ValidationError,
)


def _calendar_days(start: date, end: date) -> Decimal:
    """Inclusive calendar days (matches seed examples: Sep 10–12 => 3)."""
    return Decimal((end - start).days + 1)


def _approver_name(approver: Employee | None) -> str | None:
    if approver is None:
        return None
    return f"{approver.first_name} {approver.last_name}"


def _to_leave_request_out(request: LeaveRequest) -> LeaveRequestOut:
    return LeaveRequestOut(
        id=request.id,
        leave_type_id=request.leave_type_id,
        leave_type_code=request.leave_type.code,
        leave_type_name=request.leave_type.name,
        start_date=request.start_date,
        end_date=request.end_date,
        days=request.days,
        reason=request.reason,
        status=request.status,
        approver_id=request.approver_id,
        approver_name=_approver_name(request.approver),
        decided_at=request.decided_at,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


def list_leave_types(db: Session, organization_id: UUID) -> list[LeaveTypeOut]:
    rows = db.scalars(
        select(LeaveType)
        .where(LeaveType.organization_id == organization_id)
        .order_by(LeaveType.code)
    ).all()
    return [LeaveTypeOut.model_validate(row) for row in rows]


def get_leave_balances(
    db: Session,
    employee_id: UUID,
    year: int | None = None,
) -> list[LeaveBalanceOut]:
    get_employee_by_id(db, employee_id)
    target_year = year or date.today().year

    rows = db.scalars(
        select(LeaveBalance)
        .where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == target_year,
        )
        .options(joinedload(LeaveBalance.leave_type))
        .order_by(LeaveBalance.leave_type_id)
    ).unique().all()

    return [
        LeaveBalanceOut(
            leave_type_id=row.leave_type_id,
            leave_type_code=row.leave_type.code,
            leave_type_name=row.leave_type.name,
            year=row.year,
            entitled=row.entitled,
            used=row.used,
            pending=row.pending,
            available=row.entitled - row.used - row.pending,
        )
        for row in rows
    ]


def list_leave_requests(
    db: Session,
    employee_id: UUID,
    status: LeaveRequestStatus | None = None,
) -> list[LeaveRequestOut]:
    get_employee_by_id(db, employee_id)

    stmt = (
        select(LeaveRequest)
        .where(LeaveRequest.employee_id == employee_id)
        .options(
            joinedload(LeaveRequest.leave_type),
            joinedload(LeaveRequest.approver),
        )
        .order_by(LeaveRequest.start_date.desc())
    )
    if status is not None:
        stmt = stmt.where(LeaveRequest.status == status)

    rows = db.scalars(stmt).unique().all()
    return [_to_leave_request_out(row) for row in rows]


def get_leave_request(
    db: Session,
    employee_id: UUID,
    request_id: UUID,
) -> LeaveRequestDetail:
    request = db.scalar(
        select(LeaveRequest)
        .where(LeaveRequest.id == request_id)
        .options(
            joinedload(LeaveRequest.leave_type),
            joinedload(LeaveRequest.approver),
            joinedload(LeaveRequest.approvals),
        )
    )
    if request is None:
        raise NotFoundError(f"Leave request not found: {request_id}")
    if request.employee_id != employee_id:
        raise ForbiddenError("You can only view your own leave requests")

    base = _to_leave_request_out(request)
    return LeaveRequestDetail(
        **base.model_dump(),
        approvals=[
            LeaveApprovalOut.model_validate(a)
            for a in sorted(request.approvals, key=lambda x: x.acted_at)
        ],
    )


def _get_leave_type(
    db: Session,
    organization_id: UUID,
    code: str,
) -> LeaveType:
    leave_type = db.scalar(
        select(LeaveType).where(
            LeaveType.organization_id == organization_id,
            LeaveType.code == code,
        )
    )
    if leave_type is None:
        raise NotFoundError(f"Leave type not found: {code}")
    return leave_type


def _get_or_create_balance(
    db: Session,
    employee_id: UUID,
    leave_type: LeaveType,
    year: int,
) -> LeaveBalance:
    balance = db.scalar(
        select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type.id,
            LeaveBalance.year == year,
        )
    )
    if balance is not None:
        return balance

    balance = LeaveBalance(
        employee_id=employee_id,
        leave_type_id=leave_type.id,
        year=year,
        entitled=leave_type.annual_quota or Decimal("0"),
        used=Decimal("0"),
        pending=Decimal("0"),
    )
    db.add(balance)
    db.flush()
    return balance


def apply_leave(
    db: Session,
    employee_id: UUID,
    payload: ApplyLeaveIn,
) -> LeaveRequestOut:
    employee = get_employee_by_id(db, employee_id)
    leave_type = _get_leave_type(db, employee.organization_id, payload.leave_type_code)
    days = _calendar_days(payload.start_date, payload.end_date)
    year = payload.start_date.year

    balance = _get_or_create_balance(db, employee.id, leave_type, year)
    available = balance.entitled - balance.used - balance.pending
    if days > available:
        raise InsufficientLeaveBalance(
            f"Insufficient {leave_type.code} balance: need {days}, available {available}"
        )

    now = datetime.now(timezone.utc)
    request = LeaveRequest(
        employee_id=employee.id,
        leave_type_id=leave_type.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days=days,
        reason=payload.reason,
        status=LeaveRequestStatus.pending,
        approver_id=employee.manager_id,
        created_at=now,
        updated_at=now,
    )
    db.add(request)
    db.flush()

    balance.pending = balance.pending + days
    db.add(
        LeaveApproval(
            leave_request_id=request.id,
            actor_employee_id=employee.id,
            action=ApprovalAction.submitted,
            comments=None,
        )
    )
    db.commit()

    # Reload with relationships for response mapping
    loaded = db.scalar(
        select(LeaveRequest)
        .where(LeaveRequest.id == request.id)
        .options(
            joinedload(LeaveRequest.leave_type),
            joinedload(LeaveRequest.approver),
        )
    )
    assert loaded is not None
    return _to_leave_request_out(loaded)


def cancel_leave_request(
    db: Session,
    employee_id: UUID,
    request_id: UUID,
) -> CancelLeaveOut:
    get_employee_by_id(db, employee_id)

    request = db.scalar(
        select(LeaveRequest)
        .where(LeaveRequest.id == request_id)
        .options(joinedload(LeaveRequest.leave_type))
    )
    if request is None:
        raise NotFoundError(f"Leave request not found: {request_id}")
    if request.employee_id != employee_id:
        raise ForbiddenError("You can only cancel your own leave requests")
    if request.status != LeaveRequestStatus.pending:
        raise InvalidLeaveState(
            f"Only pending requests can be cancelled (current: {request.status.value})"
        )

    balance = db.scalar(
        select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == request.leave_type_id,
            LeaveBalance.year == request.start_date.year,
        )
    )
    if balance is None:
        raise ValidationError("Leave balance row missing for this request year")

    now = datetime.now(timezone.utc)
    request.status = LeaveRequestStatus.cancelled
    request.updated_at = now
    balance.pending = max(Decimal("0"), balance.pending - request.days)

    db.add(
        LeaveApproval(
            leave_request_id=request.id,
            actor_employee_id=employee_id,
            action=ApprovalAction.cancelled,
            comments="Cancelled by employee",
        )
    )
    db.commit()

    return CancelLeaveOut(id=request.id, status=request.status)
