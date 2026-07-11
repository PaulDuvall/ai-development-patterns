"""Traceable tests for subscription reminder selection."""

import unittest

from src.subscription_reminders import reminder_is_due


class SubscriptionReminderTests(unittest.TestCase):
    """Exercise the two acceptance criteria with the standard library."""

    def test_seven_day_reminder_is_due(self):
        """Verifies: specs/subscription-reminders.md#AC-001"""
        self.assertIs(reminder_is_due(7), True)

    def test_other_day_reminder_is_not_due(self):
        """Verifies: specs/subscription-reminders.md#AC-002"""
        self.assertIs(reminder_is_due(6), False)
