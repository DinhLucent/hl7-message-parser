"""
HL7 v2.x Message Parser — Converts raw HL7 strings to structured objects.
"""
from __future__ import annotations
from typing import Optional
from src.models import Message, Segment, Field


SEGMENT_DELIMITER = "\r"
DEFAULT_FIELD_SEPARATOR = "|"
DEFAULT_ENCODING_CHARS = "^~\\&"


def parse_message(raw: str) -> Message:
    """Parse a raw HL7 v2.x message string into a Message object.

    Args:
        raw: The raw HL7 message string. Segments can be separated by
             \\r, \\n, or \\r\\n.

    Returns:
        A Message object with parsed segments.

    Raises:
        ValueError: If the message doesn't start with 'MSH' or is empty.
    """
    if not raw or not raw.strip():
        raise ValueError("Empty HL7 message")

    # Normalize line endings → HL7 standard \r
    normalized = raw.strip().replace("\r\n", "\r").replace("\n", "\r")
    segment_lines = [line.strip() for line in normalized.split("\r") if line.strip()]

    if not segment_lines:
        raise ValueError("No segments found in message")

    if not segment_lines[0].startswith("MSH"):
        raise ValueError(f"Message must start with MSH segment, got: {segment_lines[0][:10]}")

    # Extract delimiters from MSH
    msh_line = segment_lines[0]
    field_separator = msh_line[3] if len(msh_line) > 3 else DEFAULT_FIELD_SEPARATOR
    encoding_chars = msh_line[4:8] if len(msh_line) > 7 else DEFAULT_ENCODING_CHARS

    # Parse each segment
    segments = []
    for line in segment_lines:
        segment = _parse_segment(line, field_separator)
        if segment:
            segments.append(segment)

    return Message(
        segments=segments,
        raw=raw,
        field_separator=field_separator,
        encoding_chars=encoding_chars,
    )


def _parse_segment(line: str, field_separator: str = "|") -> Optional[Segment]:
    """Parse a single segment line into a Segment object."""
    if not line or len(line) < 3:
        return None

    segment_type = line[:3]

    if segment_type == "MSH":
        # MSH is special: field separator is MSH[3], encoding chars are MSH[4:8]
        # We include encoding chars as the first parsed field (MSH-2)
        parts = line[4:].split(field_separator)
        fields = [Field(value=p) for p in parts]
    else:
        parts = line.split(field_separator)
        # First part is the segment type, rest are fields
        fields = [Field(value=p) for p in parts[1:]]

    return Segment(
        segment_type=segment_type,
        fields=fields,
        raw=line,
    )


def parse_field(field_value: str, component_separator: str = "^") -> list[str]:
    """Parse a field into its components."""
    return field_value.split(component_separator) if field_value else []
