"""Pure date math for review reminders. Month-end safe (Jan 31 + 3mo = Apr 30)."""
from __future__ import annotations

import calendar
from datetime import date

ALLOWED_INTERVALS: tuple[int, ...] = (3, 6, 12)


def next_review_due(last_reviewed: date, months: int = 3) -> date:
    if months not in ALLOWED_INTERVALS:
        raise ValueError(f"months must be one of {ALLOWED_INTERVALS}, got {months}")
    month_index = last_reviewed.month - 1 + months
    year = last_reviewed.year + month_index // 12
    month = month_index % 12 + 1
    day = min(last_reviewed.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def is_due(last_reviewed: date, months: int = 3, today: date | None = None) -> bool:
    today = today or date.today()
    return today >= next_review_due(last_reviewed, months)
