"""
Utilities for validating code examples and example directories
"""

import os
import ast
import subprocess
import tempfile
import yaml
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class CodeValidator:
    """Validator for code examples in README and example directories"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.examples_dir = self.repo_root / "examples"
        self.experiments_dir = self.repo_root / "experiments"
    
    def validate_python_syntax(self, code: str, filename: str = "<string>") -> Tuple[bool, str]:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error in {filename}: {e}"
        except Exception as e:
            return False, f"Error parsing {filename}: {e}"
    
    def validate_bash_syntax(self, code: str, filename: str = "<string>") -> Tuple[bool, str]:
        """Validate bash script syntax using bash -n"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Use bash -n to check syntax without executing
            result = subprocess.run(
                ['bash', '-n', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, f"Bash syntax error in {filename}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout validating {filename}"
        except Exception as e:
            return False, f"Error validating bash syntax in {filename}: {e}"
    
    def validate_yaml_syntax(self, code: str, filename: str = "<string>") -> Tuple[bool, str]:
        """Validate YAML syntax"""
        try:
            yaml.safe_load(code)
            return True, ""
        except yaml.YAMLError as e:
            return False, f"YAML syntax error in {filename}: {e}"
        except Exception as e:
            return False, f"Error parsing YAML in {filename}: {e}"
    
    def validate_json_syntax(self, code: str, filename: str = "<string>") -> Tuple[bool, str]:
        """Validate JSON syntax"""
        try:
            json.loads(code)
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"JSON syntax error in {filename}: {e}"
        except Exception as e:
            return False, f"Error parsing JSON in {filename}: {e}"
    
    def validate_dockerfile_syntax(self, code: str, filename: str = "<string>") -> Tuple[bool, str]:
        """Basic Dockerfile syntax validation"""
        lines = code.strip().split('\n')
        errors = []
        
        valid_instructions = {
            'FROM', 'RUN', 'CMD', 'LABEL', 'MAINTAINER', 'EXPOSE', 'ENV',
            'ADD', 'COPY', 'ENTRYPOINT', 'VOLUME', 'USER', 'WORKDIR',
            'ARG', 'ONBUILD', 'STOPSIGNAL', 'HEALTHCHECK', 'SHELL'
        }
        
        has_from = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check if line starts with valid instruction
            instruction = line.split()[0].upper()
            
            if instruction not in valid_instructions:
                errors.append(f"Line {i}: Unknown instruction '{instruction}'")
            
            if instruction == 'FROM':
                has_from = True
        
        if not has_from:
            errors.append("Dockerfile must contain at least one FROM instruction")
        
        if errors:
            return False, f"Dockerfile errors in {filename}: {'; '.join(errors)}"
        return True, ""


class ExampleDirectoryValidator:
    """Validator for example directories and their contents"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.examples_dir = self.repo_root / "examples"
        self.experiments_dir = self.repo_root / "experiments"
        self.code_validator = CodeValidator(repo_root)
    
    def validate_example_directory(self, dir_path: Path) -> Dict[str, any]:
        """Validate a complete example directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            return {
                'valid': False,
                'errors': [f"Directory does not exist: {dir_path}"],
                'warnings': []
            }
        
        errors = []
        warnings = []
        
        # Check for README.md
        readme_path = dir_path / "README.md"
        if not readme_path.exists():
            errors.append("Missing README.md in example directory")
        else:
            # Validate README content
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                if len(readme_content.strip()) < 100:
                    warnings.append("README.md seems too short for proper documentation")
                
                # Check for required sections
                required_sections = ['#', '##', '###']  # At least some headers
                if not any(section in readme_content for section in required_sections):
                    warnings.append("README.md lacks proper section headers")
                    
            except Exception as e:
                errors.append(f"Error reading README.md: {e}")
        
        # Validate all code files
        code_file_extensions = {
            '.py': self.code_validator.validate_python_syntax,
            '.sh': self.code_validator.validate_bash_syntax,
            '.yaml': self.code_validator.validate_yaml_syntax,
            '.yml': self.code_validator.validate_yaml_syntax,
            '.json': self.code_validator.validate_json_syntax
        }
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                if suffix in code_file_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        validator_func = code_file_extensions[suffix]
                        is_valid, error_msg = validator_func(content, str(file_path.relative_to(self.repo_root)))
                        
                        if not is_valid:
                            errors.append(error_msg)
                            
                    except Exception as e:
                        errors.append(f"Error reading {file_path.relative_to(self.repo_root)}: {e}")
                
                # Special case for Dockerfiles
                elif file_path.name.lower().startswith('dockerfile'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        is_valid, error_msg = self.code_validator.validate_dockerfile_syntax(
                            content, str(file_path.relative_to(self.repo_root))
                        )
                        
                        if not is_valid:
                            errors.append(error_msg)
                            
                    except Exception as e:
                        errors.append(f"Error reading {file_path.relative_to(self.repo_root)}: {e}")
        
        # Check for requirements files and validate they exist
        requirements_files = list(dir_path.glob('*requirements*.txt'))
        if requirements_files:
            for req_file in requirements_files:
                try:
                    with open(req_file, 'r', encoding='utf-8') as f:
                        requirements = f.read().strip()
                    
                    if not requirements:
                        warnings.append(f"Empty requirements file: {req_file.name}")
                    
                    # Basic format validation
                    lines = requirements.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Basic package name validation
                            if not line.replace('-', '').replace('_', '').replace('.', '').replace('>=', '').replace('==', '').replace('<=', '').replace('>', '').replace('<', '').replace('[', '').replace(']', '').replace(',', '').replace(' ', '').isalnum():
                                warnings.append(f"Potential invalid requirement on line {line_num} in {req_file.name}: {line}")
                
                except Exception as e:
                    errors.append(f"Error reading {req_file.relative_to(self.repo_root)}: {e}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'files_checked': len(list(dir_path.rglob('*'))),
            'code_files': len([f for f in dir_path.rglob('*') if f.suffix.lower() in code_file_extensions])
        }
    
    def validate_all_examples(self) -> Dict[str, Dict[str, any]]:
        """Validate all example directories"""
        results = {}
        
        # Validate main examples
        if self.examples_dir.exists():
            for example_dir in self.examples_dir.iterdir():
                if example_dir.is_dir() and not example_dir.name.startswith('.'):
                    results[f"examples/{example_dir.name}"] = self.validate_example_directory(example_dir)
        
        # Validate experimental examples
        experiments_examples_dir = self.experiments_dir / "examples"
        if experiments_examples_dir.exists():
            for example_dir in experiments_examples_dir.iterdir():
                if example_dir.is_dir() and not example_dir.name.startswith('.'):
                    results[f"experiments/examples/{example_dir.name}"] = self.validate_example_directory(example_dir)
        
        return results
    
    def check_example_completeness(self, pattern_name: str) -> Dict[str, any]:
        """Check if a pattern has a complete example implementation"""
        # Convert pattern name to directory name
        dir_name = pattern_name.lower().replace(' ', '-').replace('&', '').replace(',', '')
        dir_name = ''.join(c for c in dir_name if c.isalnum() or c == '-')
        
        example_path = self.examples_dir / dir_name
        experiment_path = self.experiments_dir / "examples" / dir_name
        
        has_main_example = example_path.exists() and example_path.is_dir()
        has_experimental = experiment_path.exists() and experiment_path.is_dir()
        
        result = {
            'pattern': pattern_name,
            'has_main_example': has_main_example,
            'has_experimental': has_experimental,
            'expected_dir_name': dir_name
        }
        
        if has_main_example:
            result['main_example_path'] = str(example_path.relative_to(self.repo_root))
        
        if has_experimental:
            result['experimental_path'] = str(experiment_path.relative_to(self.repo_root))
        
        return result


class ReadmeCodeBlockValidator:
    """Validator for code blocks within README.md"""
    
    def __init__(self, readme_content: str):
        self.readme_content = readme_content
        self.code_validator = CodeValidator(Path('.'))
    
    def extract_code_blocks(self) -> List[Dict[str, any]]:
        """Extract all code blocks from README with their languages"""
        lines = self.readme_content.split('\n')
        code_blocks = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('```'):
                language = line[3:].strip()
                start_line = i + 1
                code_lines = []
                
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):  # Found closing ```
                    code_blocks.append({
                        'language': language,
                        'code': '\n'.join(code_lines),
                        'start_line': start_line,
                        'end_line': i
                    })
            
            i += 1
        
        return code_blocks
    
    def validate_all_code_blocks(self) -> List[Dict[str, any]]:
        """Validate all code blocks in README"""
        code_blocks = self.extract_code_blocks()
        validation_results = []
        
        for block in code_blocks:
            language = block['language'].lower()
            code = block['code']
            
            if not code.strip():
                continue  # Skip empty code blocks
            
            is_valid = True
            error_msg = ""
            
            # Validate based on language
            if language in ['python', 'py']:
                is_valid, error_msg = self.code_validator.validate_python_syntax(
                    code, f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
            elif language in ['bash', 'shell', 'sh']:
                is_valid, error_msg = self.code_validator.validate_bash_syntax(
                    code, f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
            elif language in ['yaml', 'yml']:
                is_valid, error_msg = self.code_validator.validate_yaml_syntax(
                    code, f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
            elif language in ['json']:
                is_valid, error_msg = self.code_validator.validate_json_syntax(
                    code, f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
            elif language in ['dockerfile', 'docker']:
                is_valid, error_msg = self.code_validator.validate_dockerfile_syntax(
                    code, f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
            
            validation_results.append({
                'language': language,
                'start_line': block['start_line'],
                'end_line': block['end_line'],
                'is_valid': is_valid,
                'error': error_msg if not is_valid else "",
                'code_preview': code[:100] + "..." if len(code) > 100 else code
            })
        
        return validation_results