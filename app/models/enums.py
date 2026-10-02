import enum


class EmploymentStatus(str, enum.Enum):
    active = "active"
    probation = "probation"
    on_notice = "on_notice"
    terminated = "terminated"
    on_leave = "on_leave"


class WorkforceType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    intern = "intern"


class LeaveRequestStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class ApprovalAction(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
