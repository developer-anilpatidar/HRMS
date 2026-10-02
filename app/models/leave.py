import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ApprovalAction, LeaveRequestStatus

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.organization import Organization


class LeaveType(Base):
    __tablename__ = "leave_types"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    requires_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    annual_quota: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))

    organization: Mapped["Organization"] = relationship()
    balances: Mapped[list["LeaveBalance"]] = relationship(back_populates="leave_type")
    requests: Mapped[list["LeaveRequest"]] = relationship(back_populates="leave_type")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("employee_id", "leave_type_id", "year"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    leave_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    entitled: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False, server_default="0")
    used: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False, server_default="0")
    pending: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False, server_default="0")

    employee: Mapped["Employee"] = relationship(back_populates="leave_balances")
    leave_type: Mapped["LeaveType"] = relationship(back_populates="balances")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    __table_args__ = (CheckConstraint("end_date >= start_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True
    )
    leave_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[LeaveRequestStatus] = mapped_column(
        Enum(
            LeaveRequestStatus,
            name="leave_request_status",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=LeaveRequestStatus.pending.value,
        index=True,
    )
    approver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id")
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="leave_requests",
        foreign_keys=[employee_id],
    )
    leave_type: Mapped["LeaveType"] = relationship(back_populates="requests")
    approver: Mapped["Employee | None"] = relationship(foreign_keys=[approver_id])
    approvals: Mapped[list["LeaveApproval"]] = relationship(
        back_populates="leave_request",
        cascade="all, delete-orphan",
    )


class LeaveApproval(Base):
    __tablename__ = "leave_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    leave_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    action: Mapped[ApprovalAction] = mapped_column(
        Enum(
            ApprovalAction,
            name="approval_action",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    comments: Mapped[str | None] = mapped_column(Text)
    acted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    leave_request: Mapped["LeaveRequest"] = relationship(back_populates="approvals")
    actor: Mapped["Employee"] = relationship(foreign_keys=[actor_employee_id])
