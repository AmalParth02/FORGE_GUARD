import re

# Pre-compiled regex patterns for maximum matching throughput
COMPILED_PATTERNS = {
    "name": [
        re.compile(r"(?:Name|NAME|Full Name|Holder Name)[: \t]+([A-Z][a-zA-Z \t]{2,30})"),
        re.compile(r"(?:S/O|D/O|W/O|C/O)[: \t]+([A-Z][a-zA-Z \t]{2,30})"),
    ],
    "dob": [
        re.compile(r"(?:DOB|Date of Birth|Birth Date|Date Of Birth)[: \t]+(\d{2}[/.-]\d{2}[/.-]\d{4})", re.IGNORECASE),
        re.compile(r"\b(\d{2}[/.-]\d{2}[/.-]\d{4})\b"),
        re.compile(r"\b(\d{4}[/.-]\d{2}[/.-]\d{2})\b")
    ],
    "gender": [
        re.compile(r"(?:Gender|Sex|SEX|GENDER)[: \t]+(Male|Female|Transgender|MALE|FEMALE|M|F)\b", re.IGNORECASE),
        re.compile(r"\b(Male|Female|Transgender|MALE|FEMALE)\b", re.IGNORECASE)
    ],
    "aadhaar_number": [
        re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
    ],
    "pan_number": [
        re.compile(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b")
    ],
    "passport_number": [
        re.compile(r"\b[A-Z]{1}[0-9]{7}\b")
    ],
    "voter_id": [
        re.compile(r"\b[A-Z]{3}[0-9]{7}\b")
    ],
    "pincode": [
        re.compile(r"\b[1-9][0-9]{5}\b"),
        re.compile(r"(?:PIN|Pincode|Pin Code)[: \t]+(\d{6})", re.IGNORECASE)
    ],
    "nationality": [
        re.compile(r"(?:Nationality|NATIONALITY)[: \t]+(INDIAN|Indian|[A-Z]{3})\b", re.IGNORECASE),
        re.compile(r"\b(INDIAN|Indian)\b", re.IGNORECASE)
    ]
}

# Backward compatibility raw dict
PATTERNS = {
    "name": [
        r"(?:Name|NAME|Full Name|Holder Name)[: \t]+([A-Z][a-zA-Z \t]{2,30})",
        r"(?:S/O|D/O|W/O|C/O)[: \t]+([A-Z][a-zA-Z \t]{2,30})",
    ],
    "dob": [
        r"(?:DOB|Date of Birth|Birth Date|Date Of Birth)[: \t]+(\d{2}[/.-]\d{2}[/.-]\d{4})",
        r"\b(\d{2}[/.-]\d{2}[/.-]\d{4})\b",
        r"\b(\d{4}[/.-]\d{2}[/.-]\d{2})\b"
    ],
    "gender": [
        r"(?:Gender|Sex|SEX|GENDER)[: \t]+(Male|Female|Transgender|MALE|FEMALE|M|F)\b",
        r"\b(Male|Female|Transgender|MALE|FEMALE)\b"
    ],
    "aadhaar_number": [
        r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    ],
    "pan_number": [
        r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"
    ],
    "passport_number": [
        r"\b[A-Z]{1}[0-9]{7}\b"
    ],
    "voter_id": [
        r"\b[A-Z]{3}[0-9]{7}\b"
    ],
    "pincode": [
        r"\b[1-9][0-9]{5}\b",
        r"(?:PIN|Pincode|Pin Code)[: \t]+(\d{6})"
    ],
    "nationality": [
        r"(?:Nationality|NATIONALITY)[: \t]+(INDIAN|Indian|[A-Z]{3})\b",
        r"\b(INDIAN|Indian)\b"
    ]
}
