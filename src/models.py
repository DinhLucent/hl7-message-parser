"""
HL7 v2.x Data Models — Message, Segment, and Field representations.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Field:
    """Represents a single HL7 field (or component)."""
    value: str = ""

    @property
    def components(self) -> list[str]:
        """Split field into components using '^' delimiter."""
        return self.value.split("^") if self.value else []

    @property
    def subcomponents(self) -> list[str]:
        """Split field into subcomponents using '&' delimiter."""
        return self.value.split("&") if self.value else []

    def __str__(self) -> str:
        return self.value

    def __bool__(self) -> bool:
        return bool(self.value)


@dataclass
class Segment:
    """Represents an HL7 segment (e.g., MSH, PID, OBX)."""
    segment_type: str
    fields: list[Field] = field(default_factory=list)
    raw: str = ""

    def get_field(self, index: int) -> str:
        """Get field value by 1-based index (HL7 convention).
        
        For MSH: field 1 = '|' (separator), field 2 = encoding chars = fields[0],
                 field N (N>=2) = fields[N-2]
        For others: field N = fields[N-1]
        """
        if self.segment_type == "MSH":
            if index == 1:
                return "|"
            idx = index - 2  # MSH-2 = fields[0], MSH-3 = fields[1], etc.
        else:
            idx = index - 1  # PID-1 = fields[0], PID-2 = fields[1], etc.

        if 0 <= idx < len(self.fields):
            return self.fields[idx].value
        return ""

    def get_component(self, field_index: int, component_index: int = 0) -> str:
        """Get a specific component from a field."""
        field_val = self.get_field(field_index)
        parts = field_val.split("^")
        if 0 <= component_index < len(parts):
            return parts[component_index]
        return ""

    @property
    def segment_id(self) -> str:
        return self.segment_type

    # ── MSH convenience properties ──
    @property
    def sending_application(self) -> str:
        return self.get_field(3) if self.segment_type == "MSH" else ""

    @property
    def receiving_application(self) -> str:
        return self.get_field(5) if self.segment_type == "MSH" else ""

    @property
    def message_type(self) -> str:
        return self.get_component(9, 0) if self.segment_type == "MSH" else ""

    @property
    def trigger_event(self) -> str:
        return self.get_component(9, 1) if self.segment_type == "MSH" else ""

    @property
    def message_control_id(self) -> str:
        return self.get_field(10) if self.segment_type == "MSH" else ""

    @property
    def version_id(self) -> str:
        return self.get_field(12) if self.segment_type == "MSH" else ""

    # ── PID convenience properties ──
    @property
    def patient_id(self) -> str:
        return self.get_component(3, 0) if self.segment_type == "PID" else ""

    @property
    def patient_name(self) -> str:
        return self.get_field(5) if self.segment_type == "PID" else ""

    @property
    def date_of_birth(self) -> str:
        return self.get_field(7) if self.segment_type == "PID" else ""

    @property
    def gender(self) -> str:
        return self.get_field(8) if self.segment_type == "PID" else ""

    # ── OBX convenience properties ──
    @property
    def observation_id(self) -> str:
        return self.get_component(3, 0) if self.segment_type == "OBX" else ""

    @property
    def value(self) -> str:
        return self.get_field(5) if self.segment_type == "OBX" else ""

    @property
    def units(self) -> str:
        return self.get_field(6) if self.segment_type == "OBX" else ""

    @property
    def reference_range(self) -> str:
        return self.get_field(7) if self.segment_type == "OBX" else ""

    @property
    def result_status(self) -> str:
        return self.get_field(11) if self.segment_type == "OBX" else ""

    def __str__(self) -> str:
        return self.raw or f"{self.segment_type}|{'|'.join(str(f) for f in self.fields)}"


@dataclass
class Message:
    """Represents a complete HL7 v2.x message."""
    segments: list[Segment] = field(default_factory=list)
    raw: str = ""
    field_separator: str = "|"
    encoding_chars: str = "^~\\&"

    def get_segment(self, segment_type: str) -> Optional[Segment]:
        """Get the first segment of a given type."""
        for seg in self.segments:
            if seg.segment_type == segment_type:
                return seg
        return None

    def get_segments(self, segment_type: str) -> list[Segment]:
        """Get all segments of a given type."""
        return [s for s in self.segments if s.segment_type == segment_type]

    @property
    def msh(self) -> Optional[Segment]:
        return self.get_segment("MSH")

    @property
    def pid(self) -> Optional[Segment]:
        return self.get_segment("PID")

    @property
    def segment_types(self) -> list[str]:
        """List all segment types in order."""
        return [s.segment_type for s in self.segments]

    @property
    def message_type(self) -> str:
        msh = self.msh
        return msh.message_type if msh else ""

    @property
    def trigger_event(self) -> str:
        msh = self.msh
        return msh.trigger_event if msh else ""

    def to_hl7(self) -> str:
        """Convert back to raw HL7 string with \\r segment delimiters."""
        return "\r".join(str(seg) for seg in self.segments)

    def to_dict(self) -> dict:
        """Convert message to a dictionary representation."""
        result = {}
        for seg in self.segments:
            key = seg.segment_type
            entry = {f"field_{i}": f.value for i, f in enumerate(seg.fields)}
            if key in result:
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(entry)
            else:
                result[key] = entry
        return result

    def __len__(self) -> int:
        return len(self.segments)

    def __str__(self) -> str:
        return self.to_hl7()
