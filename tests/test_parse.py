from datetime import date
import pytest
from src.nldate import parse


def test_today():
    ref = date(2026, 5, 14)
    assert parse("today", today=ref) == ref


def test_tomorrow():
    ref = date(2026, 5, 14)
    assert parse("tomorrow", today=ref) == date(2026, 5, 15)


def test_yesterday():
    ref = date(2026, 5, 14)
    assert parse("yesterday", today=ref) == date(2026, 5, 13)


def test_absolute_date():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_next_tuesday():
    ref = date(2026, 5, 14)  # Thursday
    assert parse("next Tuesday", today=ref) == date(2026, 5, 19)


def test_days_before():
    ref = date(2025, 12, 1)
    assert parse("5 days before December 1st, 2025", today=ref) == date(2025, 11, 26)


def test_weeks_from_tomorrow():
    ref = date(2026, 5, 14)
    # Tomorrow is May 15. Two weeks from then is May 29.
    assert parse("two weeks from tomorrow", today=ref) == date(2026, 5, 29)


def test_month_after():
    ref = date(2025, 1, 1)
    assert parse("1 month after January 1st, 2025", today=ref) == date(2025, 2, 1)


def test_in_three_days():
    ref = date(2026, 5, 14)
    # Falls into the dateutil fallback which handles "in X days"
    assert parse("in 3 days", today=ref) == date(2026, 5, 17)


def test_invalid_input():
    with pytest.raises(ValueError):
        parse("not a real date at all")
