"""Employee agent tools — profile + leave.

Tools are built per request so employee_id/db come from the session,
not from the LLM.
"""

from __future__ import annotations

import json
from datetime import date
from uuid import UUID

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.models.enums import LeaveRequestStatus
from app.schemas.leave import ApplyLeaveIn
from app.services.employee import get_manager, get_profile
from app.services.exceptions import HRMSError
from app.services.leave import (
    apply_leave,
    cancel_leave_request,
    get_leave_balances,
    get_leave_request,
    list_leave_requests,
    list_leave_types,
)


def _json_error(exc: Exception) -> str:
    if isinstance(exc, HRMSError):
        return json.dumps({"error": exc.message})
    return json.dumps({"error": str(exc)})


def build_profile_tools(db: Session, employee_id: UUID) -> list[StructuredTool]:
    """Create profile tools closed over the authenticated employee."""

    def get_my_profile() -> str:
        """Get the authenticated employee's profile.

        Returns name, employee code, department, job title, location,
        employment status, and manager summary.
        Use when the user asks who they are, their department, title, or profile.
        """
        try:
            return get_profile(db, employee_id).model_dump_json()
        except Exception as exc:
            return _json_error(exc)

    def get_my_manager() -> str:
        """Get the authenticated employee's manager.

        Returns manager name, employee code, and work email.
        Use when the user asks who their manager is or who approves leave.
        """
        try:
            manager = get_manager(db, employee_id)
            if manager is None:
                return json.dumps({"manager": None, "message": "No manager assigned"})
            return manager.model_dump_json()
        except Exception as exc:
            return _json_error(exc)

    return [
        StructuredTool.from_function(
            func=get_my_profile,
            name="get_my_profile",
            description=get_my_profile.__doc__,
        ),
        StructuredTool.from_function(
            func=get_my_manager,
            name="get_my_manager",
            description=get_my_manager.__doc__,
        ),
    ]


def build_leave_tools(
    db: Session,
    employee_id: UUID,
    organization_id: UUID,
) -> list[StructuredTool]:
    """Create leave tools closed over the authenticated employee."""

    def list_leave_types_tool() -> str:
        """List available leave types for the organization (code, name, quota).

        Use to map names like casual leave to codes such as CL, AL, SL, UL.
        """
        try:
            rows = list_leave_types(db, organization_id)
            return json.dumps([r.model_dump(mode="json") for r in rows])
        except Exception as exc:
            return _json_error(exc)

    def get_leave_balances_tool(year: int | None = None) -> str:
        """Get the authenticated employee's leave balances.

        Args:
            year: Optional calendar year (defaults to current year).
        """
        try:
            rows = get_leave_balances(db, employee_id, year)
            return json.dumps([r.model_dump(mode="json") for r in rows])
        except Exception as exc:
            return _json_error(exc)

    def list_my_leave_requests_tool(status: str | None = None) -> str:
        """List the authenticated employee's leave requests.

        Args:
            status: Optional filter: draft, pending, approved, rejected, cancelled.
        """
        try:
            status_enum = LeaveRequestStatus(status) if status else None
            rows = list_leave_requests(db, employee_id, status_enum)
            return json.dumps([r.model_dump(mode="json") for r in rows])
        except Exception as exc:
            return _json_error(exc)

    def get_leave_request_tool(request_id: str) -> str:
        """Get one leave request detail including approval history.

        Args:
            request_id: Leave request UUID string.
        """
        try:
            detail = get_leave_request(db, employee_id, UUID(request_id))
            return detail.model_dump_json()
        except Exception as exc:
            return _json_error(exc)

    def apply_leave_tool(
        leave_type_code: str,
        start_date: str,
        end_date: str,
        reason: str | None = None,
    ) -> str:
        """Apply leave for the authenticated employee.

        Args:
            leave_type_code: Leave code such as CL, AL, SL, UL.
            start_date: Start date in YYYY-MM-DD.
            end_date: End date in YYYY-MM-DD.
            reason: Optional reason text.
        """
        try:
            payload = ApplyLeaveIn(
                leave_type_code=leave_type_code,
                start_date=date.fromisoformat(start_date),
                end_date=date.fromisoformat(end_date),
                reason=reason,
            )
            created = apply_leave(db, employee_id, payload)
            return created.model_dump_json()
        except Exception as exc:
            return _json_error(exc)

    def cancel_leave_request_tool(request_id: str) -> str:
        """Cancel a pending leave request owned by the authenticated employee.

        Args:
            request_id: Leave request UUID string.
        """
        try:
            result = cancel_leave_request(db, employee_id, UUID(request_id))
            return result.model_dump_json()
        except Exception as exc:
            return _json_error(exc)

    return [
        StructuredTool.from_function(
            func=list_leave_types_tool,
            name="list_leave_types",
            description=list_leave_types_tool.__doc__,
        ),
        StructuredTool.from_function(
            func=get_leave_balances_tool,
            name="get_leave_balances",
            description=get_leave_balances_tool.__doc__,
        ),
        StructuredTool.from_function(
            func=list_my_leave_requests_tool,
            name="list_my_leave_requests",
            description=list_my_leave_requests_tool.__doc__,
        ),
        StructuredTool.from_function(
            func=get_leave_request_tool,
            name="get_leave_request",
            description=get_leave_request_tool.__doc__,
        ),
        StructuredTool.from_function(
            func=apply_leave_tool,
            name="apply_leave",
            description=apply_leave_tool.__doc__,
        ),
        StructuredTool.from_function(
            func=cancel_leave_request_tool,
            name="cancel_leave_request",
            description=cancel_leave_request_tool.__doc__,
        ),
    ]


def build_employee_tools(
    db: Session,
    employee_id: UUID,
    organization_id: UUID,
) -> list[StructuredTool]:
    """All Employee agent tools for the current session."""
    return [
        *build_profile_tools(db, employee_id),
        *build_leave_tools(db, employee_id, organization_id),
    ]
