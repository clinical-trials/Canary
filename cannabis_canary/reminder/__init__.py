"""Follow-up review scheduling. Spec: remind every 3 months by default,
configurable to 6 or 12 months (or disabled at the app layer)."""
from cannabis_canary.reminder.schedule import ALLOWED_INTERVALS, is_due, next_review_due

__all__ = ["ALLOWED_INTERVALS", "is_due", "next_review_due"]
