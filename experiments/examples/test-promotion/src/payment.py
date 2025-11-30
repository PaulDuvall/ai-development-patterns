"""
Simple Payment Processing System

Demonstrates the Test Promotion pattern with immutable golden tests
protecting critical business logic.
"""

# In-memory transaction registry (simulates database)
_processed_transactions = set()


class DuplicateTransactionError(Exception):
    """Raised when attempting to process a transaction that was already processed."""
    pass


def process_payment(txn_id: str, amount: float) -> dict:
    """
    Process a payment transaction with idempotency protection.

    Args:
        txn_id: Unique transaction identifier
        amount: Payment amount (must be positive)

    Returns:
        dict with status, txn_id, and amount

    Raises:
        ValueError: If txn_id is empty or amount is not positive
        DuplicateTransactionError: If transaction was already processed
    """
    # Validate transaction ID
    if not txn_id or not isinstance(txn_id, str) or len(txn_id.strip()) == 0:
        raise ValueError("Transaction ID must be a non-empty string")

    # Validate amount
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Amount must be a positive number")

    # Check for duplicate transaction
    if txn_id in _processed_transactions:
        raise DuplicateTransactionError(
            f"Transaction {txn_id} was already processed"
        )

    # Process payment
    _processed_transactions.add(txn_id)

    return {
        "status": "success",
        "txn_id": txn_id,
        "amount": amount
    }


def reset_transactions():
    """Reset transaction registry (for testing only)."""
    _processed_transactions.clear()
