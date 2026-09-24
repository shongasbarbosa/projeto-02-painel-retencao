"""Schemas Pydantic usados nos endpoints (request/response)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.models import ContactOutcome, EnrollmentStatus
from app.services.risk_score import RiskLevel


# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Courses ---
class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str


# --- Enrollments ---
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    enrolled_at: datetime | None = None


class EnrollmentStatusUpdate(BaseModel):
    status: EnrollmentStatus


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    last_access_at: datetime | None
    completed_at: datetime | None


# --- Reports ---
class FunnelReport(BaseModel):
    matriculados: int
    ativos: int
    em_risco: int
    desistentes: int
    concluintes: int
    taxa_evasao: float


class RiskScoreItem(BaseModel):
    enrollment_id: int
    student_id: int
    student_name: str
    course_id: int
    course_name: str
    days_inactive: int
    submission_rate: float
    score: float
    level: RiskLevel


class ComparisonItem(BaseModel):
    course_id: int
    course_name: str
    funnel: FunnelReport


# --- Contact logs ---
class ContactLogCreate(BaseModel):
    course_id: int
    outcome: ContactOutcome
    notes: str | None = None


class ContactLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    contacted_at: datetime
    outcome: ContactOutcome
    notes: str | None


class HealthOut(BaseModel):
    status: str = Field(default="ok")
