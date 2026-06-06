"""Tests for the observability fitness function (computational sensor)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sample_operations  # noqa: E402
from observability_fitness import (  # noqa: E402
    audit_module,
    emits_structured_log,
    propagates_correlation_id,
    public_operations,
)


def test_public_operations_lists_both_samples():
    names = {fn.__name__ for fn in public_operations(sample_operations)}
    assert {"charge_payment_observable", "charge_payment_blackbox"} <= names


def test_observable_operation_passes_both_checks():
    fn = sample_operations.charge_payment_observable
    assert emits_structured_log(fn)
    assert propagates_correlation_id(fn)


def test_blackbox_operation_is_flagged():
    fn = sample_operations.charge_payment_blackbox
    assert not emits_structured_log(fn)
    assert not propagates_correlation_id(fn)


def test_audit_reports_only_the_blackbox():
    violations = audit_module(sample_operations)
    flagged = {v["operation"]: v["failed"] for v in violations}
    assert "charge_payment_observable" not in flagged
    assert flagged["charge_payment_blackbox"] == ["black_box", "drops_correlation_id"]


def test_fitness_function_as_a_gate():
    """The shape a CI gate would take: assert no operation is a black box."""
    observable = sample_operations.charge_payment_observable
    for fn in public_operations(sample_operations):
        if fn is observable:
            assert not _failed(fn), f"{fn.__name__} unexpectedly failed"


def _failed(fn):
    return not (emits_structured_log(fn) and propagates_correlation_id(fn))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
