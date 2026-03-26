"""
HL7 v2.x Constants — Segment type definitions and common codes.
"""

# Standard HL7 v2.x Segment Types
SEGMENTS = {
    "MSH": "Message Header",
    "EVN": "Event Type",
    "PID": "Patient Identification",
    "PD1": "Patient Additional Demographic",
    "PV1": "Patient Visit",
    "PV2": "Patient Visit Additional",
    "ORC": "Common Order",
    "OBR": "Observation Request",
    "OBX": "Observation Result",
    "NTE": "Notes and Comments",
    "NK1": "Next of Kin",
    "IN1": "Insurance",
    "DG1": "Diagnosis",
    "AL1": "Allergy Information",
    "GT1": "Guarantor",
    "ZDS": "Custom Segment (Document)",
}

# Common Message Types
MESSAGE_TYPES = {
    "ORU^R01": "Observation Result (Unsolicited)",
    "ORM^O01": "General Order",
    "ADT^A01": "Admit/Visit Notification",
    "ADT^A02": "Transfer a Patient",
    "ADT^A03": "Discharge/End Visit",
    "ADT^A04": "Register a Patient",
    "ADT^A08": "Update Patient Information",
    "ACK": "General Acknowledgment",
    "QRY^Q01": "Query",
    "MDM^T01": "New Document Notification",
    "SIU^S12": "Schedule Information (Unsolicited)",
}

# OBX Value Types
VALUE_TYPES = {
    "NM": "Numeric",
    "ST": "String",
    "TX": "Text",
    "DT": "Date",
    "TS": "Timestamp",
    "CE": "Coded Element",
    "CWE": "Coded with Exceptions",
    "FT": "Formatted Text",
    "ED": "Encapsulated Data",
    "SN": "Structured Numeric",
}

# Result Status Codes (OBX-11)
RESULT_STATUS = {
    "F": "Final",
    "P": "Preliminary",
    "C": "Correction",
    "X": "Cannot Obtain",
    "I": "Specimen In Lab",
    "R": "Results Stored",
    "S": "Partial",
    "W": "Post-Original as Wrong",
}

# Abnormal Flags (OBX-8)
ABNORMAL_FLAGS = {
    "N": "Normal",
    "L": "Low",
    "H": "High",
    "LL": "Critical Low",
    "HH": "Critical High",
    "A": "Abnormal",
    "AA": "Very Abnormal",
}
