from datetime import date, datetime
from zoneinfo import ZoneInfo

from backend.app.config import Settings


def today_in_timezone(settings: Settings) -> date:
    return datetime.now(ZoneInfo(settings.app_timezone)).date()


def next_streak(last_checkin_date: date | None, checkin_date: date) -> int:
    if last_checkin_date is None:
        return 1
    if (checkin_date - last_checkin_date).days == 1:
        return 1  # Caller adds the existing streak to this continuation marker.
    return 0
