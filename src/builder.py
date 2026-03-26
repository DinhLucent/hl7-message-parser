"""
HL7 v2.x Message Builder — Fluent API for constructing HL7 messages.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from src.models import Message, Segment, Field


class MessageBuilder:
    """Fluent builder for constructing HL7 v2.x messages."""

    def __init__(self):
        self._segments: list[Segment] = []
        self._field_sep = "|"
        self._encoding = "^~\\&"

    def msh(
        self,
        sending_app: str = "APP",
        sending_facility: str = "FACILITY",
        receiving_app: str = "RECV",
        receiving_facility: str = "HOSPITAL",
        message_type: str = "ORU^R01",
        control_id: Optional[str] = None,
        processing_id: str = "P",
        version: str = "2.5",
        timestamp: Optional[str] = None,
    ) -> MessageBuilder:
        """Add MSH (Message Header) segment."""
        ts = timestamp or datetime.now().strftime("%Y%m%d%H%M%S")
        ctrl_id = control_id or f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}"

        fields = [
            Field(self._encoding),
            Field(sending_app),
            Field(sending_facility),
            Field(receiving_app),
            Field(receiving_facility),
            Field(ts),
            Field(""),  # MSH-8: Security
            Field(message_type),
            Field(ctrl_id),
            Field(processing_id),
            Field(version),
        ]

        raw = f"MSH{self._field_sep}{self._field_sep.join(f.value for f in fields)}"
        self._segments.append(Segment(segment_type="MSH", fields=fields, raw=raw))
        return self

    def pid(
        self,
        set_id: int = 1,
        patient_id: str = "",
        patient_name: str = "",
        dob: str = "",
        gender: str = "",
        address: str = "",
        phone: str = "",
    ) -> MessageBuilder:
        """Add PID (Patient Identification) segment."""
        fields = [
            Field(str(set_id)),
            Field(""),  # PID-2: External ID
            Field(f"{patient_id}^^^MRN"),
            Field(""),  # PID-4: Alternate ID
            Field(patient_name),
            Field(""),  # PID-6: Mother's Maiden Name
            Field(dob),
            Field(gender),
            Field(""),  # PID-9: Alias
            Field(""),  # PID-10: Race
            Field(address),
            Field(""),  # PID-12: County Code
            Field(phone),
        ]

        raw = f"PID{self._field_sep}{self._field_sep.join(f.value for f in fields)}"
        self._segments.append(Segment(segment_type="PID", fields=fields, raw=raw))
        return self

    def obx(
        self,
        set_id: int = 1,
        value_type: str = "NM",
        observation_id: str = "",
        value: str = "",
        units: str = "",
        reference_range: str = "",
        abnormal_flags: str = "N",
        result_status: str = "F",
    ) -> MessageBuilder:
        """Add OBX (Observation Result) segment."""
        fields = [
            Field(str(set_id)),
            Field(value_type),
            Field(observation_id),
            Field(""),  # OBX-4: Sub-ID
            Field(value),
            Field(units),
            Field(reference_range),
            Field(abnormal_flags),
            Field(""),  # OBX-9: Probability
            Field(""),  # OBX-10: Nature of Abnormal
            Field(result_status),
        ]

        raw = f"OBX{self._field_sep}{self._field_sep.join(f.value for f in fields)}"
        self._segments.append(Segment(segment_type="OBX", fields=fields, raw=raw))
        return self

    def orc(
        self,
        order_control: str = "NW",
        placer_order: str = "",
        filler_order: str = "",
    ) -> MessageBuilder:
        """Add ORC (Common Order) segment."""
        fields = [
            Field(order_control),
            Field(placer_order),
            Field(filler_order),
        ]

        raw = f"ORC{self._field_sep}{self._field_sep.join(f.value for f in fields)}"
        self._segments.append(Segment(segment_type="ORC", fields=fields, raw=raw))
        return self

    def custom_segment(self, segment_type: str, *field_values: str) -> MessageBuilder:
        """Add a custom segment with arbitrary fields."""
        fields = [Field(v) for v in field_values]
        raw = f"{segment_type}{self._field_sep}{self._field_sep.join(field_values)}"
        self._segments.append(Segment(segment_type=segment_type, fields=fields, raw=raw))
        return self

    def build(self) -> Message:
        """Build and return the complete Message object."""
        if not self._segments:
            raise ValueError("Cannot build empty message — add at least MSH segment")

        if self._segments[0].segment_type != "MSH":
            raise ValueError("First segment must be MSH")

        return Message(
            segments=self._segments,
            field_separator=self._field_sep,
            encoding_chars=self._encoding,
        )
