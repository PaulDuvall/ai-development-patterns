"""
CLI Tests for IAM Policy Generator
=================================

Tests corresponding to cli_requirements section in iam_policy_spec.md
Validates command-line interface behavior and exit codes.
"""

import pytest
import subprocess
import sys
import json
from pathlib import Path

# Get the path to the IAM policy generator script
SCRIPT_PATH = Path(__file__).parent.parent / "iam_policy_generator.py"


class TestCLIRequirements:
    """Test CLI requirements from specification section {#cli_requirements}"""
    
    def test_policy_type_flag(self):
        """Test --policy-type flag acceptance [^test_cli_policy_type]"""
        # Test valid policy type
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read",
            "--resource", "arn:aws:s3:::test-bucket/*"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Verify policy is generated
        output = json.loads(result.stdout)
        assert "policy" in output or "Version" in output
    
    def test_resource_flag(self):
        """Test --resource flag acceptance [^test_cli_resource]"""
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read", 
            "--resource", "arn:aws:s3:::my-bucket/my-object"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Verify resource is included in policy
        output = json.loads(result.stdout)
        policy_json = json.dumps(output)
        assert "arn:aws:s3:::my-bucket/my-object" in policy_json
    
    def test_exit_codes(self):
        """Test exit codes for success and validation errors [^test_exit_codes]"""
        # Test success case (exit code 0)
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read",
            "--resource", "arn:aws:s3:::valid-bucket/*"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Test validation error (exit code 1)
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "invalid-type",
            "--resource", "arn:aws:s3:::test-bucket/*"
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        
        # Test missing required argument (should fail)
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read"
            # Missing --resource flag
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
    
    def test_help_display(self):
        """Test help information display [^test_cli_help]"""
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--policy-type" in result.stdout
        assert "--resource" in result.stdout
        assert "Examples:" in result.stdout
    
    def test_compact_flag(self):
        """Test --compact flag for JSON output formatting"""
        # Test normal output (with indentation)
        result_normal = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read",
            "--resource", "arn:aws:s3:::test-bucket/*"
        ], capture_output=True, text=True)
        
        # Test compact output
        result_compact = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read", 
            "--resource", "arn:aws:s3:::test-bucket/*",
            "--compact"
        ], capture_output=True, text=True)
        
        assert result_normal.returncode == 0
        assert result_compact.returncode == 0
        
        # Compact output should be shorter (no indentation)
        assert len(result_compact.stdout) < len(result_normal.stdout)
        
        # Both should be valid JSON
        json.loads(result_normal.stdout)
        json.loads(result_compact.stdout)
    
    def test_missing_required_arguments(self):
        """Test behavior when required arguments are missing"""
        # Missing both arguments
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH)
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()
        
        # Missing resource argument
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
    
    def test_policy_validation_in_output(self):
        """Test that output includes policy validation when requested"""
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read",
            "--resource", "arn:aws:s3:::test-bucket/*"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        
        # Should include validation metadata by default
        assert "metadata" in output or "validation_status" in json.dumps(output)
    
    def test_no_validation_info_flag(self):
        """Test --no-validation-info flag excludes metadata"""
        result = subprocess.run([
            sys.executable, str(SCRIPT_PATH),
            "--policy-type", "s3-read",
            "--resource", "arn:aws:s3:::test-bucket/*",
            "--no-validation-info"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        
        # Should not include validation metadata
        output_str = json.dumps(output)
        assert "metadata" not in output_str and "validation_status" not in output_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])