from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee
from app.schemas.employee import DirectoryEntry, EmployeeProfile, ManagerSummary
from app.services.exceptions import NotFoundError


def get_employee_by_id(db: Session, employee_id: UUID) -> Employee:
    employee = db.scalar(
        select(Employee)
        .where(Employee.id == employee_id)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.job_title),
            joinedload(Employee.location),
            joinedload(Employee.manager),
        )
    )
    if employee is None:
        raise NotFoundError(f"Employee not found: {employee_id}")
    return employee


def get_employee_by_email(db: Session, work_email: str) -> Employee:
    employee = db.scalar(
        select(Employee)
        .where(Employee.work_email == work_email.strip().lower())
        .options(
            joinedload(Employee.department),
            joinedload(Employee.job_title),
            joinedload(Employee.location),
            joinedload(Employee.manager),
        )
    )
    if employee is None:
        raise NotFoundError(f"Employee not found for email: {work_email}")
    return employee


def _to_manager_summary(manager: Employee | None) -> ManagerSummary | None:
    if manager is None:
        return None
    return ManagerSummary.model_validate(manager)


def get_profile(db: Session, employee_id: UUID) -> EmployeeProfile:
    employee = get_employee_by_id(db, employee_id)
    return EmployeeProfile(
        id=employee.id,
        organization_id=employee.organization_id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
        work_email=employee.work_email,
        phone=employee.phone,
        hire_date=employee.hire_date,
        employment_status=employee.employment_status,
        workforce_type=employee.workforce_type,
        department=employee.department.name if employee.department else None,
        job_title=employee.job_title.title if employee.job_title else None,
        location=employee.location.name if employee.location else None,
        manager=_to_manager_summary(employee.manager),
    )


def get_manager(db: Session, employee_id: UUID) -> ManagerSummary | None:
    employee = get_employee_by_id(db, employee_id)
    return _to_manager_summary(employee.manager)


def lookup_directory(
    db: Session,
    organization_id: UUID,
    query: str,
    *,
    limit: int = 10,
) -> list[DirectoryEntry]:
    """Public directory search within one org (name, code, or email)."""
    q = query.strip()
    if not q:
        return []

    pattern = f"%{q}%"
    rows = db.scalars(
        select(Employee)
        .where(Employee.organization_id == organization_id)
        .where(
            or_(
                Employee.first_name.ilike(pattern),
                Employee.last_name.ilike(pattern),
                Employee.employee_code.ilike(pattern),
                Employee.work_email.ilike(pattern),
            )
        )
        .options(
            joinedload(Employee.department),
            joinedload(Employee.job_title),
            joinedload(Employee.location),
        )
        .order_by(Employee.first_name, Employee.last_name)
        .limit(limit)
    ).unique().all()

    return [
        DirectoryEntry(
            id=e.id,
            employee_code=e.employee_code,
            first_name=e.first_name,
            last_name=e.last_name,
            work_email=e.work_email,
            department=e.department.name if e.department else None,
            job_title=e.job_title.title if e.job_title else None,
            location=e.location.name if e.location else None,
        )
        for e in rows
    ]
