import re

# Best-effort phone pattern: handles +country code, parens, dashes, dots, spaces.
# Deliberately a bit loose since company sites format numbers inconsistently.
PHONE_PATTERN = re.compile(
    r'(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{2,4})?'
)

# Best-effort street-address pattern: "<number> <street words> <St/Ave/Rd/...>"
# optionally followed by city/state/zip.
ADDRESS_PATTERN = re.compile(
    r'(?<![\d-])\d{1,6}\s[A-Za-z0-9.,\s]{3,45}?'
    r'(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|'
    r'Drive|Dr\.?|Way|Suite|Ste\.?|Floor|Plaza|Place|Pl\.?)'
    r'[A-Za-z0-9.,\s]{0,50}?(?:\d{4,6})?',
    re.IGNORECASE,
)


def extract_phone_from_text(text):
    """Return the first plausible phone number found in text, or 'N/A'."""
    if not text:
        return "N/A"

    for match in PHONE_PATTERN.finditer(text):
        candidate = match.group().strip()
        digits_only = re.sub(r'\D', '', candidate)
        # Real phone numbers have at least 7 digits; skip short false positives
        # like years, prices, or page numbers.
        if 7 <= len(digits_only) <= 15:
            return candidate
    return "N/A"


def extract_address_from_text(text):
    """Return the first plausible postal address found in text, or 'N/A'."""
    if not text:
        return "N/A"

    match = ADDRESS_PATTERN.search(text)
    if match:
        candidate = match.group().strip()
        # Collapse extra whitespace picked up from HTML text extraction
        candidate = re.sub(r'\s+', ' ', candidate)
        return candidate
    return "N/A"