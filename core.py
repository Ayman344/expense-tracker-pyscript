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


# ----------------------------------------------------------------------------
# Monthly budget goals (issue #5)
# ----------------------------------------------------------------------------
WARNING_RATIO = 0.8        # 80% of the budget -> warning
_STATUS_RANK = {"none": 0, "ok": 1, "warning": 2, "over": 3}


def month_spent(transactions, month):
    """Expense total per category for a month ('YYYY-MM')."""
    totals = {}
    for t in transactions:
        if t["type"] == "expense" and t["date"].startswith(month):
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]
    return {cat: round(amount, 2) for cat, amount in totals.items()}


def budget_status(spent, budget):
    """'none' (no budget), 'ok' (<80%), 'warning' (80-100%), 'over' (>100%)."""
    if not budget or budget <= 0:
        return "none"
    ratio = spent / budget
    if ratio > 1:
        return "over"
    if ratio >= WARNING_RATIO:
        return "warning"
    return "ok"


def budget_alerts(transactions, budgets, month):
    """Categories at 'warning' or 'over' for a month, worst first.
    Each item: (category, spent, budget, status)."""
    spent = month_spent(transactions, month)
    alerts = []
    for cat, budget in budgets.items():
        status = budget_status(spent.get(cat, 0), budget)
        if status in ("warning", "over"):
            alerts.append((cat, spent.get(cat, 0), budget, status))
    alerts.sort(key=lambda a: (-_STATUS_RANK[a[3]], -(a[1] / a[2])))
    return alerts


def crossed_threshold(spent_before, spent_after, budget):
    """New status ('warning' or 'over') if spending moved into a worse
    status; otherwise None. Used to show a message after adding an expense."""
    before = budget_status(spent_before, budget)
    after = budget_status(spent_after, budget)
    if after in ("warning", "over") and _STATUS_RANK[after] > _STATUS_RANK[before]:
        return after
    return None
