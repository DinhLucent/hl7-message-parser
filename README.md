# hl7-message-parser

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Tests](https://img.shields.io/badge/Tests-passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

A modular, professional HL7 v2.x message engine. It provides a fluent builder API for constructing messages and a robust parser for converting raw clinical data into structured, semantically labeled objects.

## What is HL7 v2.x?

Health Level Seven (HL7) Version 2 is the most widely implemented standard for healthcare data exchange in the world. It uses a pipe-delimited (`|`) format to transmit patient information, laboratory results, and clinical orders between EMRs, LIS, and RIS systems.

## Quick Start

### Parse a message

```python
from src.parser import parse_message

raw_hl7 = "MSH|^~\\&|LAB|FAC|||20240101||ORU^R01|MSG001|P|2.5\rPID|1||12345||DOE^JOHN"
msg = parse_message(raw_hl7)

print(msg.message_type)  # ORU
print(msg.pid.patient_name)  # DOE^JOHN
```

### Use the Fluent Builder

```python
from src.builder import MessageBuilder

msg = (
    MessageBuilder()
    .msh(sending_app="LAB", message_type="ORU^R01")
    .pid(patient_id="PAT001", patient_name="Doe^Jane")
    .obx(observation_id="8310-5", value="37.5", units="Cel")
    .build()
)

print(msg.to_hl7())
```

## Features

- **Semantic Dictionary Export**: Convert messages to dictionaries with human-readable keys (e.g., `patient_id` instead of `field_3`).
- **Visual Tree View**: Built-in `pretty_print()` for inspecting complex message hierarchies during debugging.
- **Fluent Builder API**: Chainable methods to construct valid HL7 messages without manual string concatenation.
- **Modular Architecture**: Separate layers for Parsing, Building, Data Modeling, and Validation.
- **Pure Python**: Zero external dependencies. Designed for high-speed clinical middleware.

## How it works — module by module

### `src/models.py` — Data Abstractions

The foundation of the toolkit. Provides the `Message`, `Segment`, and `Field` dataclasses.

#### Visual Inspection

```python
msg = parse_message(raw_hl7)
print(msg.pretty_print())
```

Output:
```
HL7 Message (ORU^R01)
├── MSH
│   ├── [MSH.3] LAB
│   ├── [MSH.9] ORU^R01
├── PID
│   ├── [PID.3] 12345
│   ├── [PID.5] DOE^JOHN
```

#### Semantic Export

```python
# Standard extract (field_1, field_2...)
data = msg.to_dict()

# Semantic extract (patient_id, message_type...)
clean_data = msg.to_dict(semantic=True)
print(clean_data["PID"]["patient_id"])
```

### `src/validators.py` — Clinical Rules

Validate message integrity, checking for mandatory fields (like Control ID) and segment sequences.

## Project Structure

```
hl7-message-parser/
├── src/
│   ├── builder.py          # Fluent API for construction
│   ├── parser.py           # String-to-Object logic
│   ├── models.py           # Message/Segment/Field classes
│   └── validators.py       # HL7 clinical rules
├── tests/
│   └── test_parser.py      # Full suite for parser/builder/models
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

```bash
git clone https://github.com/DinhLucent/hl7-message-parser.git
cd hl7-message-parser
pip install -r requirements.txt
```

## Running Tests

```bash
python -m pytest tests/test_parser.py -v
```

## License

MIT License — see [LICENSE](LICENSE)

---
Built by [DinhLucent](https://github.com/DinhLucent)
