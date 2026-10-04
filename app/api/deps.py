import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.employee import Employee
from app.services.employee import get_employee_by_email
from app.services.exceptions import NotFoundError

# Demo default: Neha Verma (override with X-Employee-Email or DEMO_EMPLOYEE_EMAIL)
DEFAULT_EMPLOYEE_EMAIL = os.getenv(
    "DEMO_EMPLOYEE_EMAIL",
    "neha.verma@novatech.example",
)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_employee(
    db: DbSession,
    x_employee_email: Annotated[
        str | None,
        Header(
            description="Demo identity. Defaults to Neha if omitted.",
            examples=["neha.verma@novatech.example"],
        ),
    ] = None,
) -> Employee:
    """Resolve the acting employee for self-service endpoints.

    Production will replace this with JWT / session auth.
    """
    email = (x_employee_email or DEFAULT_EMPLOYEE_EMAIL).strip().lower()
    try:
        return get_employee_by_email(db, email)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc


def get_current_employee_id(
    employee: Annotated[Employee, Depends(get_current_employee)],
) -> UUID:
    return employee.id


CurrentEmployee = Annotated[Employee, Depends(get_current_employee)]
CurrentEmployeeId = Annotated[UUID, Depends(get_current_employee_id)]
