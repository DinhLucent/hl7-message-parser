"""
HL7 Message Validator — Checks message integrity and required fields.
"""
from __future__ import annotations
from typing import Optional
from src.models import Message


class ValidationError:
    """Represents a single validation issue."""

    def __init__(self, level: str, segment: str, field: int, message: str):
        self.level = level        # "error" or "warning"
        self.segment = segment
        self.field = field
        self.message = message

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.segment}-{self.field}: {self.message}"


class ValidationResult:
    """Result of validating an HL7 message."""

    def __init__(self):
        self.errors: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return not any(e.level == "error" for e in self.errors)

    @property
    def error_count(self) -> int:
        return sum(1 for e in self.errors if e.level == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for e in self.errors if e.level == "warning")

    def add_error(self, segment: str, field: int, message: str):
        self.errors.append(ValidationError("error", segment, field, message))

    def add_warning(self, segment: str, field: int, message: str):
        self.errors.append(ValidationError("warning", segment, field, message))

    def __str__(self) -> str:
        if self.is_valid:
            return f"✅ Valid ({self.warning_count} warnings)"
        return f"❌ Invalid ({self.error_count} errors, {self.warning_count} warnings)"


# Required fields: (segment_type, field_index, description)
REQUIRED_FIELDS = [
    ("MSH", 9, "Message Type"),
    ("MSH", 10, "Message Control ID"),
    ("MSH", 12, "Version ID"),
]

PID_REQUIRED_FOR_CLINICAL = [
    ("PID", 3, "Patient ID"),
    ("PID", 5, "Patient Name"),
]


def validate_message(
    msg: Message,
    require_pid: bool = False,
    strict: bool = False,
) -> ValidationResult:
    """Validate an HL7 message for integrity and required fields.

    Args:
        msg: The Message object to validate.
        require_pid: If True, PID segment and its fields are required.
        strict: If True, warnings about recommended fields become errors.

    Returns:
        A ValidationResult object.
    """
    result = ValidationResult()

    # Must have MSH
    msh = msg.get_segment("MSH")
    if not msh:
        result.add_error("MSH", 0, "MSH segment is required")
        return result

    # Check required MSH fields
    for seg_type, field_idx, desc in REQUIRED_FIELDS:
        seg = msg.get_segment(seg_type)
        if seg and not seg.get_field(field_idx):
            result.add_error(seg_type, field_idx, f"{desc} is required")

    # Version check
    version = msh.get_field(12)
    if version and not version.startswith("2."):
        result.add_warning("MSH", 12, f"Unexpected HL7 version: {version}")

    # PID validation
    if require_pid:
        pid = msg.get_segment("PID")
        if not pid:
            result.add_error("PID", 0, "PID segment is required for clinical messages")
        else:
            for seg_type, field_idx, desc in PID_REQUIRED_FOR_CLINICAL:
                if not pid.get_field(field_idx):
                    level = "error" if strict else "warning"
                    if level == "error":
                        result.add_error(seg_type, field_idx, f"{desc} is recommended")
                    else:
                        result.add_warning(seg_type, field_idx, f"{desc} is recommended")

    # OBX validation
    for obx in msg.get_segments("OBX"):
        if not obx.get_field(3):
            result.add_warning("OBX", 3, "Observation Identifier is recommended")
        if not obx.get_field(11):
            result.add_warning("OBX", 11, "Result Status should be set (F/P/C)")

    return result
