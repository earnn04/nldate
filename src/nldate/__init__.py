import re
from datetime import date, datetime, timedelta
from typing import Optional

from dateutil.parser import parse as du_parse
from dateutil.relativedelta import relativedelta


def parse(s: str, today: Optional[date] = None) -> date:
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

    # 2. Relative Expressions
    # UPDATED: Added "a" and "an" to the mapping
    num_map = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

    # UPDATED: Regex now includes "a|an"
    num_pattern = r"(\d+|a|an|one|two|three|four|five)"
    unit_pattern = r"\s+(day|week|month|year)s?"

    # Handle "X units ago" (e.g., 'a week ago', '3 days ago')
    ago_match = re.search(num_pattern + unit_pattern + r"\s+ago", s)
    if ago_match:
        num_str, unit = ago_match.groups()
        num = int(num_str) if num_str.isdigit() else num_map.get(num_str, 1)
        delta_args = {f"{unit}s": -num}
        return today + relativedelta(**delta_args)

    # Handle "in X units"
    in_match = re.search(r"in\s+" + num_pattern + unit_pattern, s)
    if in_match:
        num_str, unit = in_match.groups()
        num = int(num_str) if num_str.isdigit() else num_map.get(num_str, 1)
        delta_args = {f"{unit}s": num}
        return today + relativedelta(**delta_args)

    # Handle "before/after/from"
    rel_pattern = num_pattern + unit_pattern + r"\s+(before|after|from)\s+(.*)"
    match = re.search(rel_pattern, s)
    if match:
        num_str, unit, direction, base_str = match.groups()
        num = int(num_str) if num_str.isdigit() else num_map.get(num_str, 1)
        base_date = parse(base_str, today=today)
        multiplier = -1 if direction == "before" else 1
        delta_args = {f"{unit}s": num * multiplier}
        return base_date + relativedelta(**delta_args)

    # 3. Weekday logic
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    if s.startswith("next ") and s.split()[-1] in weekdays:
        target_weekday = weekdays[s.split()[-1]]
        days_ahead = (target_weekday - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    # 4. Absolute date fallback
    try:
        default_dt = datetime.combine(today, datetime.min.time())
        return du_parse(s, default=default_dt).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s}")
