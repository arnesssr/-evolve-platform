from datetime import datetime, timedelta
from typing import Optional, Tuple

# Minimal cron parser supporting numeric or '*' for: minute hour dom month dow
# Does not support ranges/lists/steps. Returns next run time >= from_dt + 1 minute.

def _parse_field(field: str, min_val: int, max_val: int) -> Optional[int]:
    field = (field or '*').strip()
    if field == '*':
        return None
    try:
        v = int(field)
        if v < min_val or v > max_val:
            return None
        return v
    except Exception:
        return None


def compute_next_run(cron_expr: str, from_dt: Optional[datetime] = None) -> Optional[datetime]:
    """Compute next run datetime for a very simple cron expression.

    Supports: "m h dom mon dow" where each is '*' or a single integer.
    Minute: 0-59, Hour: 0-23, Day of month: 1-31, Month: 1-12, Day of week: 0-6 (Mon=0)
    Note: Python's datetime.weekday() => Monday=0 .. Sunday=6.
    """
    if not cron_expr:
        return None
    parts = cron_expr.split()
    if len(parts) != 5:
        return None

    m_s, h_s, dom_s, mon_s, dow_s = parts
    m = _parse_field(m_s, 0, 59)
    h = _parse_field(h_s, 0, 23)
    dom = _parse_field(dom_s, 1, 31)
    mon = _parse_field(mon_s, 1, 12)
    dow = _parse_field(dow_s, 0, 6)

    now = from_dt or datetime.utcnow()
    # Start searching from next minute
    candidate = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

    # Search up to 2 years ahead to avoid infinite loops
    limit = now + timedelta(days=730)
    while candidate <= limit:
        if (m is not None and candidate.minute != m):
            candidate += timedelta(minutes=1)
            continue
        if (h is not None and candidate.hour != h):
            candidate += timedelta(minutes=1)
            continue
        if (mon is not None and candidate.month != mon):
            # Jump to next month start at 00:00 to speed up
            year = candidate.year + (1 if candidate.month == 12 else 0)
            month = 1 if candidate.month == 12 else candidate.month + 1
            candidate = candidate.replace(year=year, month=month, day=1, hour=0, minute=0)
            continue
        if (dom is not None and candidate.day != dom):
            # Jump one day
            candidate += timedelta(days=1)
            candidate = candidate.replace(hour=0, minute=0)
            continue
        if (dow is not None and candidate.weekday() != dow):
            # Jump one day
            candidate += timedelta(days=1)
            candidate = candidate.replace(hour=0, minute=0)
            continue
        # All constraints matched
        return candidate

    return None

