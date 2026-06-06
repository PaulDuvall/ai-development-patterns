"""Observability fitness function (computational sensor).

The deterministic half of the Observable Development feedback loop. It statically
verifies that every public operation in a module satisfies the observability
standard in `.ai/rules/observability.md`:

    * it emits at least one structured log (not a black box), and
    * it does not bypass the structured helpers with a raw logger/print call
      that would drop the correlation ID.

It answers "is it logged?" in milliseconds and reliably. The complementary
"is it useful?" question is answered probabilistically by `log_quality_judge.py`.
"""

import ast
import inspect
from types import ModuleType
from typing import Callable

# Structured helpers that embed correlation_id (see observable_logging.py).
STRUCTURED_LOG_FUNCS = frozenset({"log_operation", "log_error", "log_performance"})

# Raw sinks that bypass structured context and drop the correlation ID.
RAW_LOG_METHODS = frozenset({"debug", "info", "warning", "warn", "error", "critical"})


def public_operations(module: ModuleType) -> list[Callable]:
    """Return the module's own public functions (operations to regulate).

    Args:
        module: The imported module to inspect.

    Returns:
        Functions defined in `module` whose names do not start with an underscore.
    """
    return [
        obj
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__ and not name.startswith("_")
    ]


def _called_names(fn: Callable) -> list[ast.Call]:
    """Parse `fn`'s source and return every call node in its body."""
    tree = ast.parse(inspect.getsource(fn))
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def emits_structured_log(fn: Callable) -> bool:
    """Return True if `fn` makes at least one structured log call."""
    return any(_is_structured_call(call) for call in _called_names(fn))


def propagates_correlation_id(fn: Callable) -> bool:
    """Return True unless `fn` makes a raw log/print call that drops the ID."""
    return not any(_is_raw_log_call(call) for call in _called_names(fn))


def _is_structured_call(call: ast.Call) -> bool:
    """True if the call targets a structured log helper by name."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id in STRUCTURED_LOG_FUNCS
    return isinstance(func, ast.Attribute) and func.attr in STRUCTURED_LOG_FUNCS


def _is_raw_log_call(call: ast.Call) -> bool:
    """True if the call is a bare print() or logger.<level>() sink."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id == "print"
    return isinstance(func, ast.Attribute) and func.attr in RAW_LOG_METHODS


def audit_module(module: ModuleType) -> list[dict]:
    """Return a violation report for every non-observable operation in `module`.

    Args:
        module: The imported module to audit.

    Returns:
        One dict per offending function with its name and the failed checks.
        An empty list means the module passes the fitness function.
    """
    violations = []
    for fn in public_operations(module):
        failed = _failed_checks(fn)
        if failed:
            violations.append({"operation": fn.__name__, "failed": failed})
    return violations


def _failed_checks(fn: Callable) -> list[str]:
    """Return the names of the observability checks `fn` fails."""
    failed = []
    if not emits_structured_log(fn):
        failed.append("black_box")
    if not propagates_correlation_id(fn):
        failed.append("drops_correlation_id")
    return failed
