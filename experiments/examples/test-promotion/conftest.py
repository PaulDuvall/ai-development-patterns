"""
pytest configuration for Test Promotion example
"""

import pytest
from src.payment import reset_transactions


@pytest.fixture(autouse=True)
def reset_payment_state():
    """Reset payment state before each test."""
    reset_transactions()
    yield
    reset_transactions()
