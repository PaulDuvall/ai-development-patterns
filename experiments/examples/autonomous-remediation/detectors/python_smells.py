"""AST-based detectors for cyclomatic complexity, long functions, deep nesting."""
from __future__ import annotations

import ast


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    nest_types = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith)
    if isinstance(node, nest_types):
        depth += 1
    best = depth
    for child in ast.iter_child_nodes(node):
        best = max(best, _max_nesting(child, depth))
    return best


def _complexity(node: ast.AST) -> int:
    score = 1
    branch_types = (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.With)
    for child in ast.walk(node):
        if isinstance(child, branch_types):
            score += 1
    return score


def _function_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    if not node.body:
        return 0
    return node.body[-1].end_lineno - node.lineno


def _finding(rule_id: str, file_path: str, func: ast.AST, message: str) -> dict:
    return {
        "rule_id": rule_id, "file": file_path, "line": func.lineno,
        "severity": "warning", "message": message,
    }


def _check_function(func: ast.AST, cfg: dict, file_path: str) -> list[dict]:
    findings: list[dict] = []
    length, cx, nest = _function_length(func), _complexity(func), _max_nesting(func)
    max_len = cfg.get("max_function_length", 20)
    max_cx = cfg.get("max_complexity", 10)
    max_nest = cfg.get("max_nesting", 3)

    if length > max_len:
        findings.append(_finding("long_function", file_path, func,
            f"function '{func.name}' is {length} lines (max {max_len})"))
    if cx > max_cx:
        findings.append(_finding("complexity", file_path, func,
            f"function '{func.name}' has cyclomatic complexity {cx} (max {max_cx})"))
    if nest > max_nest:
        findings.append(_finding("deep_nesting", file_path, func,
            f"function '{func.name}' nests {nest} levels deep (max {max_nest})"))
    return findings


def detect(file_path: str, cfg: dict) -> list[dict]:
    try:
        source = open(file_path, encoding="utf-8").read()
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        print(f"python_smells: could not parse {file_path} ({exc})", flush=True)
        return []

    findings: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            findings.extend(_check_function(node, cfg, file_path))
    return findings
