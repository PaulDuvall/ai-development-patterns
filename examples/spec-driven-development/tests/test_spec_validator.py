"""Regression tests for executable specification traceability."""

from pathlib import Path
import sys


EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXAMPLE_ROOT))

from spec_validator import SpecificationValidator  # noqa: E402


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
        ) == 17
        assert all(not missing for missing in validation_results.values())

    def test_syntax_validation_ignores_authority_examples_in_prose(self):
        validator = SpecificationValidator(
            EXAMPLE_ROOT / "user_authentication_structured.md",
            EXAMPLE_ROOT / "tests",
        )

        assert validator.validate_syntax() == []

    def test_missing_class_method_is_reported(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text(
            "class TestExample:\n"
            "    def test_present(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        specification = tmp_path / "example.md"
        specification.write_text(
            "## Contract {#contract authority=system}\n"
            "- The implementation MUST behave. [^test_behavior]\n\n"
            "[^test_behavior]: "
            "tests/test_example.py::TestExample::test_missing\n",
            encoding="utf-8",
        )
        validator = SpecificationValidator(specification, tests_dir)

        results = validator.validate_test_references(
            validator.extract_specifications())

        assert results == {
            "contract": [
                "Missing test node: TestExample::test_missing "
                "in tests/test_example.py"
            ]
        }
