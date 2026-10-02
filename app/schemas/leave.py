from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import ApprovalAction, LeaveRequestStatus


class LeaveTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    is_paid: bool
    requires_approval: bool
    annual_quota: Decimal | None = None


class LeaveBalanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leave_type_id: UUID
    leave_type_code: str
    leave_type_name: str
    year: int
    entitled: Decimal
    used: Decimal
    pending: Decimal
    available: Decimal = Field(
        description="entitled - used - pending",
    )


class ApplyLeaveIn(BaseModel):
    leave_type_code: str = Field(..., min_length=1, max_length=32, examples=["CL"])
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("leave_type_code")
    @classmethod
    def normalize_leave_type_code(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_date_range(self) -> "ApplyLeaveIn":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class LeaveApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    action: ApprovalAction
    comments: str | None = None
    acted_at: datetime
    actor_employee_id: UUID


class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leave_type_id: UUID
    leave_type_code: str
    leave_type_name: str
    start_date: date
    end_date: date
    days: Decimal
    reason: str | None = None
    status: LeaveRequestStatus
    approver_id: UUID | None = None
    approver_name: str | None = None
    decided_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class LeaveRequestDetail(LeaveRequestOut):
    approvals: list[LeaveApprovalOut] = Field(default_factory=list)


class CancelLeaveOut(BaseModel):
    id: UUID
    status: LeaveRequestStatus
    message: str = "Leave request cancelled"
