"""Unit tests for core.py. Run from the repo root:  python -m unittest discover tests"""

import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core  # noqa: E402


class TestNthOccurrence(unittest.TestCase):
    def test_weekly_steps_seven_days(self):
        start = date(2026, 9, 21)
        self.assertEqual(core.nth_occurrence(start, "weekly", 0), date(2026, 9, 21))
        self.assertEqual(core.nth_occurrence(start, "weekly", 2), date(2026, 10, 5))

    def test_monthly_same_day(self):
        self.assertEqual(core.nth_occurrence(date(2026, 1, 15), "monthly", 1), date(2026, 2, 15))

    def test_monthly_clamps_to_month_end_and_recovers(self):
        start = date(2026, 1, 31)
        self.assertEqual(core.nth_occurrence(start, "monthly", 1), date(2026, 2, 28))
        self.assertEqual(core.nth_occurrence(start, "monthly", 2), date(2026, 3, 31))
        self.assertEqual(core.nth_occurrence(start, "monthly", 3), date(2026, 4, 30))

    def test_monthly_leap_year(self):
        self.assertEqual(core.nth_occurrence(date(2028, 1, 31), "monthly", 1), date(2028, 2, 29))

    def test_monthly_crosses_year(self):
        self.assertEqual(core.nth_occurrence(date(2026, 11, 30), "monthly", 2), date(2027, 1, 30))

    def test_unknown_frequency(self):
        with self.assertRaises(ValueError):
            core.nth_occurrence(date(2026, 1, 1), "daily", 1)


class TestDueOccurrences(unittest.TestCase):
    def rule(self, **kw):
        base = {"start_date": "2026-08-05", "frequency": "monthly", "last_generated": None}
        base.update(kw)
        return base

    def test_catch_up_counts_all_past_occurrences(self):
        due = core.due_occurrences(self.rule(), date(2026, 10, 5))
        self.assertEqual(due, ["2026-08-05", "2026-09-05", "2026-10-05"])

    def test_no_duplicates_after_last_generated(self):
        rule = self.rule(last_generated="2026-10-05")
        self.assertEqual(core.due_occurrences(rule, date(2026, 10, 5)), [])

    def test_only_new_occurrences_after_last_generated(self):
        rule = self.rule(last_generated="2026-09-05")
        self.assertEqual(core.due_occurrences(rule, date(2026, 10, 20)), ["2026-10-05"])

    def test_future_start_has_nothing_due(self):
        rule = self.rule(start_date="2026-12-01")
        self.assertEqual(core.due_occurrences(rule, date(2026, 10, 5)), [])

    def test_weekly_catch_up(self):
        rule = self.rule(start_date="2026-09-21", frequency="weekly")
        self.assertEqual(len(core.due_occurrences(rule, date(2026, 10, 5))), 3)


class TestNextDue(unittest.TestCase):
    def test_next_due_after_today(self):
        rule = {"start_date": "2026-08-05", "frequency": "monthly"}
        self.assertEqual(core.next_due(rule, date(2026, 10, 5)), "2026-11-05")

    def test_next_due_future_start(self):
        rule = {"start_date": "2026-12-01", "frequency": "weekly"}
        self.assertEqual(core.next_due(rule, date(2026, 10, 5)), "2026-12-01")


def tx(cat, amount, day, kind="expense"):
    return {"category": cat, "amount": amount, "date": day, "type": kind}


class TestBudgets(unittest.TestCase):
    def test_month_spent_filters_month_and_type(self):
        rows = [tx("Food", 50, "2026-10-01"), tx("Food", 25.5, "2026-10-20"),
                tx("Food", 99, "2026-09-30"), tx("Salary", 3000, "2026-10-01", "income")]
        self.assertEqual(core.month_spent(rows, "2026-10"), {"Food": 75.5})

    def test_status_thresholds(self):
        self.assertEqual(core.budget_status(79.99, 100), "ok")
        self.assertEqual(core.budget_status(80, 100), "warning")
        self.assertEqual(core.budget_status(100, 100), "warning")
        self.assertEqual(core.budget_status(100.01, 100), "over")

    def test_no_or_zero_budget(self):
        self.assertEqual(core.budget_status(50, None), "none")
        self.assertEqual(core.budget_status(50, 0), "none")

    def test_alerts_worst_first(self):
        rows = [tx("Food", 120, "2026-10-02"), tx("Transport", 85, "2026-10-03"),
                tx("Health", 10, "2026-10-04")]
        budgets = {"Food": 100, "Transport": 100, "Health": 100}
        alerts = core.budget_alerts(rows, budgets, "2026-10")
        self.assertEqual([a[0] for a in alerts], ["Food", "Transport"])
        self.assertEqual([a[3] for a in alerts], ["over", "warning"])

    def test_crossed_threshold(self):
        self.assertEqual(core.crossed_threshold(70, 85, 100), "warning")
        self.assertEqual(core.crossed_threshold(85, 110, 100), "over")
        self.assertIsNone(core.crossed_threshold(85, 90, 100))   # still warning
        self.assertIsNone(core.crossed_threshold(10, 20, 100))   # still ok
        self.assertIsNone(core.crossed_threshold(10, 200, 0))    # no budget


if __name__ == "__main__":
    unittest.main()
