import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EmploymentStatus, WorkforceType

if TYPE_CHECKING:
    from app.models.leave import LeaveBalance, LeaveRequest
    from app.models.organization import Department, JobTitle, Location, Organization


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("organization_id", "email"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    employee: Mapped["Employee | None"] = relationship(back_populates="user", uselist=False)


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_code"),
        UniqueConstraint("organization_id", "work_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    employee_code: Mapped[str] = mapped_column(String(32), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    work_email: Mapped[str] = mapped_column(String(255), nullable=False)
    personal_email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(32))
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[date | None] = mapped_column(Date)
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(
            EmploymentStatus,
            name="employment_status",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=EmploymentStatus.active.value,
    )
    workforce_type: Mapped[WorkforceType] = mapped_column(
        Enum(
            WorkforceType,
            name="workforce_type",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default=WorkforceType.full_time.value,
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), index=True
    )
    job_title_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_titles.id")
    )
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="employees")
    user: Mapped["User | None"] = relationship(back_populates="employee")
    location: Mapped["Location | None"] = relationship()
    department: Mapped["Department | None"] = relationship()
    job_title: Mapped["JobTitle | None"] = relationship()
    manager: Mapped["Employee | None"] = relationship(
        remote_side="Employee.id",
        foreign_keys=[manager_id],
        back_populates="direct_reports",
    )
    direct_reports: Mapped[list["Employee"]] = relationship(
        back_populates="manager",
        foreign_keys=[manager_id],
    )
    leave_balances: Mapped[list["LeaveBalance"]] = relationship(back_populates="employee")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="employee",
        foreign_keys="LeaveRequest.employee_id",
    )
