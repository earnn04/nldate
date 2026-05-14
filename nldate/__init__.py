import re
from datetime import date, datetime, timedelta
from typing import Optional

from dateutil.parser import parse as du_parse
from dateutil.relativedelta import relativedelta


def parse(s: str, today: Optional[date] = None) -> date:
    """
    Parses a natural language date string into a date object.
    """
    if today is None:
        today = date.today()

    s = s.lower().strip()

    # 1. Basic Constants
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

# 2. Relative Expressions (e.g., "5 days before yesterday", "in 3 days")
    num_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    
    # Check for "in X days" specifically
    in_match = re.search(r"in\s+(\d+|one|two|three|four|five)\s+(day|week|month|year)s?", s)
    if in_match:
        num_str, unit = in_match.groups()
        num = int(num_str) if num_str.isdigit() else num_map.get(num_str, 1)
        delta_args = {f"{unit}s": num}
        return today + relativedelta(**delta_args) # type: ignore

    # Existing before/after logic
    rel_pattern = (
        r"(\d+|one|two|three|four|five)\s+(day|week|month|year)s?\s+"
        r"(before|after|from)\s+(.*)"
    )
    match = re.search(rel_pattern, s)
    if match:
        num_str, unit, direction, base_str = match.groups()
        num = int(num_str) if num_str.isdigit() else num_map.get(num_str, 1)
        base_date = parse(base_str, today=today)
        multiplier = -1 if direction == "before" else 1
        delta_args = {f"{unit}s": num * multiplier}
        return base_date + relativedelta(**delta_args) # type: ignore

    # 3. Weekday logic (e.g., "next tuesday")
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    if s.startswith("next ") and s.split()[-1] in weekdays:
        target_weekday = weekdays[s.split()[-1]]
        days_ahead = (target_weekday - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    # 4. Absolute date fallback using dateutil
    try:
        # We use a datetime default so du_parse returns a datetime we can call .date() on
        default_dt = datetime.combine(today, datetime.min.time())
        return du_parse(s, default=default_dt).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s}")