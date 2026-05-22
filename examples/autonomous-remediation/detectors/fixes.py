"""Prescribed-fix hints and report formatter for the LLM remediator."""
from __future__ import annotations

FIX_HINTS = {
    "complexity":      "Use extract-method, early returns, guard clauses, or lookup tables.",
    "long_function":   "Extract helper functions for distinct logical steps.",
    "deep_nesting":    "Use guard clauses and early returns to flatten control flow.",
    "duplicate_block": "Extract repeated code into a shared helper function.",
    "vuln_dependency": "Upgrade to the patched version listed in the advisory.",
    "secret_leak":     "Move the value to a secret manager and reference via env var.",
}


def format_report(file_path: str, violations: list[dict], hints: dict[str, str]) -> str:
    lines = [f"{len(violations)} violation(s) in {file_path}:", ""]
    for v in violations:
        rule_id = v["rule_id"]
        lines.append(f"  [{rule_id.upper()}] line {v['line']}: {v['message']}")
        hint = hints.get(rule_id)
        if hint:
            lines.append(f"    → {hint}")
    lines.append("")
    lines.append("Fix these violations and re-save the file.")
    return "\n".join(lines)
