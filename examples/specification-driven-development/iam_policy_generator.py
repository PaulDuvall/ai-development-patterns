#!/usr/bin/env python3
"""
IAM Policy Generator - SpecDriven AI Implementation
==================================================

Command-line tool for generating AWS IAM policies based on policy type and resource specifications.
Implements the machine-readable specification defined in iam_policy_spec.md.

Usage:
    python iam_policy_generator.py --policy-type s3-read --resource arn:aws:s3:::my-bucket/*
    python iam_policy_generator.py --policy-type ec2-admin --resource arn:aws:ec2:us-east-1:123456789012:instance/*
"""

import argparse
import json
import re
import sys
import time
from typing import Dict, List, Optional, Tuple
import logging


class IAMPolicyGenerator:
    """Generates AWS IAM policies based on policy types and resource specifications"""
    
    # Policy templates with actions mapped to policy types
    POLICY_TEMPLATES = {
        "s3-read": {
            "actions": ["s3:GetObject", "s3:ListBucket"],
            "effect": "Allow",
            "description": "Read-only access to S3 resources"
        },
        "s3-write": {
            "actions": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"],
            "effect": "Allow",
            "description": "Read-write access to S3 resources"
        },
        "ec2-admin": {
            "actions": ["ec2:*"],
            "effect": "Allow",
            "description": "Full administrative access to EC2 resources"
        },
        "lambda-execute": {
            "actions": ["lambda:InvokeFunction"],
            "effect": "Allow",
            "description": "Execute Lambda functions"
        },
        "iam-read": {
            "actions": ["iam:Get*", "iam:List*"],
            "effect": "Allow",
            "description": "Read-only access to IAM resources"
        }
    }
    
    # Valid AWS service prefixes for ARN validation
    VALID_SERVICES = {
        "s3", "ec2", "lambda", "iam", "rds", "dynamodb", "sns", "sqs", 
        "cloudwatch", "logs", "apigateway", "cognito-idp", "cognito-identity"
    }
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Configure secure logging that doesn't expose sensitive information"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('iam_generator.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_policy_type(self, policy_type: str) -> Tuple[bool, Optional[str]]:
        """Validate policy type against supported templates"""
        if not policy_type:
            return False, "Policy type cannot be empty"
        
        if policy_type not in self.POLICY_TEMPLATES:
            available = ", ".join(self.POLICY_TEMPLATES.keys())
            return False, f"Unsupported policy type '{policy_type}'. Available: {available}"
        
        return True, None
    
    def validate_arn_format(self, arn: str) -> Tuple[bool, Optional[str]]:
        """Validate ARN format according to AWS ARN syntax"""
        if not arn:
            return False, "Resource ARN cannot be empty"
        
        # AWS ARN format: arn:partition:service:region:account-id:resource-type/resource-id
        arn_pattern = r'^arn:aws:[a-zA-Z0-9\-]+:[a-zA-Z0-9\-]*:[0-9]*:[a-zA-Z0-9\-\/:_]*$'
        
        if not re.match(arn_pattern, arn):
            return False, f"Invalid ARN format. Expected: arn:aws:service:region:account:resource"
        
        # Extract service from ARN
        arn_parts = arn.split(':')
        if len(arn_parts) < 6:
            return False, "ARN must have at least 6 components separated by colons"
        
        service = arn_parts[2]
        if service not in self.VALID_SERVICES:
            return False, f"Unsupported AWS service '{service}' in ARN"
        
        return True, None
    
    def check_resource_policy_compatibility(self, policy_type: str, resource_arn: str) -> Tuple[bool, Optional[str]]:
        """Check if resource ARN is compatible with policy type"""
        arn_parts = resource_arn.split(':')
        service = arn_parts[2] if len(arn_parts) > 2 else ""
        
        compatibility_map = {
            "s3-read": ["s3"],
            "s3-write": ["s3"],
            "ec2-admin": ["ec2"],
            "lambda-execute": ["lambda"],
            "iam-read": ["iam"]
        }
        
        compatible_services = compatibility_map.get(policy_type, [])
        if service not in compatible_services:
            return False, f"Policy type '{policy_type}' is not compatible with service '{service}'"
        
        return True, None
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input to prevent injection attacks"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', input_str)
        
        # Limit length to prevent DoS
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
        
        return sanitized.strip()
    
    def escape_arn_for_json(self, arn: str) -> str:
        """Escape special characters in ARN for JSON output"""
        # JSON escape characters that might appear in ARNs
        escaped = arn.replace('\\', '\\\\').replace('"', '\\"')
        return escaped
    
    def generate_policy(self, policy_type: str, resource_arn: str, compact: bool = False) -> Dict:
        """Generate IAM policy JSON based on policy type and resource"""
        start_time = time.time()
        
        # Input validation
        policy_type = self.sanitize_input(policy_type)
        resource_arn = self.sanitize_input(resource_arn)
        
        # Validate policy type
        valid_type, type_error = self.validate_policy_type(policy_type)
        if not valid_type:
            raise ValueError(f"Policy type validation failed: {type_error}")
        
        # Validate ARN format
        valid_arn, arn_error = self.validate_arn_format(resource_arn)
        if not valid_arn:
            raise ValueError(f"ARN validation failed: {arn_error}")
        
        # Check compatibility
        compatible, compat_error = self.check_resource_policy_compatibility(policy_type, resource_arn)
        if not compatible:
            raise ValueError(f"Compatibility check failed: {compat_error}")
        
        # Get policy template
        template = self.POLICY_TEMPLATES[policy_type]
        
        # Generate policy document
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": template["effect"],
                    "Action": template["actions"],
                    "Resource": self.escape_arn_for_json(resource_arn)
                }
            ]
        }
        
        # Log generation (without exposing sensitive ARN details)
        generation_time = time.time() - start_time
        self.logger.info(f"Generated {policy_type} policy in {generation_time:.3f}s")
        
        return policy
    
    def format_output(self, policy: Dict, compact: bool = False, include_validation: bool = True) -> str:
        """Format policy output as JSON with optional validation status"""
        if compact:
            json_output = json.dumps(policy, separators=(',', ':'))
        else:
            json_output = json.dumps(policy, indent=2)
        
        if include_validation:
            # Add validation metadata (not part of actual policy)
            validation_info = {
                "validation_status": "passed",
                "generator_version": "1.0.0",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
            
            output = {
                "policy": policy,
                "metadata": validation_info
            }
            
            if compact:
                return json.dumps(output, separators=(',', ':'))
            else:
                return json.dumps(output, indent=2)
        
        return json_output
    
    def handle_error(self, error: Exception, error_code: int = 1) -> Dict:
        """Handle errors with structured error response"""
        error_response = {
            "error": {
                "code": error_code,
                "message": str(error),
                "type": type(error).__name__
            }
        }
        
        # Log error securely (without exposing sensitive details)
        self.logger.error(f"Policy generation failed: {type(error).__name__}")
        
        # Provide suggestions for common errors
        error_msg = str(error).lower()
        suggestions = []
        
        if "arn" in error_msg:
            suggestions.append("Check ARN format: arn:aws:service:region:account:resource")
        if "policy type" in error_msg:
            suggestions.append(f"Valid policy types: {', '.join(self.POLICY_TEMPLATES.keys())}")
        if "compatibility" in error_msg:
            suggestions.append("Ensure policy type matches the service in your ARN")
        
        if suggestions:
            error_response["error"]["suggestions"] = suggestions
        
        return error_response


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate AWS IAM policies based on policy type and resource specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --policy-type s3-read --resource arn:aws:s3:::my-bucket/*
  %(prog)s --policy-type ec2-admin --resource arn:aws:ec2:us-east-1:123456789012:instance/*
  %(prog)s --policy-type lambda-execute --resource arn:aws:lambda:us-east-1:123456789012:function:my-function
        """
    )
    
    parser.add_argument(
        "--policy-type", 
        required=True,
        help="Type of IAM policy to generate (s3-read, s3-write, ec2-admin, lambda-execute, iam-read)"
    )
    
    parser.add_argument(
        "--resource",
        required=True, 
        help="AWS resource ARN for which to generate the policy"
    )
    
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON without indentation"
    )
    
    parser.add_argument(
        "--no-validation-info",
        action="store_true",
        help="Exclude validation metadata from output"
    )
    
    args = parser.parse_args()
    
    generator = IAMPolicyGenerator()
    
    try:
        # Generate policy
        policy = generator.generate_policy(args.policy_type, args.resource, args.compact)
        
        # Format output
        output = generator.format_output(
            policy, 
            compact=args.compact,
            include_validation=not args.no_validation_info
        )
        
        print(output)
        return 0
        
    except ValueError as e:
        # Validation errors
        error_response = generator.handle_error(e, error_code=1)
        print(json.dumps(error_response, indent=2))
        return 1
        
    except Exception as e:
        # Unexpected errors
        error_response = generator.handle_error(e, error_code=2)
        print(json.dumps(error_response, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())