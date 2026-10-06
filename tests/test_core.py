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


if __name__ == "__main__":
    unittest.main()
