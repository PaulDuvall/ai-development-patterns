"""
Input Validation Tests for IAM Policy Generator
==============================================

Tests corresponding to input_validation section in iam_policy_spec.md
Validates input parameter checking and ARN format validation.
"""

import pytest
from iam_policy_generator import IAMPolicyGenerator


class TestInputValidation:
    """Test input validation requirements from specification section {#input_validation}"""
    
    def setup_method(self):
        """Set up test instance"""
        self.generator = IAMPolicyGenerator()
    
    def test_invalid_service_names(self):
        """REQ-003: Reject unsupported AWS service names."""
        invalid_arns = [
            "arn:aws:invalid-service:us-east-1:123456789012:resource/*",
            "arn:aws:fake:us-east-1:123456789012:resource/*",
            "arn:aws:notreal:us-east-1:123456789012:resource/*"
        ]
        
        for arn in invalid_arns:
            valid, error = self.generator.validate_arn_format(arn)
            assert not valid
            assert "Unsupported AWS service" in error
            assert "invalid" in error.lower() or "fake" in error.lower() or "notreal" in error.lower()
    
    def test_arn_format_validation(self):
        """REQ-003: Accept valid ARN shapes and reject invalid ones."""
        # Valid ARNs
        valid_arns = [
            "arn:aws:s3:::my-bucket/*",
            "arn:aws:s3:::my-bucket/my-object",
            "arn:aws:ec2:us-east-1:123456789012:instance/*",
            "arn:aws:lambda:us-west-2:123456789012:function:my-function",
            "arn:aws:iam::123456789012:role/my-role"
        ]
        
        for arn in valid_arns:
            valid, error = self.generator.validate_arn_format(arn)
            assert valid, f"ARN should be valid: {arn}, error: {error}"
        
        # Invalid ARNs
        invalid_arns = [
            "not-an-arn",
            "arn:invalid:s3:::bucket",
            "arn:aws:s3",  # Too short
            "invalid:format:here",
            "",  # Empty
            "arn:aws:s3:::bucket with spaces/*",  # Invalid characters
        ]
        
        for arn in invalid_arns:
            valid, error = self.generator.validate_arn_format(arn)
            assert not valid, f"ARN should be invalid: {arn}"
            assert error is not None
    
    def test_policy_type_validation(self):
        """REQ-002: Accept only policy types in the template registry."""
        # Valid policy types
        valid_types = ["s3-read", "s3-write", "ec2-admin", "lambda-execute", "iam-read"]
        
        for policy_type in valid_types:
            valid, error = self.generator.validate_policy_type(policy_type)
            assert valid, f"Policy type should be valid: {policy_type}, error: {error}"
        
        # Invalid policy types
        invalid_types = ["invalid-type", "s3-invalid", "", None]
        
        for policy_type in invalid_types:
            valid, error = self.generator.validate_policy_type(policy_type)
            assert not valid, f"Policy type should be invalid: {policy_type}"
            if policy_type:  # Skip None for error message check
                assert "Unsupported policy type" in error
    
    def test_resource_policy_compatibility(self):
        """REQ-004: Enforce resource-service and policy compatibility."""
        # Compatible combinations
        compatible_pairs = [
            ("s3-read", "arn:aws:s3:::my-bucket/*"),
            ("s3-write", "arn:aws:s3:::my-bucket/object"),
            ("ec2-admin", "arn:aws:ec2:us-east-1:123456789012:instance/*"),
            ("lambda-execute", "arn:aws:lambda:us-east-1:123456789012:function:my-func"),
            ("iam-read", "arn:aws:iam::123456789012:role/my-role")
        ]
        
        for policy_type, arn in compatible_pairs:
            compatible, error = self.generator.check_resource_policy_compatibility(policy_type, arn)
            assert compatible, f"Should be compatible: {policy_type} with {arn}, error: {error}"
        
        # Incompatible combinations
        incompatible_pairs = [
            ("s3-read", "arn:aws:ec2:us-east-1:123456789012:instance/*"),
            ("ec2-admin", "arn:aws:s3:::my-bucket/*"),
            ("lambda-execute", "arn:aws:s3:::my-bucket/*"),
            ("iam-read", "arn:aws:ec2:us-east-1:123456789012:instance/*")
        ]
        
        for policy_type, arn in incompatible_pairs:
            compatible, error = self.generator.check_resource_policy_compatibility(policy_type, arn)
            assert not compatible, f"Should be incompatible: {policy_type} with {arn}"
            assert "not compatible" in error
    
    def test_empty_input_validation(self):
        """REQ-002 REQ-003: Reject empty policy types and ARNs."""
        # Empty policy type
        valid, error = self.generator.validate_policy_type("")
        assert not valid
        assert "cannot be empty" in error
        
        # Empty ARN
        valid, error = self.generator.validate_arn_format("")
        assert not valid
        assert "cannot be empty" in error
    
    def test_arn_component_validation(self):
        """REQ-003: Report incomplete ARN component structure clearly."""
        # ARN with insufficient components
        invalid_arn = "arn:aws:s3"
        valid, error = self.generator.validate_arn_format(invalid_arn)
        assert not valid
        assert "6 components" in error
        
        # ARN with valid component count but invalid service
        invalid_service_arn = "arn:aws:invalidservice:us-east-1:123456789012:resource"
        valid, error = self.generator.validate_arn_format(invalid_service_arn)
        assert not valid
        assert "Unsupported AWS service" in error
    
    def test_input_sanitization(self):
        """REQ-005: Remove unsafe characters and bound input length."""
        malicious_inputs = [
            "s3-read'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            'policy-type">&lt;script&gt;',
            "input with \"quotes\" and 'apostrophes'",
            "very_long_" + "a" * 1000 + "_input"  # Very long input
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = self.generator.sanitize_input(malicious_input)
            
            # Should not contain dangerous characters
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert '"' not in sanitized
            assert "'" not in sanitized
            assert ";" not in sanitized
            
            # Should be length-limited
            assert len(sanitized) <= 500
    
    def test_arn_escaping(self):
        """REQ-005: Escape ARN quotes and backslashes for JSON."""
        test_arns = [
            'arn:aws:s3:::bucket-with-"quotes"/*',
            'arn:aws:s3:::bucket\\with\\backslashes/*',
            'arn:aws:s3:::normal-bucket/*'
        ]
        
        for arn in test_arns:
            escaped = self.generator.escape_arn_for_json(arn)
            
            # Should escape backslashes and quotes
            if '\\' in arn:
                assert '\\\\' in escaped
            if '"' in arn:
                assert '\\"' in escaped
            
            # Should be valid when used in JSON
            import json
            test_json = json.dumps({"resource": escaped})
            parsed = json.loads(test_json)
            assert "resource" in parsed

    def test_generated_policy_matches_template(self):
        """REQ-006: Copy reviewed template fields into an IAM statement."""
        policy = self.generator.generate_policy(
            "s3-read", "arn:aws:s3:::example-bucket/*")

        assert policy["Version"] == "2012-10-17"
        assert policy["Statement"] == [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "arn:aws:s3:::example-bucket/*",
        }]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
