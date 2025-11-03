"""Enumerations for database models."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Enum that serialises to its value."""

    def __str__(self) -> str:  # pragma: no cover - convenience
        return str(self.value)


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class RoleKey(StrEnum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    IT = "it"
    ADMIN = "admin"


class ControlType(StrEnum):
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    PHYSICAL = "physical"


class ContentType(StrEnum):
    VIDEO = "video"
    SCORM = "scorm"
    PDF = "pdf"
    QUIZ = "quiz"
    SIMULATION = "simulation"


class AssignmentStatus(StrEnum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class EventType(StrEnum):
    PHISH_FAIL = "phish_fail"
    POLICY_ACK = "policy_ack"
    LOGIN = "login"
    QUIZ_ATTEMPT = "quiz_attempt"
    CONTENT_VIEW = "content_view"


class ExportType(StrEnum):
    EMPLOYEES_CSV = "employees_csv"
    ASSIGNMENTS_CSV = "assignments_csv"
    EVIDENCE_ZIP = "evidence_zip"


class ExportStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PolicyStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


__all__ = [
    "UserStatus",
    "RoleKey",
    "ControlType",
    "ContentType",
    "AssignmentStatus",
    "EventType",
    "ExportType",
    "ExportStatus",
    "PolicyStatus",
    "StrEnum",
]
