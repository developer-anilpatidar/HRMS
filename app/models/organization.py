import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.types import CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255))
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False, server_default="IN")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="Asia/Kolkata")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    locations: Mapped[list["Location"]] = relationship(back_populates="organization")
    departments: Mapped[list["Department"]] = relationship(back_populates="organization")
    job_titles: Mapped[list["JobTitle"]] = relationship(back_populates="organization")
    employees: Mapped[list["Employee"]] = relationship(back_populates="organization")


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(80))
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False, server_default="IN")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    organization: Mapped["Organization"] = relationship(back_populates="locations")


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id")
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    organization: Mapped["Organization"] = relationship(back_populates="departments")
    parent: Mapped["Department | None"] = relationship(remote_side="Department.id")


class JobTitle(Base):
    __tablename__ = "job_titles"
    __table_args__ = (UniqueConstraint("organization_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(32))

    organization: Mapped["Organization"] = relationship(back_populates="job_titles")
