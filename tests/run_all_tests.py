#!/usr/bin/env python3
"""
Comprehensive test runner with detailed reporting for AI Development Patterns validation
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class PatternTestRunner:
    """Comprehensive test runner for pattern validation"""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.tests_dir = self.repo_root / "tests"
        self.results_dir = self.tests_dir / "test-results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Test suites configuration
        self.test_suites = {
            'pattern_compliance': {
                'name': 'Pattern Specification Compliance',
                'module': 'test_pattern_compliance.py',
                'description': 'Validates patterns against pattern-spec.md requirements',
                'critical': True
            },
            'readme_accuracy': {
                'name': 'README Accuracy & Consistency',
                'module': 'test_readme_accuracy.py', 
                'description': 'Verifies README internal consistency and accuracy',
                'critical': True
            },
            'link_validation': {
                'name': 'Hyperlink Integrity',
                'module': 'test_links.py',
                'description': 'Validates all internal and external hyperlinks',
                'critical': True
            },
            'example_validation': {
                'name': 'Example Code Validation',
                'module': 'test_examples.py',
                'description': 'Validates code examples and example directories',
                'critical': False
            },
            'dependency_validation': {
                'name': 'Pattern Dependencies',
                'module': 'test_dependencies.py', 
                'description': 'Validates pattern dependency relationships',
                'critical': True
            }
        }
    
    def run_test_suite(self, suite_name: str, verbose: bool = True) -> Dict[str, Any]:
        """Run a specific test suite"""
        suite_config = self.test_suites[suite_name]
        
        print(f"\\n{'='*60}")
        print(f"Running {suite_config['name']}")
        print(f"{'='*60}")
        print(f"Description: {suite_config['description']}")
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            suite_config['module'],
            '-v' if verbose else '-q',
            '--tb=short',
            f'--junitxml={self.results_dir}/{suite_name}_results.xml'
        ]
        
        # Add special flags for specific test suites
        if suite_name == 'link_validation':
            cmd.extend(['-m', 'not slow'])  # Skip slow external link tests by default
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.tests_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per suite
            )
            
            duration = time.time() - start_time
            
            return {
                'suite': suite_name,
                'name': suite_config['name'],
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'critical': suite_config['critical']
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'suite': suite_name,
                'name': suite_config['name'],
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': f'Test suite timed out after 5 minutes',
                'critical': suite_config['critical']
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'suite': suite_name,
                'name': suite_config['name'],
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': f'Error running test suite: {str(e)}',
                'critical': suite_config['critical']
            }
    
    def run_external_link_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run external link tests (slow tests)"""
        print(f"\\n{'='*60}")
        print("Running External Link Validation (Slow Tests)")
        print(f"{'='*60}")
        print("Description: Validates external HTTP/HTTPS links are accessible")
        
        start_time = time.time()
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'test_links.py',
            '-v' if verbose else '-q',
            '--tb=short',
            '-m', 'slow',
            f'--junitxml={self.results_dir}/external_links_results.xml'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.tests_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for external links
            )
            
            duration = time.time() - start_time
            
            return {
                'suite': 'external_links',
                'name': 'External Link Validation',
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'critical': False  # External links are not critical
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'suite': 'external_links',
                'name': 'External Link Validation',
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': 'External link tests timed out after 10 minutes',
                'critical': False
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'suite': 'external_links',
                'name': 'External Link Validation',
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': f'Error running external link tests: {str(e)}',
                'critical': False
            }
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        total_suites = len(results)
        passed_suites = len([r for r in results if r['success']])
        failed_suites = total_suites - passed_suites
        
        critical_results = [r for r in results if r['critical']]
        critical_passed = len([r for r in critical_results if r['success']])
        critical_failed = len(critical_results) - critical_passed
        
        total_duration = sum(r['duration'] for r in results)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'critical_suites': len(critical_results),
            'critical_passed': critical_passed,
            'critical_failed': critical_failed,
            'total_duration': total_duration,
            'success_rate': (passed_suites / total_suites * 100) if total_suites > 0 else 0,
            'critical_success_rate': (critical_passed / len(critical_results) * 100) if critical_results else 0,
            'overall_success': critical_failed == 0,  # Success if all critical tests pass
            'results': results
        }
        
        return summary
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """Print formatted summary report"""
        print(f"\\n{'='*80}")
        print("AI DEVELOPMENT PATTERNS VALIDATION SUMMARY")
        print(f"{'='*80}")
        
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Total Duration: {summary['total_duration']:.1f} seconds")
        print()
        
        # Overall results
        status_icon = "✅" if summary['overall_success'] else "❌"
        print(f"{status_icon} Overall Status: {'PASS' if summary['overall_success'] else 'FAIL'}")
        print()
        
        # Suite summary
        print("Test Suite Summary:")
        print(f"  Total Suites: {summary['total_suites']}")
        print(f"  Passed: {summary['passed_suites']} ({summary['success_rate']:.1f}%)")
        print(f"  Failed: {summary['failed_suites']}")
        print()
        
        # Critical tests
        print("Critical Test Summary:")
        print(f"  Critical Suites: {summary['critical_suites']}")
        print(f"  Critical Passed: {summary['critical_passed']} ({summary['critical_success_rate']:.1f}%)")
        print(f"  Critical Failed: {summary['critical_failed']}")
        print()
        
        # Individual suite results
        print("Individual Suite Results:")
        print(f"{'Suite':<35} {'Status':<8} {'Duration':<10} {'Critical'}")
        print("-" * 70)
        
        for result in summary['results']:
            status = "PASS" if result['success'] else "FAIL"
            status_icon = "✅" if result['success'] else "❌"
            critical_icon = "🔴" if result['critical'] else "⚪"
            
            print(f"{result['name']:<35} {status_icon} {status:<6} {result['duration']:<8.1f}s {critical_icon}")
        
        print()
        
        # Failed suite details
        failed_results = [r for r in summary['results'] if not r['success']]
        if failed_results:
            print("Failed Suite Details:")
            print("-" * 40)
            
            for result in failed_results:
                print(f"\\n{result['name']}:")
                if result['stderr']:
                    print(f"  Error: {result['stderr'][:200]}...")
                if 'FAILED' in result['stdout']:
                    # Extract failed test names
                    lines = result['stdout'].split('\\n')
                    failed_lines = [line for line in lines if 'FAILED' in line]
                    for line in failed_lines[:5]:  # Show first 5 failed tests
                        print(f"  {line.strip()}")
        
        # Quality gates
        print(f"\\n{'='*80}")
        print("QUALITY GATES")
        print(f"{'='*80}")
        
        if summary['critical_failed'] == 0:
            print("✅ All critical quality gates PASSED - Repository is ready for merge/deploy")
        else:
            print("❌ Critical quality gates FAILED - Repository needs attention before merge/deploy")
            print(f"   {summary['critical_failed']} critical test suite(s) failed")
        
        print(f"{'='*80}")
    
    def save_report(self, summary: Dict[str, Any]):
        """Save comprehensive report to files"""
        # Save JSON report
        json_report_path = self.results_dir / "comprehensive_report.json"
        with open(json_report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save markdown report
        md_report_path = self.results_dir / "comprehensive_report.md"
        with open(md_report_path, 'w') as f:
            f.write("# AI Development Patterns Validation Report\\n\\n")
            f.write(f"**Generated:** {summary['timestamp']}\\n")
            f.write(f"**Duration:** {summary['total_duration']:.1f} seconds\\n\\n")
            
            status = "✅ PASS" if summary['overall_success'] else "❌ FAIL"
            f.write(f"**Overall Status:** {status}\\n\\n")
            
            f.write("## Summary\\n\\n")
            f.write(f"- Total Test Suites: {summary['total_suites']}\\n")
            f.write(f"- Passed: {summary['passed_suites']} ({summary['success_rate']:.1f}%)\\n")
            f.write(f"- Failed: {summary['failed_suites']}\\n")
            f.write(f"- Critical Tests Passed: {summary['critical_passed']}/{summary['critical_suites']}\\n\\n")
            
            f.write("## Test Suite Results\\n\\n")
            f.write("| Suite | Status | Duration | Critical |\\n")
            f.write("|-------|--------|----------|----------|\\n")
            
            for result in summary['results']:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                critical = "🔴" if result['critical'] else "⚪"
                f.write(f"| {result['name']} | {status} | {result['duration']:.1f}s | {critical} |\\n")
        
        print(f"\\nReports saved:")
        print(f"  JSON: {json_report_path}")
        print(f"  Markdown: {md_report_path}")
    
    def run_all_tests(self, include_external_links: bool = False, verbose: bool = True) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report"""
        print("Starting AI Development Patterns Validation")
        print(f"Repository: {self.repo_root}")
        print(f"Tests Directory: {self.tests_dir}")
        
        results = []
        
        # Run all main test suites
        for suite_name in self.test_suites.keys():
            result = self.run_test_suite(suite_name, verbose)
            results.append(result)
        
        # Optionally run external link tests
        if include_external_links:
            external_result = self.run_external_link_tests(verbose)
            results.append(external_result)
        
        # Generate and display summary
        summary = self.generate_summary_report(results)
        self.print_summary_report(summary)
        self.save_report(summary)
        
        return summary


def main():
    """Main entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AI Development Patterns validation tests')
    parser.add_argument('--external-links', action='store_true',
                       help='Include external link validation (slow)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Run in quiet mode (less verbose)')
    parser.add_argument('--suite', choices=['pattern_compliance', 'readme_accuracy', 
                                          'link_validation', 'example_validation', 
                                          'dependency_validation'],
                       help='Run specific test suite only')
    
    args = parser.parse_args()
    
    runner = PatternTestRunner()
    
    if args.suite:
        # Run single suite
        result = runner.run_test_suite(args.suite, verbose=not args.quiet)
        success = result['success']
        print(f"\\nSuite {'PASSED' if success else 'FAILED'}: {result['name']}")
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        summary = runner.run_all_tests(
            include_external_links=args.external_links,
            verbose=not args.quiet
        )
        
        # Exit with appropriate code
        sys.exit(0 if summary['overall_success'] else 1)


if __name__ == '__main__':
    main()