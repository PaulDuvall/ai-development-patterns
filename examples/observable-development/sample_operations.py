"""Sample operations demonstrating the observability fitness function.

`charge_payment_observable` satisfies the standard; `charge_payment_blackbox`
violates it. The fitness function in `observability_fitness.py` passes the first
and flags the second — see `tests/test_observability_fitness.py`.
"""

import logging

from observable_logging import log_error, log_operation

logger = logging.getLogger(__name__)


def charge_payment_observable(amount: float, payment_method: str) -> str:
    """Charge a payment, emitting structured context at each step.

    Args:
        amount: The amount to charge.
        payment_method: The payment method identifier.

    Returns:
        A transaction identifier on success.

    Raises:
        ValueError: If the amount is not positive.
    """
    log_operation("payment_start", amount=amount, method=payment_method)
    if amount <= 0:
        error = ValueError("amount must be positive")
        log_error("payment", error, amount=amount)
        raise error
    log_operation("payment_success", amount=amount)
    return f"txn_{int(amount * 100)}"


def charge_payment_blackbox(amount: float, payment_method: str) -> str:
    """Anti-pattern: a black box that logs nothing structured.

    The fitness function flags this operation with `black_box` because it emits
    no structured log, and the raw `logger.error` call also drops the
    correlation ID.
    """
    try:
        return f"txn_{int(amount * 100)}"
    except Exception:
        logger.error("payment failed")
        raise
