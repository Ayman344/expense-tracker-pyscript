"""
core.py — pure Python logic for PyExpense (no browser / PyScript imports).

Keeping this logic separate means it can be unit-tested with plain Python
(`python -m unittest discover tests`) and also loaded by PyScript in the browser.
"""

import calendar
from datetime import date, timedelta

FREQUENCIES = ("weekly", "monthly")
_MAX_OCCURRENCES = 1000   # safety cap for very old start dates


# ----------------------------------------------------------------------------
# Recurring transactions (issue #4)
# ----------------------------------------------------------------------------
def nth_occurrence(start, frequency, n):
    """Return the n-th occurrence (n = 0 is the start date).

    weekly  -> start + 7*n days
    monthly -> same day-of-month as `start`, n months later, clamped to the
               last day of short months (Jan 31 -> Feb 28 -> Mar 31).
    """
    if frequency == "weekly":
        return start + timedelta(days=7 * n)
    if frequency == "monthly":
        month_index = start.month - 1 + n
        year = start.year + month_index // 12
        month = month_index % 12 + 1
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, min(start.day, last_day))
    raise ValueError(f"unknown frequency: {frequency!r}")


def due_occurrences(rule, today):
    """Dates (ISO strings) of a rule's occurrences that are due but not yet
    generated: after `rule['last_generated']` (if any) and on/before `today`."""
    start = date.fromisoformat(rule["start_date"])
    last = rule.get("last_generated")
    last = date.fromisoformat(last) if last else None

    due = []
    for n in range(_MAX_OCCURRENCES):
        occ = nth_occurrence(start, rule["frequency"], n)
        if occ > today:
            break
        if last is None or occ > last:
            due.append(occ.isoformat())
    return due


def next_due(rule, today):
    """The first occurrence strictly after `today` (ISO string)."""
    start = date.fromisoformat(rule["start_date"])
    for n in range(_MAX_OCCURRENCES):
        occ = nth_occurrence(start, rule["frequency"], n)
        if occ > today:
            return occ.isoformat()
    return None
