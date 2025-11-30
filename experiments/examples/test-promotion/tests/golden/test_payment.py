"""
Golden Test: Payment Idempotency

This test is IMMUTABLE (444 permissions).
AI cannot modify this file - it serves as a behavioral contract.

Tests that duplicate payment transactions are properly rejected.
"""

import pytest
from src.payment import process_payment, DuplicateTransactionError


def test_payment_idempotency():
    """Payment processing MUST prevent duplicate charges for same transaction ID."""
    # First payment should succeed
    result = process_payment(txn_id="TXN-123", amount=100.00)
    assert result["status"] == "success"
    assert result["amount"] == 100.00

    # Duplicate payment MUST raise error
    with pytest.raises(DuplicateTransactionError) as exc_info:
        process_payment(txn_id="TXN-123", amount=100.00)

    assert "already processed" in str(exc_info.value).lower()


def test_payment_validation():
    """Payment MUST validate amount is positive."""
    with pytest.raises(ValueError) as exc_info:
        process_payment(txn_id="TXN-456", amount=-50.00)

    assert "positive" in str(exc_info.value).lower()


def test_payment_requires_transaction_id():
    """Payment MUST require valid transaction ID."""
    with pytest.raises(ValueError) as exc_info:
        process_payment(txn_id="", amount=100.00)

    assert "transaction id" in str(exc_info.value).lower()
