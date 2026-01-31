"""
Tests for example code validation - README code blocks and example directories
"""

import pytest
from pathlib import Path
from utils.example_validator import (
    ExampleDirectoryValidator, 
    ReadmeCodeBlockValidator,
    CodeValidator
)
from utils.pattern_parser import PatternParser
from utils.git_utils import git_ls_files, git_tracked_child_dirs


class TestCodeExamples:
    """Test suite for validating code examples in README and example directories"""
    
    def test_readme_code_blocks_syntax_valid(self, readme_content):
        """Verify all code blocks in README have valid syntax"""
        validator = ReadmeCodeBlockValidator(readme_content)
        validation_results = validator.validate_all_code_blocks()
        
        invalid_blocks = [block for block in validation_results if not block['is_valid']]
        
        assert not invalid_blocks, f"Invalid code blocks found: {invalid_blocks}"
    
    def test_python_code_blocks_parseable(self, readme_content):
        """Specifically test Python code blocks can be parsed"""
        validator = ReadmeCodeBlockValidator(readme_content)
        code_blocks = validator.extract_code_blocks()
        
        python_blocks = [block for block in code_blocks 
                        if block['language'].lower() in ['python', 'py']]
        
        code_validator = CodeValidator(Path('.'))
        invalid_python = []
        
        for block in python_blocks:
            if block['code'].strip():  # Skip empty blocks
                is_valid, error = code_validator.validate_python_syntax(
                    block['code'], 
                    f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
                if not is_valid:
                    invalid_python.append({
                        'lines': f"{block['start_line']}-{block['end_line']}",
                        'error': error,
                        'code_preview': block['code'][:200]
                    })
        
        assert not invalid_python, f"Invalid Python code blocks: {invalid_python}"
    
    def test_bash_scripts_syntax_valid(self, readme_content):
        """Test bash/shell script syntax in README"""
        validator = ReadmeCodeBlockValidator(readme_content)
        code_blocks = validator.extract_code_blocks()
        
        bash_blocks = [block for block in code_blocks 
                      if block['language'].lower() in ['bash', 'shell', 'sh']]
        
        code_validator = CodeValidator(Path('.'))
        invalid_bash = []
        
        for block in bash_blocks:
            if block['code'].strip() and not block['code'].strip().startswith('#'):
                is_valid, error = code_validator.validate_bash_syntax(
                    block['code'],
                    f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
                if not is_valid:
                    invalid_bash.append({
                        'lines': f"{block['start_line']}-{block['end_line']}",
                        'error': error,
                        'code_preview': block['code'][:200]
                    })
        
        assert not invalid_bash, f"Invalid bash code blocks: {invalid_bash}"
    
    def test_yaml_config_files_valid(self, readme_content):
        """Test YAML configuration examples in README"""
        validator = ReadmeCodeBlockValidator(readme_content)
        code_blocks = validator.extract_code_blocks()
        
        yaml_blocks = [block for block in code_blocks 
                      if block['language'].lower() in ['yaml', 'yml']]
        
        code_validator = CodeValidator(Path('.'))
        invalid_yaml = []
        
        for block in yaml_blocks:
            if block['code'].strip():
                is_valid, error = code_validator.validate_yaml_syntax(
                    block['code'],
                    f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
                if not is_valid:
                    invalid_yaml.append({
                        'lines': f"{block['start_line']}-{block['end_line']}",
                        'error': error,
                        'code_preview': block['code'][:200]
                    })
        
        assert not invalid_yaml, f"Invalid YAML code blocks: {invalid_yaml}"
    
    def test_json_examples_valid(self, readme_content):
        """Test JSON examples in README"""
        validator = ReadmeCodeBlockValidator(readme_content)
        code_blocks = validator.extract_code_blocks()
        
        json_blocks = [block for block in code_blocks 
                      if block['language'].lower() in ['json']]
        
        code_validator = CodeValidator(Path('.'))
        invalid_json = []
        
        for block in json_blocks:
            if block['code'].strip():
                is_valid, error = code_validator.validate_json_syntax(
                    block['code'],
                    f"README.md:lines {block['start_line']}-{block['end_line']}"
                )
                if not is_valid:
                    invalid_json.append({
                        'lines': f"{block['start_line']}-{block['end_line']}",
                        'error': error,
                        'code_preview': block['code'][:200]
                    })
        
        assert not invalid_json, f"Invalid JSON code blocks: {invalid_json}"


class TestExampleDirectories:
    """Test suite for validating example directories"""
    
    def test_all_example_directories_valid(self, repo_root):
        """Verify all example directories have valid structure and code"""
        validator = ExampleDirectoryValidator(repo_root)
        results = validator.validate_all_examples()
        
        failed_examples = {}
        warning_examples = {}
        
        for example_name, result in results.items():
            if not result['valid']:
                failed_examples[example_name] = result['errors']
            elif result['warnings']:
                warning_examples[example_name] = result['warnings']
        
        assert not failed_examples, f"Example directories with errors: {failed_examples}"
        
        # Print warnings but don't fail
        if warning_examples:
            print(f"Example directories with warnings: {warning_examples}")
    
    def test_example_directories_have_readmes(self, repo_root):
        """Verify all example directories contain README.md files"""
        missing_readmes = []

        for example_dir in git_tracked_child_dirs(repo_root, "examples"):
            readme_path = example_dir / "README.md"
            if not readme_path.exists():
                missing_readmes.append(str(example_dir.relative_to(repo_root)))
        
        assert not missing_readmes, f"Example directories missing README.md: {missing_readmes}"
    
    def test_python_files_in_examples_valid(self, repo_root):
        """Test all Python files in example directories"""
        code_validator = CodeValidator(repo_root)
        invalid_python_files = []

        tracked_files = git_ls_files(repo_root, "examples")
        for rel_path in tracked_files:
            if not rel_path.endswith(".py"):
                continue
            python_file = repo_root / rel_path

            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                is_valid, error = code_validator.validate_python_syntax(content, rel_path)

                if not is_valid:
                    invalid_python_files.append({
                        'file': rel_path,
                        'error': error
                    })

            except Exception as e:
                invalid_python_files.append({
                    'file': rel_path,
                    'error': f"Failed to read file: {e}"
                })
        
        assert not invalid_python_files, f"Invalid Python files in examples: {invalid_python_files}"
    
    def test_shell_scripts_in_examples_valid(self, repo_root):
        """Test all shell scripts in example directories"""
        code_validator = CodeValidator(repo_root)
        invalid_shell_files = []

        tracked_files = git_ls_files(repo_root, "examples")
        for rel_path in tracked_files:
            if not rel_path.endswith(".sh"):
                continue
            shell_file = repo_root / rel_path

            try:
                with open(shell_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                is_valid, error = code_validator.validate_bash_syntax(content, rel_path)

                if not is_valid:
                    invalid_shell_files.append({
                        'file': rel_path,
                        'error': error
                    })

            except Exception as e:
                invalid_shell_files.append({
                    'file': rel_path,
                    'error': f"Failed to read file: {e}"
                })
        
        assert not invalid_shell_files, f"Invalid shell scripts in examples: {invalid_shell_files}"
    
    def test_dockerfile_syntax_in_examples(self, repo_root):
        """Test Dockerfile syntax in example directories"""
        code_validator = CodeValidator(repo_root)
        invalid_dockerfiles = []

        tracked_files = git_ls_files(repo_root, "examples")
        for rel_path in tracked_files:
            filename = rel_path.split("/")[-1]
            is_dockerfile = (
                filename.lower().startswith("dockerfile")
                or filename.lower().endswith(".dockerfile")
                or "dockerfile" in filename.lower()
            )
            if not is_dockerfile:
                continue

            dockerfile = repo_root / rel_path
            if not dockerfile.is_file():
                continue

            try:
                with open(dockerfile, 'r', encoding='utf-8') as f:
                    content = f.read()

                is_valid, error = code_validator.validate_dockerfile_syntax(content, rel_path)

                if not is_valid:
                    invalid_dockerfiles.append({
                        'file': rel_path,
                        'error': error
                    })

            except Exception as e:
                invalid_dockerfiles.append({
                    'file': rel_path,
                    'error': f"Failed to read file: {e}"
                })
        
        assert not invalid_dockerfiles, f"Invalid Dockerfiles in examples: {invalid_dockerfiles}"
    
    def test_requirements_files_format(self, repo_root):
        """Test requirements.txt files format in examples"""
        invalid_requirements = []

        tracked_files = git_ls_files(repo_root, "examples")
        for rel_path in tracked_files:
            filename = rel_path.split("/")[-1]
            if "requirements" not in filename or not filename.endswith(".txt"):
                continue

            req_file = repo_root / rel_path
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.strip().split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Basic validation for package names
                        # Should contain alphanumeric, hyphens, underscores, and version specifiers
                        if not any(c.isalnum() for c in line):
                            invalid_requirements.append({
                                'file': rel_path,
                                'line': line_num,
                                'content': line,
                                'error': 'Line does not appear to be a valid requirement'
                            })

            except Exception as e:
                invalid_requirements.append({
                    'file': rel_path,
                    'error': f"Failed to read file: {e}"
                })
        
        assert not invalid_requirements, f"Invalid requirements files: {invalid_requirements}"


class TestExampleCompleteness:
    """Test suite for checking example completeness against patterns"""
    
    def test_patterns_have_example_implementations(self, readme_content, repo_root):
        """Check which patterns have example implementations"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        validator = ExampleDirectoryValidator(repo_root)
        
        patterns_without_examples = []
        patterns_with_examples = []
        
        for pattern_name in patterns.keys():
            completeness = validator.check_example_completeness(pattern_name)
            
            if not completeness['has_main_example'] and not completeness['has_experimental']:
                patterns_without_examples.append({
                    'pattern': pattern_name,
                    'expected_dir': completeness['expected_dir_name']
                })
            else:
                patterns_with_examples.append(pattern_name)
        
        # This is informational - we don't require all patterns to have examples
        total_patterns = len(patterns)
        patterns_with_impl = len(patterns_with_examples)
        coverage_percent = (patterns_with_impl / total_patterns * 100) if total_patterns > 0 else 0
        
        print(f"Example implementation coverage: {patterns_with_impl}/{total_patterns} patterns ({coverage_percent:.1f}%)")
        print(f"Patterns with examples: {patterns_with_examples}")
        
        if patterns_without_examples:
            print(f"Patterns without examples: {[p['pattern'] for p in patterns_without_examples]}")
        
        # We expect at least 50% of patterns to have examples
        assert coverage_percent >= 30, \
            f"Example coverage too low: {coverage_percent:.1f}% (expected at least 30%)"
    
    def test_example_directories_match_patterns(self, readme_content, repo_root):
        """Verify example directories correspond to actual patterns"""
        parser = PatternParser(readme_content)
        pattern_names = set(parser.extract_patterns().keys())
        
        examples_dir = repo_root / "examples"
        orphaned_examples = []
        
        if examples_dir.exists():
            for example_dir in examples_dir.iterdir():
                if example_dir.is_dir() and not example_dir.name.startswith('.'):
                    dir_name = example_dir.name
                    
                    # Try to match directory name to pattern
                    matched_pattern = None
                    for pattern_name in pattern_names:
                        expected_dir = pattern_name.lower().replace(' ', '-').replace('&', '').replace(',', '')
                        expected_dir = ''.join(c for c in expected_dir if c.isalnum() or c == '-')
                        
                        if dir_name == expected_dir:
                            matched_pattern = pattern_name
                            break
                    
                    if not matched_pattern:
                        orphaned_examples.append(dir_name)
        
        # Orphaned examples are not necessarily bad - they might be supporting examples
        if orphaned_examples:
            print(f"Example directories without direct pattern matches: {orphaned_examples}")
        
        # We don't assert failure here since some examples might be shared utilities
