"""Employee agent tools — profile-related (leave tools come later).

Tools are built per request so employee_id/db come from the session,
not from the LLM.
"""

from __future__ import annotations

import json
from uuid import UUID

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.services.employee import get_manager, get_profile
from app.services.exceptions import HRMSError


def build_profile_tools(db: Session, employee_id: UUID) -> list[StructuredTool]:
    """Create profile tools closed over the authenticated employee."""

    def get_my_profile() -> str:
        """Get the authenticated employee's profile.

        Returns name, employee code, department, job title, location,
        employment status, and manager summary.
        Use when the user asks who they are, their department, title, or profile.
        """
        try:
            profile = get_profile(db, employee_id)
            return profile.model_dump_json()
        except HRMSError as exc:
            return json.dumps({"error": exc.message})

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
        except HRMSError as exc:
            return json.dumps({"error": exc.message})

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
