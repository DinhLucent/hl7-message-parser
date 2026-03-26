"""
Tests for HL7 Message Parser.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import parse_message
from src.builder import MessageBuilder
from src.validators import validate_message
from src.models import Message, Segment, Field


# ── Sample HL7 Messages ──

SAMPLE_ORU = (
    "MSH|^~\\&|LAB|FACILITY|EHR|HOSPITAL|20240101120000||ORU^R01|MSG001|P|2.5\r"
    "PID|1||12345^^^MRN||DOE^JOHN||19800101|M\r"
    "OBX|1|NM|GLU^Glucose||95|mg/dL|70-100|N|||F\r"
    "OBX|2|NM|HGB^Hemoglobin||14.2|g/dL|12-17|N|||F"
)

SAMPLE_MINIMAL = "MSH|^~\\&|APP|FAC|RECV|HOSP|20240101||ACK|MSG002|P|2.5"


class TestParser:
    """Tests for the HL7 parser."""

    def test_parse_basic_message(self):
        msg = parse_message(SAMPLE_ORU)
        assert isinstance(msg, Message)
        assert len(msg.segments) == 4

    def test_parse_segment_types(self):
        msg = parse_message(SAMPLE_ORU)
        assert msg.segment_types == ["MSH", "PID", "OBX", "OBX"]

    def test_parse_msh_fields(self):
        msg = parse_message(SAMPLE_ORU)
        msh = msg.get_segment("MSH")
        assert msh is not None
        assert msh.message_type == "ORU"
        assert msh.trigger_event == "R01"
        assert msh.message_control_id == "MSG001"
        assert msh.version_id == "2.5"

    def test_parse_pid_fields(self):
        msg = parse_message(SAMPLE_ORU)
        pid = msg.get_segment("PID")
        assert pid is not None
        assert pid.patient_id == "12345"
        assert pid.patient_name == "DOE^JOHN"
        assert pid.date_of_birth == "19800101"
        assert pid.gender == "M"

    def test_parse_obx_fields(self):
        msg = parse_message(SAMPLE_ORU)
        obx_list = msg.get_segments("OBX")
        assert len(obx_list) == 2
        assert obx_list[0].observation_id == "GLU"
        assert obx_list[0].value == "95"
        assert obx_list[0].units == "mg/dL"
        assert obx_list[1].observation_id == "HGB"

    def test_parse_minimal_message(self):
        msg = parse_message(SAMPLE_MINIMAL)
        assert len(msg.segments) == 1
        assert msg.message_type == "ACK"

    def test_parse_newline_delimiters(self):
        raw = SAMPLE_ORU.replace("\r", "\n")
        msg = parse_message(raw)
        assert len(msg.segments) == 4

    def test_parse_empty_raises(self):
        with pytest.raises(ValueError, match="Empty"):
            parse_message("")

    def test_parse_no_msh_raises(self):
        with pytest.raises(ValueError, match="MSH"):
            parse_message("PID|1||12345")


class TestBuilder:
    """Tests for the HL7 message builder."""

    def test_build_basic_message(self):
        msg = (
            MessageBuilder()
            .msh(sending_app="LAB", receiving_app="EHR", message_type="ORU^R01")
            .pid(patient_id="12345", patient_name="DOE^JOHN")
            .obx(set_id=1, value_type="NM", observation_id="GLU", value="95", units="mg/dL")
            .build()
        )
        assert isinstance(msg, Message)
        assert len(msg.segments) == 3

    def test_build_msh_only(self):
        msg = MessageBuilder().msh().build()
        assert msg.segment_types == ["MSH"]

    def test_build_empty_raises(self):
        with pytest.raises(ValueError):
            MessageBuilder().build()

    def test_build_to_hl7_roundtrip(self):
        msg = (
            MessageBuilder()
            .msh(sending_app="TEST", message_type="ACK")
            .build()
        )
        hl7_str = msg.to_hl7()
        assert hl7_str.startswith("MSH|")

    def test_build_custom_segment(self):
        msg = (
            MessageBuilder()
            .msh(message_type="ORU^R01")
            .custom_segment("ZDS", "1", "custom_data", "extra")
            .build()
        )
        assert "ZDS" in msg.segment_types


class TestValidator:
    """Tests for HL7 message validation."""

    def test_valid_message(self):
        msg = parse_message(SAMPLE_ORU)
        result = validate_message(msg)
        assert result.is_valid

    def test_missing_control_id(self):
        raw = "MSH|^~\\&|LAB|FAC|EHR|HOSP|20240101||ORU^R01||P|2.5"
        msg = parse_message(raw)
        result = validate_message(msg)
        assert not result.is_valid

    def test_pid_required(self):
        msg = parse_message(SAMPLE_MINIMAL)
        result = validate_message(msg, require_pid=True)
        assert not result.is_valid

    def test_validation_result_string(self):
        msg = parse_message(SAMPLE_ORU)
        result = validate_message(msg)
        assert "Valid" in str(result) or "Invalid" in str(result)


class TestModels:
    """Tests for data models."""

    def test_field_components(self):
        f = Field("DOE^JOHN^M")
        assert f.components == ["DOE", "JOHN", "M"]

    def test_field_bool(self):
        assert bool(Field("value"))
        assert not bool(Field(""))

    def test_message_to_dict(self):
        msg = parse_message(SAMPLE_ORU)
        d = msg.to_dict()
        assert "MSH" in d
        assert "PID" in d

    def test_message_to_hl7(self):
        msg = parse_message(SAMPLE_ORU)
        hl7 = msg.to_hl7()
        assert hl7.startswith("MSH|")
        assert "\r" in hl7
