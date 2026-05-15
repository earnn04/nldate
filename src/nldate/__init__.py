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
    if s in ("today", "now"):
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

    # Helper to extract all time units from a string
    def extract_delta(text: str) -> dict[str, int]:
        num_map = {
            "a": 1,
            "an": 1,
            "the": 1,  # Added "the" as a synonym for 1
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
        }
        # Added "the" to the regex pattern
        pattern = r"(\d+|a|an|the|one|two|three|four|five)\s+(day|week|month|year)s?"
        kwargs: dict[str, int] = {}
        for m in re.finditer(pattern, text):
            # Unpacking without brackets
            val, unit = m.groups()
            num = int(val) if val.isdigit() else num_map.get(val, 1)
            kwargs[f"{unit}s"] = kwargs.get(f"{unit}s", 0) + num
        return kwargs

    # 2. Relative Expressions

    # Handle "ago"
    if s.endswith(" ago"):
        delta_args = extract_delta(s)
        if delta_args:
            return today + relativedelta(**{k: -v for k, v in delta_args.items()})  # type: ignore

    # Handle "in X"
    if s.startswith("in "):
        delta_args = extract_delta(s)
        if delta_args:
            return today + relativedelta(**delta_args)  # type: ignore

    # Handle before/after/from
    for pivot in [" before ", " after ", " from "]:
        if pivot in s:
            # Unpacking without brackets
            duration_str, base_str = s.split(pivot, 1)
            delta_args = extract_delta(duration_str)
            if delta_args:
                base_date = parse(base_str, today=today)
                multiplier = -1 if "before" in pivot else 1
                kwargs = {k: v * multiplier for k, v in delta_args.items()}
                return base_date + relativedelta(**kwargs)  # type: ignore

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
    words = s.split()
    if len(words) == 2:
        # Unpacking without brackets
        modifier, day_name = words
        if modifier in ("next", "last") and day_name in weekdays:
            target_weekday = weekdays[day_name]
            current_weekday = today.weekday()

            if modifier == "next":
                days_diff = (target_weekday - current_weekday + 7) % 7
                if days_diff == 0:
                    days_diff = 7
                return today + timedelta(days=days_diff)
            else:  # last
                days_diff = (current_weekday - target_weekday + 7) % 7
                if days_diff == 0:
                    days_diff = 7
                return today - timedelta(days=days_diff)

    # 4. Absolute date fallback
    try:
        default_dt = datetime.combine(today, datetime.min.time())
        return du_parse(s, default=default_dt).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s}")
