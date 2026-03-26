# 🏥 HL7 Message Parser

[![CI](https://github.com/DinhLucent/hl7-message-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/DinhLucent/hl7-message-parser/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A lightweight, zero-dependency Python library for **parsing, constructing, and validating HL7 v2.x messages**. Built for healthcare IT professionals working with Laboratory Information Systems (LIS), Electronic Health Records (EHR), and medical device integration.

## ✨ Features

| Feature | Description |
|---|---|
| **Parse** | Convert raw HL7 strings into structured Python objects |
| **Build** | Construct HL7 messages programmatically with a fluent API |
| **Validate** | Check message integrity, required segments, and field constraints |
| **Zero Dependencies** | Pure Python — no external packages needed |
| **Type Hints** | Full PEP 484 type annotations for IDE support |

## 🚀 Quick Start

```bash
pip install -e .
```

### Parsing a Message

```python
from hl7_parser import parse_message

raw = "MSH|^~\\&|LAB|FACILITY|EHR|HOSPITAL|20240101120000||ORU^R01|MSG001|P|2.5\rPID|1||12345^^^MRN||DOE^JOHN||19800101|M\rOBX|1|NM|GLU^Glucose||95|mg/dL|70-100|N|||F"

msg = parse_message(raw)

# Access segments
msh = msg.get_segment("MSH")
print(msh.get_field(9))   # "ORU^R01"
print(msh.message_type)    # "ORU"
print(msh.trigger_event)   # "R01"

# Access patient info
pid = msg.get_segment("PID")
print(pid.patient_name)    # "DOE^JOHN"
print(pid.patient_id)      # "12345"

# Access results
for obx in msg.get_segments("OBX"):
    print(f"{obx.observation_id}: {obx.value} {obx.units}")
```

### Building a Message

```python
from hl7_parser import MessageBuilder

msg = (
    MessageBuilder()
    .msh(sending_app="LAB", receiving_app="EHR", message_type="ORU^R01")
    .pid(patient_id="12345", patient_name="DOE^JOHN", dob="19800101")
    .obx(set_id=1, value_type="NM", observation_id="GLU", value="95", units="mg/dL")
    .build()
)

print(msg.to_hl7())  # Raw HL7 string with \r delimiters
```

## 📋 Supported Message Types

- **ORU^R01** — Observation Result (Lab Results)
- **ORM^O01** — Order Message
- **ADT^A01-A08** — Admit/Discharge/Transfer
- **ACK** — Acknowledgment
- **QRY^Q01** — Query

## 🏗️ Architecture

```
src/
├── __init__.py          # Public API exports
├── parser.py            # HL7 message parser
├── models.py            # Message, Segment, Field models
├── builder.py           # Fluent message builder
├── validators.py        # Message validation rules
└── constants.py         # HL7 segment definitions
```

## 🧪 Testing

```bash
pip install pytest
pytest tests/ -v
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
