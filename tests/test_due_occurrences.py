"""Tests for core.due_occurrences (Assignment 3).

Generated with an AI coding tool (Claude Code), then reviewed by hand.
Review changes: exact-list assertions instead of weak checks (today boundary,
empty last_generated); added last_generated-after-today and before-start cases;
renamed and documented the safety-cap test, which exposes a known limitation.
Run from the repo root:  python -m unittest discover -s tests
"""

import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import due_occurrences  # noqa: E402


def rule(start, frequency="monthly", last_generated=None):
    return {"start_date": start, "frequency": frequency, "last_generated": last_generated}


class TestCatchUp(unittest.TestCase):
    """Normal cases: all missed occurrences up to today are returned."""

    def test_monthly_catch_up_from_past_start(self):
        result = due_occurrences(rule("2026-07-15"), date(2026, 10, 5))
        self.assertEqual(result, ["2026-07-15", "2026-08-15", "2026-09-15"])

    def test_weekly_catch_up(self):
        result = due_occurrences(rule("2026-09-07", "weekly"), date(2026, 10, 5))
        self.assertEqual(result, ["2026-09-07", "2026-09-14", "2026-09-21",
                                  "2026-09-28", "2026-10-05"])

    def test_results_are_iso_strings_in_ascending_order(self):
        result = due_occurrences(rule("2026-01-10"), date(2026, 6, 30))
        self.assertTrue(all(isinstance(d, str) for d in result))
        self.assertEqual(result, sorted(result))
        self.assertEqual(len(result), 6)


class TestTodayBoundary(unittest.TestCase):
    """Edge cases around 'today'."""

    def test_occurrence_on_today_is_included(self):
        result = due_occurrences(rule("2026-09-05"), date(2026, 10, 5))
        self.assertEqual(result, ["2026-09-05", "2026-10-05"])

    def test_start_equal_to_today_returns_today(self):
        self.assertEqual(due_occurrences(rule("2026-10-05"), date(2026, 10, 5)), ["2026-10-05"])

    def test_future_start_returns_empty_list(self):
        self.assertEqual(due_occurrences(rule("2026-10-06"), date(2026, 10, 5)), [])


class TestLastGenerated(unittest.TestCase):
    """No duplicates: dates on/before last_generated are skipped."""

    def test_last_generated_equal_to_latest_returns_empty(self):
        r = rule("2026-08-05", last_generated="2026-10-05")
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)), [])

    def test_only_occurrences_after_last_generated(self):
        r = rule("2026-07-15", last_generated="2026-08-20")
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)), ["2026-09-15"])

    def test_missing_last_generated_key_means_nothing_generated(self):
        r = {"start_date": "2026-08-05", "frequency": "monthly"}
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)),
                         ["2026-08-05", "2026-09-05", "2026-10-05"])

    def test_empty_last_generated_means_nothing_generated(self):
        r = rule("2026-08-05", last_generated="")
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)),
                         ["2026-08-05", "2026-09-05", "2026-10-05"])

    def test_last_generated_after_today_returns_empty(self):
        # e.g. the device clock was moved back after entries were generated
        r = rule("2026-08-05", last_generated="2026-12-05")
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)), [])

    def test_last_generated_before_start_returns_all(self):
        r = rule("2026-08-05", last_generated="2026-01-01")
        self.assertEqual(due_occurrences(r, date(2026, 10, 5)),
                         ["2026-08-05", "2026-09-05", "2026-10-05"])

    def test_rule_is_not_modified(self):
        r = rule("2026-08-05", last_generated="2026-09-05")
        before = dict(r)
        due_occurrences(r, date(2026, 10, 5))
        self.assertEqual(r, before)


class TestCalendarEdges(unittest.TestCase):
    """Month-end clamping and leap years."""

    def test_month_end_clamping_sequence(self):
        result = due_occurrences(rule("2026-01-31"), date(2026, 4, 30))
        self.assertEqual(result, ["2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30"])

    def test_leap_year_february(self):
        result = due_occurrences(rule("2028-01-31"), date(2028, 3, 1))
        self.assertEqual(result, ["2028-01-31", "2028-02-29"])


class TestLimitsAndErrors(unittest.TestCase):
    """Safety cap and invalid input."""

    def test_safety_cap_returns_at_most_1000_dates(self):
        # Known limitation (found in review): the loop stops after 1000 steps, so a
        # weekly rule started in 1990 returns 1990-2009 and never reaches today.
        # This test documents the current contract; the limitation is in the backlog.
        result = due_occurrences(rule("1990-01-01", "weekly"), date(2026, 10, 5))
        self.assertEqual(len(result), 1000)
        self.assertEqual(result[0], "1990-01-01")
        self.assertLess(result[-1], "2026-10-05")

    def test_unknown_frequency_raises_value_error(self):
        with self.assertRaises(ValueError):
            due_occurrences(rule("2026-08-05", "daily"), date(2026, 10, 5))


if __name__ == "__main__":
    unittest.main()
