import re
from datetime import datetime, timezone


_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2})(?::?(\d{2}))")


def parse_offset_minutes(tz_text: str) -> int:
    if tz_text is None:
        raise ValueError("Timezone is NULL")

    tz_text = tz_text.strip()
    if not tz_text:
        raise ValueError("Timezone is empty")

    matches = _TZ_OFFSET_RE.findall(tz_text)
    if not matches:
        raise ValueError(f"Invalid timezone format: {tz_text!r}")

    
    sign_str, hh_str, mm_str = matches[-1]

    hh = int(hh_str)
    mm = int(mm_str) if mm_str else 0

    if hh > 14 or mm > 59:
        raise ValueError(f"Invalid timezone offset values: {tz_text!r}")

    sign = 1 if sign_str == "+" else -1
    return sign * (hh * 60 + mm)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)