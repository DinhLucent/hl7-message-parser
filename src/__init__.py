"""
HL7 Message Parser — A lightweight Python library for HL7 v2.x messages.

Usage:
    from src.parser import parse_message
    from src.builder import MessageBuilder
"""

from src.parser import parse_message
from src.builder import MessageBuilder
from src.models import Message, Segment, Field
from src.validators import validate_message

__version__ = "0.1.0"
__all__ = [
    "parse_message",
    "MessageBuilder",
    "Message",
    "Segment",
    "Field",
    "validate_message",
]
