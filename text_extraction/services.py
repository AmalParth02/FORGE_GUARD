import re

# Pre-compiled regex patterns for maximum matching throughput
COMPILED_PATTERNS = {
    "name": [
        re.compile(r"^(?:Full\s*Name|Holder(?:\'s)?\s*Name|Name(?:\s*of\s*Holder)?|Given\s*Names?|First\s*Name|NAME|Name)\s*[:\-]?\s*(.*)$", re.IGNORECASE),
        re.compile(r"(?:S/O|D/O|W/O|C/O)[: \t]+([A-Za-z][a-zA-Z \t]{2,30})"),
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

EXCLUDED_NAME_LABELS = {
    "NAME", "FULL NAME", "HOLDER NAME", "HOLDER'S NAME", "NAME OF HOLDER",
    "SURNAME", "GIVEN NAMES", "GIVEN NAME", "FIRST NAME", "LAST NAME", "MIDDLE NAME",
    "ADDRESS", "PERMANENT ADDRESS", "PRESENT ADDRESS",
    "DOB", "DATE OF BIRTH", "BIRTH DATE", "DATE OF ISSUE", "DATE OF EXPIRY", "VALID TILL", "EXPIRY DATE",
    "SEX", "GENDER", "MALE", "FEMALE", "TRANSGENDER",
    "FATHER", "FATHER'S NAME", "MOTHER", "MOTHER'S NAME", "HUSBAND", "GUARDIAN", "S/O", "D/O", "W/O", "C/O",
    "ID", "ID NUMBER", "ID NO", "LICENSE NO", "LICENCE NO", "DL NO", "DL NUMBER",
    "DRIVING LICENSE", "DRIVINGLICENSE", "DRIVER LICENSE", "DRIVER'S LICENSE", "DRIVER'S LICENCE", "DRIVING LICENCE",
    "CLASS", "CLASS C", "CATEGORIES OF VEHICLES", "CLASS/ENDO", "ISSUED", "EXPIRES", "AUTHORIZATION",
    "AADHAAR", "AADHAAR NUMBER", "AADHAAR NO", "UIDAI", "GOVERNMENT OF INDIA", "GOVT OF INDIA",
    "PAN", "PAN NUMBER", "PAN CARD", "INCOME TAX DEPARTMENT",
    "PASSPORT", "REPUBLIC OF INDIA", "PASSPORT NO", "TYPE", "CODE", "NATIONALITY", "COUNTRY",
    "VOTER ID", "ELECTION COMMISSION", "EPIC NO", "ELECTOR PHOTO IDENTITY CARD",
    "PIN", "PINCODE", "PIN CODE", "SIGNATURE", "HOLDER SIGNATURE", "AUTHORISED SIGNATORY", "BLOOD GROUP"
}

NEXT_SECTION_PREFIXES = (
    "ADDRESS", "DATE OF BIRTH", "DOB", "BIRTH", "SEX", "GENDER",
    "CATEGORIES", "CLASS/ENDO", "ISSUED", "EXPIRES", "VALID",
    "FATHER", "MOTHER", "HUSBAND", "S/O", "D/O", "W/O", "C/O",
    "PIN", "NATIONALITY", "SIGNATURE", "ID"
)

class TextExtractionService:
    """
    High-Performance Regex-based service for extracting key fields from document text.
    Uses pre-compiled regular expressions for sub-millisecond throughput.
    """

    @classmethod
    def _extract_name(cls, text):
        """
        Extracts person's name supporting both single-line ('Name: JOHN DOE')
        and multi-line ('Name\\nJOHN DOE') label-value structures.
        Prevents label leakage and excludes non-name fields.
        """
        if not text:
            return None

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name_label_regex = COMPILED_PATTERNS["name"][0]

        for i, line in enumerate(lines):
            match = name_label_regex.match(line)
            if match:
                raw_val = match.group(1).strip()
                # If value is on the same line, truncate any subsequent field marker
                if raw_val:
                    raw_val = re.split(
                        r"\b(?:DOB|Date of [Bb]irth|Sex|Gender|Address|S/O|D/O|W/O|C/O|ID|Class)\b",
                        raw_val,
                        flags=re.IGNORECASE
                    )[0].strip()
                    val_clean = re.sub(r"[^a-zA-Z\s.'-]", "", raw_val).strip()
                    val_upper = val_clean.upper()
                    if val_clean and len(val_clean) >= 2 and val_upper not in EXCLUDED_NAME_LABELS:
                        if re.match(r"^[A-Za-z][A-Za-z\s.'-]{1,50}$", val_clean):
                            return val_clean

                # If label was alone on line, check the next non-empty line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    next_line_trunc = re.split(
                        r"\b(?:DOB|Date of [Bb]irth|Sex|Gender|Address|S/O|D/O|W/O|C/O|ID|Class)\b",
                        next_line,
                        flags=re.IGNORECASE
                    )[0].strip()
                    next_clean = re.sub(r"[^a-zA-Z\s.'-]", "", next_line_trunc).strip()
                    next_upper = next_clean.upper()

                    if next_upper in EXCLUDED_NAME_LABELS:
                        continue
                    if any(next_upper.startswith(p) for p in NEXT_SECTION_PREFIXES):
                        continue

                    if re.match(r"^[A-Za-z][A-Za-z\s.'-]{1,50}$", next_clean) and len(next_clean) >= 2:
                        return next_clean

        # Fallback to relationship match (S/O, D/O, W/O, C/O) if direct name label wasn't found
        so_pattern = COMPILED_PATTERNS["name"][1]
        so_match = so_pattern.search(text)
        if so_match:
            candidate = so_match.group(1).strip()
            cand_upper = candidate.upper()
            if cand_upper not in EXCLUDED_NAME_LABELS and re.match(r"^[A-Za-z][A-Za-z\s.'-]{1,50}$", candidate):
                return candidate

        return None

    @classmethod
    def extract_fields(cls, text):
        """
        Runs pre-compiled regex matchers against OCR text and returns structured fields dict.
        """
        if not text:
            return {
                "document_type": "UNKNOWN",
                "extracted_fields": {},
                "raw_text": ""
            }

        extracted = {}

        # 1. Aadhaar Number
        aadhaar_match = COMPILED_PATTERNS["aadhaar_number"][0].search(text)
        if aadhaar_match:
            extracted["aadhaar_number"] = aadhaar_match.group(0).replace(" ", "")

        # 2. PAN Number
        pan_match = COMPILED_PATTERNS["pan_number"][0].search(text)
        if pan_match:
            extracted["pan_number"] = pan_match.group(0)

        # 3. Passport Number
        passport_match = COMPILED_PATTERNS["passport_number"][0].search(text)
        if passport_match:
            extracted["passport_number"] = passport_match.group(0)

        # 4. Voter ID
        voter_match = COMPILED_PATTERNS["voter_id"][0].search(text)
        if voter_match:
            extracted["voter_id"] = voter_match.group(0)

        # 5. Date of Birth
        for pattern in COMPILED_PATTERNS["dob"]:
            match = pattern.search(text)
            if match:
                extracted["dob"] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break

        # 6. Gender
        for pattern in COMPILED_PATTERNS["gender"]:
            match = pattern.search(text)
            if match:
                val = match.group(1).upper()
                extracted["gender"] = "MALE" if val in ["M", "MALE"] else ("FEMALE" if val in ["F", "FEMALE"] else val)
                break

        # 7. Name
        name_val = cls._extract_name(text)
        if name_val:
            extracted["name"] = name_val

        # 8. Pincode
        for pattern in COMPILED_PATTERNS["pincode"]:
            match = pattern.search(text)
            if match:
                extracted["pincode"] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break

        # 9. Nationality
        for pattern in COMPILED_PATTERNS["nationality"]:
            match = pattern.search(text)
            if match:
                extracted["nationality"] = match.group(1).upper()
                break

        # Determine document type classification
        text_upper = text.upper()
        document_type = "UNKNOWN"
        if any(kw in text_upper for kw in [
            "DRIVINGLICENSE", "DRIVING LICENSE", "DRIVER LICENSE", "DRIVER'S LICENSE",
            "DRIVER’S LICENSE", "DRIVING LICENCE", "DRIVER LICENCE", "DRIVER'S LICENCE"
        ]):
            document_type = "DRIVING_LICENSE"
        elif "aadhaar_number" in extracted or "AADHAAR" in text_upper or "GOVERNMENT OF INDIA" in text_upper:
            document_type = "AADHAAR_CARD"
        elif "pan_number" in extracted or "INCOME TAX DEPARTMENT" in text_upper:
            document_type = "PAN_CARD"
        elif "passport_number" in extracted or "PASSPORT" in text_upper or "REPUBLIC OF INDIA" in text_upper:
            document_type = "PASSPORT"
        elif "voter_id" in extracted or "ELECTION COMMISSION" in text_upper:
            document_type = "VOTER_ID"

        return {
            "document_type": document_type,
            "extracted_fields": extracted,
            "raw_text": text
        }
