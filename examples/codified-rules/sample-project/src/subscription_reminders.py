"""Select subscriptions that need a seven-day reminder."""


def reminder_is_due(days_until_charge):
    """Return whether the subscription needs its scheduled reminder."""
    # Implements: specs/subscription-reminders.md#AC-001
    # Implements: specs/subscription-reminders.md#AC-002
    return days_until_charge == 7
