from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EmploymentStatus, WorkforceType


class ManagerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    work_email: str


class EmployeeProfile(BaseModel):
    """Self-service profile returned by GET /me and get_my_profile tool."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    employee_code: str
    first_name: str
    last_name: str
    work_email: str
    phone: str | None = None
    hire_date: date
    employment_status: EmploymentStatus
    workforce_type: WorkforceType
    department: str | None = None
    job_title: str | None = None
    location: str | None = None
    manager: ManagerSummary | None = None


class DirectoryEntry(BaseModel):
    """Public directory fields for limited colleague lookup."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    work_email: str
    department: str | None = None
    job_title: str | None = None
    location: str | None = None
