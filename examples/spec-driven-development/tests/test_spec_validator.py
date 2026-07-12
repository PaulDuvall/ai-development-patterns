"""Regression tests for executable specification traceability."""

from pathlib import Path
import sys

import pytest


EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXAMPLE_ROOT))

import spec_validator as validator_module  # noqa: E402
from spec_validator import SpecificationValidator  # noqa: E402


def write_test_project(
    root: Path,
    *,
    reference: str,
    requirement_id: str = "REQ-001",
    test_source: str | None = None,
) -> tuple[Path, Path]:
    """Create a minimal specification and collectable pytest directory."""
    tests_dir = root / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").write_text(
        test_source
        or (
            "class TestExample:\n"
            "    def test_present(self):\n"
            f'        \"\"\"{requirement_id}: covered behavior.\"\"\"\n'
            "        assert True\n"
        ),
        encoding="utf-8",
    )
    specification = root / "example.md"
    specification.write_text(
        "## Contract {#contract authority=system}\n"
        f"- **{requirement_id}**: The implementation MUST behave. "
        "[^test_behavior]\n\n"
        f"[^test_behavior]: {reference}\n",
        encoding="utf-8",
    )
    return specification, tests_dir


def errors_for(results: dict, section: str = "contract") -> list[str]:
    """Return flattened validation errors for one specification section."""
    return SpecificationValidator.validation_errors(results[section])


