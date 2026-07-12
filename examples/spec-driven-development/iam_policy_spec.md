# IAM Policy Generator Specification {#iam_policy_gen}

## Overview {#overview}

This executable specification defines the behavior implemented by
`iam_policy_generator.py`. Its seven normative requirements are intentionally
limited to behavior covered by the checked-in test suite; proposed capabilities
without implementation or tests do not appear as requirements.

## Definitions {#definitions}

- **Policy type**: A supported IAM action template such as `s3-read` or `ec2-admin`.
- **Resource ARN**: An identifier in the standard `aws` partition with at least six colon-separated components.
- **Policy document**: JSON containing the IAM version and one or more generated statements.

## CLI Contract {#cli_contract authority=system}

- **REQ-001**: The CLI MUST require `--policy-type` and `--resource`, display help, return zero for a valid request, and return non-zero for missing or invalid input. [^test_cli_policy_type] [^test_cli_resource] [^test_cli_help] [^test_exit_codes] [^test_missing_arguments]

## Input Validation {#input_validation authority=platform}

- **REQ-002**: The generator MUST accept only a policy type present in its reviewed template registry. [^test_policy_type_validation]
- **REQ-003**: The generator MUST reject empty, structurally incomplete, syntactically invalid, unsupported-service, or invalid general-purpose S3 bucket ARNs with an actionable error. [^test_empty_input] [^test_arn_validation] [^test_arn_components] [^test_invalid_service] [^test_s3_bucket_naming]
- **REQ-004**: The generator MUST reject a resource whose AWS service is incompatible with the selected policy type. [^test_compatibility]
- **REQ-005**: The generator MUST reject unsafe characters and values longer than 500 characters without rewriting resource identity, and JSON serialization MUST preserve every accepted resource value exactly. [^test_unsafe_input] [^test_json_round_trip]

## Policy Generation {#policy_generation authority=system}

- **REQ-006**: A generated policy MUST use IAM version `2012-10-17`; non-S3 templates MUST copy their effect and actions to the validated resource, while S3 templates MUST place bucket actions on the bucket ARN and object actions on the object ARN, constrain `ListBucket` to wildcard prefixes, and omit `ListBucket` for exact-object scope. [^test_policy_shape] [^test_s3_resource_pairing] [^test_s3_prefix_scope] [^test_s3_exact_scope]

## Output Format {#output_format authority=feature}

- **REQ-007**: Output MUST be valid JSON, support compact formatting, include validation metadata by default, and omit that metadata only when requested. [^test_compact_output] [^test_validation_status] [^test_no_validation_info]

## Evaluation Cases {#evaluation}

Each citation below names a test that exists. The traceability fitness test
checks these requirement IDs independently, while `spec_validator.py` verifies
that the cited test nodes resolve.

[^test_cli_policy_type]: tests/test_cli.py::TestCLIRequirements::test_policy_type_flag
[^test_cli_resource]: tests/test_cli.py::TestCLIRequirements::test_resource_flag
[^test_cli_help]: tests/test_cli.py::TestCLIRequirements::test_help_display
[^test_exit_codes]: tests/test_cli.py::TestCLIRequirements::test_exit_codes
[^test_missing_arguments]: tests/test_cli.py::TestCLIRequirements::test_missing_required_arguments
[^test_policy_type_validation]: tests/test_validation.py::TestInputValidation::test_policy_type_validation
[^test_empty_input]: tests/test_validation.py::TestInputValidation::test_empty_input_validation
[^test_arn_validation]: tests/test_validation.py::TestInputValidation::test_arn_format_validation
[^test_arn_components]: tests/test_validation.py::TestInputValidation::test_arn_component_validation
[^test_invalid_service]: tests/test_validation.py::TestInputValidation::test_invalid_service_names
[^test_s3_bucket_naming]: tests/test_generator_runtime.py::test_s3_generation_rejects_invalid_or_reserved_bucket_names
[^test_compatibility]: tests/test_validation.py::TestInputValidation::test_resource_policy_compatibility
[^test_unsafe_input]: tests/test_validation.py::TestInputValidation::test_unsafe_input_rejected_without_rewriting
[^test_json_round_trip]: tests/test_validation.py::TestInputValidation::test_json_serialization_preserves_accepted_resource
[^test_policy_shape]: tests/test_validation.py::TestInputValidation::test_generated_policy_matches_template
[^test_s3_resource_pairing]: tests/test_validation.py::TestInputValidation::test_s3_actions_use_matching_resource_types
[^test_s3_prefix_scope]: tests/test_validation.py::TestInputValidation::test_s3_prefix_scope_constrains_bucket_listing
[^test_s3_exact_scope]: tests/test_validation.py::TestInputValidation::test_s3_exact_object_scope_omits_bucket_listing
[^test_compact_output]: tests/test_cli.py::TestCLIRequirements::test_compact_flag
[^test_validation_status]: tests/test_cli.py::TestCLIRequirements::test_policy_validation_in_output
[^test_no_validation_info]: tests/test_cli.py::TestCLIRequirements::test_no_validation_info_flag

## Authority Conflict Resolution

When requirements conflict, system authority takes precedence over platform
authority, which takes precedence over feature authority. No conflict exists in
the current seven-requirement scope.
