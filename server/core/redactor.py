import re

PATTERNS = [
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]'),
    (r'\+?[\d\s\-\(\)]{10,15}', '[PHONE REDACTED]'),
    (r'\b\d{12}\b', '[ID REDACTED]'),
    (r'\b(?:\d{4}[\s\-]?){3}\d{4}\b', '[CARD REDACTED]'),
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text