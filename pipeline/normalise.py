"""
Stage 2: parse/normalise helpers.

Sources disagree on surface form: "MEL 251", "MEL-251", "mel251" are one course;
credits appear as "3", "3.0", "3-0-2", "4 credits"; semesters as "Sem 5", "V",
"5th". Normalisation happens once, here, so every downstream stage can assume a
canonical form -- and so the validator's duplicate check actually catches
duplicates that differ only in spacing.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

_ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
          "VII": 7, "VIII": 8, "IX": 9, "X": 10}

_CODE_RE = re.compile(r"^\s*([A-Za-z]{2,4})[\s\-_/]*([0-9]{3,4})\s*$")


def normalise_code(raw: Optional[str]) -> Optional[str]:
    """'mel 251' / 'MEL-251' -> 'MEL251'. Returns None for blanks."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = _CODE_RE.match(s)
    if m:
        return f"{m.group(1).upper()}{m.group(2)}"
    # Unrecognised shape: upper-case and strip internal whitespace, but preserve
    # the original so the validator can flag it rather than silently mangling it.
    return re.sub(r"\s+", "", s.upper())


def code_is_canonical(code: Optional[str]) -> bool:
    return bool(code) and bool(re.match(r"^[A-Z]{2,4}[0-9]{3,4}$", code))


def normalise_credits(raw) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Return (credits, credit_structure, problem).

    Accepts 3, '3', '3.0', '3-0-2' (L-T-P), '4 credits'. When given L-T-P it does
    NOT compute the credit total: institutes weight practicals differently
    (commonly L + T + P/2), so inferring a number here would be a guess dressed
    as data. The structure is kept and credits left None for a human to fill.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, None, None
    s = str(raw).strip()
    ltp = re.match(r"^\s*(\d+)\s*[-:/]\s*(\d+)\s*[-:/]\s*(\d+)\s*$", s)
    if ltp:
        return None, f"{ltp.group(1)}-{ltp.group(2)}-{ltp.group(3)}", None
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return None, None, f"credits not numeric: {s!r}"
    try:
        return float(m.group(1)), None, None
    except ValueError:
        return None, None, f"credits not numeric: {s!r}"


def normalise_semester(raw) -> Tuple[Optional[int], Optional[str]]:
    """'Sem 5' / 'V' / '5th' / 5 -> 5. Returns (value, problem)."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, None
    s = str(raw).strip().upper().replace("SEMESTER", "").replace("SEM", "").strip(" .:-")
    if s in _ROMAN:
        return _ROMAN[s], None
    m = re.search(r"(\d+)", s)
    if not m:
        return None, f"semester not recognised: {raw!r}"
    return int(m.group(1)), None


def normalise_enum(raw: Optional[str], allowed: tuple, default=None,
                   aliases: Optional[dict] = None) -> Tuple[Optional[str], Optional[str]]:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return default, None
    s = str(raw).strip().lower().replace("_", "-").replace(" ", "-")
    if aliases and s in aliases:
        s = aliases[s]
    if s in allowed:
        return s, None
    return default, f"value {raw!r} not in {allowed}"


def normalise_text(raw: Optional[str]) -> Optional[str]:
    """Collapse the whitespace that PDF extraction scatters through prose."""
    if raw is None:
        return None
    s = re.sub(r"[ \t]+", " ", str(raw))
    s = re.sub(r"\s*\n\s*", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    # PDF text layers frequently hyphenate across line breaks.
    s = re.sub(r"(\w)-\n(\w)", r"\1\2", s)
    return s.strip() or None


def normalise_date(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if raw is None or not str(raw).strip():
        return None, None
    s = str(raw).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s, None
    for pat, order in ((r"^(\d{2})[/-](\d{2})[/-](\d{4})$", "dmy"),
                       (r"^(\d{4})/(\d{2})/(\d{2})$", "ymd")):
        m = re.match(pat, s)
        if m:
            if order == "dmy":
                return f"{m.group(3)}-{m.group(2)}-{m.group(1)}", None
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", None
    return None, f"date not ISO-8601: {raw!r}"