class TestSpecificationValidator:
    def test_checked_in_spec_resolves_every_cited_pytest_node(self):
        validator = SpecificationValidator(
            EXAMPLE_ROOT / "iam_policy_spec.md",
            EXAMPLE_ROOT / "tests",
        )

        specifications = validator.extract_specifications()
        validation_results = validator.validate_test_references(specifications)

        assert set(specifications) == {
            "cli_contract",
            "input_validation",
            "policy_generation",
            "output_format",
        }
        assert sum(
            len(section["test_references"])
            for section in specifications.values()
        ) == 21
        assert all(
            not validator.validation_errors(result)
            for result in validation_results.values())
        assert sum(
            result["validated_references"]
            for result in validation_results.values()) == 21

    def test_syntax_validation_ignores_authority_examples_in_prose(self):
        validator = SpecificationValidator(
            EXAMPLE_ROOT / "user_authentication_structured.md",
            EXAMPLE_ROOT / "tests",
        )

        assert validator.validate_syntax() == []

    def test_missing_class_method_is_reported(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_example.py::TestExample::test_missing",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == [
            "Uncollected pytest node: "
            "tests/test_example.py::TestExample::test_missing"
        ]
        assert results["contract"]["validated_references"] == 0

    def test_production_node_outside_test_directory_is_rejected(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="production.py::Production::not_a_test",
        )
        (tmp_path / "production.py").write_text(
            "class Production:\n"
            "    def not_a_test(self):\n"
            '        \"\"\"REQ-001: not test evidence.\"\"\"\n'
            "        return True\n",
            encoding="utf-8",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == [
            "Test reference is outside test directory: "
            "production.py::Production::not_a_test"
        ]

    def test_cited_node_must_declare_the_same_requirement(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_example.py::TestExample::test_present",
            test_source=(
                "class TestExample:\n"
                "    def test_present(self):\n"
                '        \"\"\"REQ-002: a different requirement.\"\"\"\n'
                "        assert True\n"
            ),
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == [
            "Pytest node tests/test_example.py::TestExample::test_present "
            "does not declare REQ-001 in its docstring"
        ]

    def test_reference_must_name_a_collected_node(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_example.py",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == [
            "Test reference must name a pytest node: tests/test_example.py"
        ]

    def test_collection_failure_fails_closed(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_example.py::test_present",
            test_source="def test_present(:\n    pass\n",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert len(errors_for(results)) == 1
        assert errors_for(results)[0].startswith("Pytest collection failed:")
        assert results["contract"]["validated_references"] == 0

    def test_missing_test_directory_fails_closed(self, tmp_path):
        specification = tmp_path / "example.md"
        specification.write_text(
            "## Contract {#contract authority=system}\n"
            "- **REQ-001**: It MUST work. [^test_work]\n\n"
            "[^test_work]: tests/test_example.py::test_work\n",
            encoding="utf-8",
        )
        validator = SpecificationValidator(specification, tmp_path / "missing")

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == [
            f"Test directory not found: {tmp_path / 'missing'}"]

    def test_undefined_footnote_is_reported(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_example.py::TestExample::test_present",
        )
        specification.write_text(
            "## Contract {#contract authority=system}\n"
            "- **REQ-001**: It MUST work. [^undefined]\n",
            encoding="utf-8",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == ["Undefined test reference: [^undefined]"]

    def test_missing_file_inside_test_directory_is_reported(self, tmp_path):
        specification, tests_dir = write_test_project(
            tmp_path,
            reference="tests/test_missing.py::test_missing",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert errors_for(results) == ["Missing test file: tests/test_missing.py"]

    def test_missing_specification_returns_no_sections(self, tmp_path, capsys):
        validator = SpecificationValidator(
            tmp_path / "missing.md", tmp_path / "tests")

        assert validator.extract_specifications() == {}
        assert "Specification file not found" in capsys.readouterr().out

    def test_node_path_normalization_handles_file_and_parameter_nodes(self):
        assert SpecificationValidator._normalize_node_path([]) == ()
        assert SpecificationValidator._normalize_node_path(
            ["TestExample", "test_case[value]"]
        ) == ("TestExample", "test_case")

    def test_authority_conflict_report_identifies_precedence_gap(self):
        validator = SpecificationValidator("unused.md", "unused-tests")
        specifications = {
            "system_input": {
                "title": "Input Validation",
                "authority": "system",
                "authority_level": 3,
            },
            "feature_input": {
                "title": "Input Rules",
                "authority": "feature",
                "authority_level": 1,
            },
            "cli": {
                "title": "CLI Contract",
                "authority": "system",
                "authority_level": 3,
            },
        }

        assert validator.check_authority_conflicts(specifications) == [
            "Potential authority conflict in validation: "
            "system_input (system) vs feature_input (feature)"
        ]

    def test_coverage_report_never_reports_negative_coverage(self):
        validator = SpecificationValidator("unused.md", "unused-tests")
        specifications = {
            "linked": {"test_references": [{"id": "one"}]},
            "empty": {"test_references": []},
        }
        results = {
            "linked": {
                "validated_references": 0,
                "reference_errors": ["first failure", "second failure"],
                "unlinked_requirements": [],
                "collection_error": None,
            },
            "empty": {
                "validated_references": 0,
                "reference_errors": [],
                "unlinked_requirements": [],
                "collection_error": None,
            },
        }

        report = validator.generate_coverage_report(specifications, results)

        assert "Coverage: 0.0%" in report
        assert "Validated test references: 0" in report
        assert "Invalid test references: 1" in report
        assert "Unlinked requirements: 0" in report
        assert "⚠️ linked: 0% (0/1 references validated; " in report
        assert "❌ empty: 0% (0/0 references validated; " in report
        assert "first failure" in report

    def test_collection_failure_counts_zero_validated_references(self):
        validator = SpecificationValidator("unused.md", "unused-tests")
        specifications = {
            "contract": {"test_references": [{"id": "one"}, {"id": "two"}]}
        }
        results = {
            "contract": {
                "validated_references": 0,
                "reference_errors": [],
                "unlinked_requirements": [],
                "collection_error": "Pytest collection failed: syntax error",
            }
        }

        report = validator.generate_coverage_report(specifications, results)

        assert "Validated test references: 0" in report
        assert "Invalid test references: 2" in report
        assert "Collection failures: 1" in report
        assert "Coverage: 0.0%" in report

    def test_unlinked_requirements_do_not_reduce_valid_reference_count(self):
        validator = SpecificationValidator("unused.md", "unused-tests")
        specifications = {
            "contract": {"test_references": [{"id": "one"}]}
        }
        results = {
            "contract": {
                "validated_references": 1,
                "reference_errors": [],
                "unlinked_requirements": ["REQ-001 MUST be linked"],
                "collection_error": None,
            }
        }

        report = validator.generate_coverage_report(specifications, results)

        assert "Validated test references: 1" in report
        assert "Invalid test references: 0" in report
        assert "Unlinked requirements: 1" in report
        assert "Coverage: 100.0%" in report
        assert "Requirement has no test reference: REQ-001 MUST be linked" in report

    def test_syntax_validation_reports_missing_structure_and_bad_authority(
        self, tmp_path
    ):
        missing = SpecificationValidator(
            tmp_path / "missing.md", tmp_path / "tests")
        assert missing.validate_syntax() == [
            f"Specification file not found: {tmp_path / 'missing.md'}"
        ]

        specification = tmp_path / "bad.md"
        specification.write_text(
            "## Contract {#contract authority=invalid}\n"
            "The behavior is descriptive.\n",
            encoding="utf-8",
        )
        errors = SpecificationValidator(
            specification, tmp_path / "tests").validate_syntax()

        assert "No authority levels found" in errors
        assert "No test references found (format: [^test_id]: test/path)" in errors
        assert "No requirement strength indicators found (MUST/SHOULD/MAY)" in errors
        assert "Invalid authority level: invalid" in errors

    @pytest.mark.parametrize(
        ("content", "expected_error"),
        [
            (
                "## First {#first authority=system}\n"
                "- **REQ-001**: First MUST work. [^first]\n\n"
                "## Second {#second authority=platform}\n"
                "- **REQ-001**: Second MUST work. [^second]\n\n"
                "[^first]: tests/test_example.py::test_first\n"
                "[^second]: tests/test_example.py::test_second\n",
                "Duplicate requirement ID: REQ-001 (2 declarations)",
            ),
            (
                "## First {#duplicate authority=system}\n"
                "- **REQ-001**: First MUST work. [^first]\n\n"
                "## Second {#duplicate authority=platform}\n"
                "- **REQ-002**: Second MUST work. [^second]\n\n"
                "[^first]: tests/test_example.py::test_first\n"
                "[^second]: tests/test_example.py::test_second\n",
                "Duplicate section anchor: duplicate (2 definitions)",
            ),
            (
                "## Contract {#contract authority=system}\n"
                "- **REQ-001**: It MUST work. [^behavior]\n\n"
                "[^behavior]: tests/test_example.py::test_first\n"
                "[^behavior]: tests/test_example.py::test_second\n",
                "Duplicate footnote definition: [^behavior] (2 definitions)",
            ),
        ],
    )
    def test_syntax_rejects_duplicate_global_identifiers(
        self, content, expected_error, tmp_path
    ):
        specification = tmp_path / "duplicates.md"
        specification.write_text(content, encoding="utf-8")

        validator = SpecificationValidator(specification, tmp_path / "tests")
        errors = validator.validate_syntax()

        assert expected_error in errors
        assert validator.extract_specifications() == {}

    def test_run_validation_reports_success(self, capsys):
        validator = SpecificationValidator(
            EXAMPLE_ROOT / "iam_policy_spec.md", EXAMPLE_ROOT / "tests")

        result = validator.run_validation(
            check_coverage=True,
            check_conflicts=True,
            validate_syntax=True,
        )

        output = capsys.readouterr().out
        assert result == 0
        assert "Specification syntax is valid" in output
        assert "Coverage: 100.0%" in output
        assert "No authority conflicts detected" in output

    def test_run_validation_fails_each_requested_gate(self, monkeypatch, capsys):
        validator = SpecificationValidator("unused.md", "unused-tests")
        section = {
            "title": "Input Validation",
            "authority": "system",
            "authority_level": 3,
            "test_references": [{"id": "one"}],
            "requirements": [],
            "unlinked_requirements": [],
        }
        monkeypatch.setattr(validator, "validate_syntax", lambda: ["bad syntax"])
        monkeypatch.setattr(
            validator, "extract_specifications", lambda: {"input": section})
        monkeypatch.setattr(
            validator,
            "validate_test_references",
            lambda specifications: {"input": {
                "validated_references": 0,
                "reference_errors": ["bad test link"],
                "unlinked_requirements": [],
                "collection_error": None,
            }},
        )
        monkeypatch.setattr(
            validator,
            "check_authority_conflicts",
            lambda specifications: ["authority conflict"],
        )

        result = validator.run_validation(
            check_coverage=True,
            check_conflicts=True,
            validate_syntax=True,
        )

        output = capsys.readouterr().out
        assert result == 1
        assert "Syntax validation failed" in output
        assert "bad test link" in output
        assert "Potential authority conflicts found" in output

    def test_run_validation_fails_when_no_specifications_exist(self, capsys):
        validator = SpecificationValidator("missing.md", "missing-tests")

        assert validator.run_validation(check_coverage=True) == 1
        assert "No specifications found" in capsys.readouterr().out

    def test_cli_main_requires_a_mode(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["spec_validator.py"])

        assert validator_module.main() == 1
        assert "usage:" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "arguments",
        [
            ["--validate-syntax", str(EXAMPLE_ROOT / "iam_policy_spec.md")],
            [
                "--check-coverage",
                "--authority-conflicts",
                "--spec-file",
                str(EXAMPLE_ROOT / "iam_policy_spec.md"),
                "--test-dir",
                str(EXAMPLE_ROOT / "tests"),
            ],
        ],
    )
    def test_cli_main_runs_selected_modes(self, arguments, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["spec_validator.py", *arguments])

        assert validator_module.main() == 0
