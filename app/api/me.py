from fastapi import APIRouter

from app.api.deps import CurrentEmployeeId, DbSession
from app.schemas.employee import EmployeeProfile
from app.services.employee import get_profile

router = APIRouter(tags=["me"])


@router.get("/me", response_model=EmployeeProfile)
def read_me(db: DbSession, employee_id: CurrentEmployeeId) -> EmployeeProfile:
    """Return the authenticated (demo) employee's profile."""
    return get_profile(db, employee_id)
