#!/usr/bin/env python3
"""
Quality Metrics Tracker for AI-Driven Refactoring

Tracks code quality metrics before and after refactoring to measure improvements.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class QualityMetrics:
    def __init__(self, source_dir: str = "src"):
        self.source_dir = source_dir
        self.metrics_file = Path("quality_metrics.json")
    
    def measure_complexity(self) -> Dict[str, Any]:
        """Measure cyclomatic complexity using radon."""
        try:
            result = subprocess.run(
                ["radon", "cc", self.source_dir, "--json"],
                capture_output=True, text=True, check=True
            )
            complexity_data = json.loads(result.stdout)
            
            # Calculate average complexity
            total_complexity = 0
            total_functions = 0
            
            for file_data in complexity_data.values():
                for item in file_data:
                    if item['type'] in ['function', 'method']:
                        total_complexity += item['complexity']
                        total_functions += 1
            
            avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
            
            return {
                "average_complexity": round(avg_complexity, 2),
                "total_functions": total_functions,
                "high_complexity_count": sum(
                    1 for file_data in complexity_data.values()
                    for item in file_data
                    if item['type'] in ['function', 'method'] and item['complexity'] > 10
                )
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"error": "radon not available"}
    
    def measure_coverage(self) -> Dict[str, Any]:
        """Measure test coverage using coverage.py."""
        try:
            # Run tests with coverage
            subprocess.run(
                ["coverage", "run", "-m", "pytest", "tests/"],
                capture_output=True, check=True
            )
            
            # Get coverage report
            result = subprocess.run(
                ["coverage", "report", "--format=json"],
                capture_output=True, text=True, check=True
            )
            
            coverage_data = json.loads(result.stdout)
            
            return {
                "coverage_percent": round(coverage_data['totals']['percent_covered'], 2),
                "lines_covered": coverage_data['totals']['covered_lines'],
                "lines_total": coverage_data['totals']['num_statements'],
                "missing_lines": coverage_data['totals']['missing_lines']
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"error": "coverage not available"}
    
    def measure_duplication(self) -> Dict[str, Any]:
        """Measure code duplication using pylint."""
        try:
            result = subprocess.run(
                ["pylint", self.source_dir, "--disable=all", "--enable=R0801", 
                 "--reports=no", "--output-format=json"],
                capture_output=True, text=True
            )
            
            # pylint returns non-zero for warnings, so don't check return code
            if result.stdout.strip():
                messages = json.loads(result.stdout)
                duplication_count = len([m for m in messages if m['message-id'] == 'R0801'])
            else:
                duplication_count = 0
            
            return {
                "duplication_violations": duplication_count,
                "duplication_score": max(0, 10 - duplication_count)  # Simple scoring
            }
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            return {"error": "pylint not available"}
    
    def measure_maintainability(self) -> Dict[str, Any]:
        """Measure maintainability index using radon."""
        try:
            result = subprocess.run(
                ["radon", "mi", self.source_dir, "--json"],
                capture_output=True, text=True, check=True
            )
            
            mi_data = json.loads(result.stdout)
            
            # Calculate average maintainability index
            total_mi = 0
            file_count = 0
            
            for file_path, mi_score in mi_data.items():
                if isinstance(mi_score, (int, float)):
                    total_mi += mi_score
                    file_count += 1
            
            avg_mi = total_mi / file_count if file_count > 0 else 0
            
            return {
                "maintainability_index": round(avg_mi, 2),
                "files_measured": file_count,
                "maintainability_grade": self._grade_maintainability(avg_mi)
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"error": "radon not available"}
    
    def _grade_maintainability(self, mi_score: float) -> str:
        """Convert MI score to letter grade."""
        if mi_score >= 85: return "A"
        elif mi_score >= 70: return "B" 
        elif mi_score >= 50: return "C"
        elif mi_score >= 25: return "D"
        else: return "F"
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all quality metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "complexity": self.measure_complexity(),
            "coverage": self.measure_coverage(),
            "duplication": self.measure_duplication(),
            "maintainability": self.measure_maintainability()
        }
    
    def save_baseline(self):
        """Save current metrics as baseline for comparison."""
        metrics = self.collect_all_metrics()
        
        # Load existing data or create new
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                data = json.load(f)
        else:
            data = {"measurements": []}
        
        # Add new measurement
        data["measurements"].append({
            "type": "baseline",
            **metrics
        })
        
        # Save updated data
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Baseline metrics saved to {self.metrics_file}")
        self._print_metrics_summary(metrics)
    
    def measure_improvement(self):
        """Measure improvement since last baseline."""
        if not self.metrics_file.exists():
            print("❌ No baseline found. Run --baseline first.")
            return
        
        with open(self.metrics_file) as f:
            data = json.load(f)
        
        # Get last baseline
        baselines = [m for m in data["measurements"] if m["type"] == "baseline"]
        if not baselines:
            print("❌ No baseline measurement found.")
            return
        
        baseline = baselines[-1]
        current = self.collect_all_metrics()
        
        # Add current measurement
        data["measurements"].append({
            "type": "improvement",
            **current
        })
        
        # Save updated data
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Calculate and display improvements
        self._display_improvements(baseline, current)
    
    def _display_improvements(self, baseline: Dict, current: Dict):
        """Display improvement comparison."""
        print("\n📊 Refactoring Impact Analysis")
        print("=" * 50)
        
        # Complexity improvements
        if "error" not in baseline["complexity"] and "error" not in current["complexity"]:
            old_complexity = baseline["complexity"]["average_complexity"]
            new_complexity = current["complexity"]["average_complexity"]
            complexity_improvement = old_complexity - new_complexity
            
            print(f"🔄 Cyclomatic Complexity:")
            print(f"   Before: {old_complexity}")
            print(f"   After:  {new_complexity}")
            print(f"   Change: {complexity_improvement:+.2f} ({'better' if complexity_improvement > 0 else 'worse'})")
        
        # Coverage improvements
        if "error" not in baseline["coverage"] and "error" not in current["coverage"]:
            old_coverage = baseline["coverage"]["coverage_percent"]
            new_coverage = current["coverage"]["coverage_percent"]
            coverage_improvement = new_coverage - old_coverage
            
            print(f"\n🎯 Test Coverage:")
            print(f"   Before: {old_coverage}%")
            print(f"   After:  {new_coverage}%")
            print(f"   Change: {coverage_improvement:+.2f}% ({'better' if coverage_improvement > 0 else 'worse'})")
        
        # Maintainability improvements
        if "error" not in baseline["maintainability"] and "error" not in current["maintainability"]:
            old_mi = baseline["maintainability"]["maintainability_index"]
            new_mi = current["maintainability"]["maintainability_index"]
            mi_improvement = new_mi - old_mi
            
            old_grade = baseline["maintainability"]["maintainability_grade"]
            new_grade = current["maintainability"]["maintainability_grade"]
            
            print(f"\n🔧 Maintainability Index:")
            print(f"   Before: {old_mi} (Grade {old_grade})")
            print(f"   After:  {new_mi} (Grade {new_grade})")
            print(f"   Change: {mi_improvement:+.2f} ({'better' if mi_improvement > 0 else 'worse'})")
        
        # Overall assessment
        print(f"\n✅ Metrics collected at: {current['timestamp']}")
        print(f"📁 Data saved to: {self.metrics_file}")
    
    def _print_metrics_summary(self, metrics: Dict):
        """Print a summary of current metrics."""
        print("\n📊 Current Quality Metrics")
        print("=" * 30)
        
        if "error" not in metrics["complexity"]:
            print(f"🔄 Avg Complexity: {metrics['complexity']['average_complexity']}")
            print(f"   High complexity functions: {metrics['complexity']['high_complexity_count']}")
        
        if "error" not in metrics["coverage"]:
            print(f"🎯 Test Coverage: {metrics['coverage']['coverage_percent']}%")
        
        if "error" not in metrics["maintainability"]:
            print(f"🔧 Maintainability: {metrics['maintainability']['maintainability_index']} "
                  f"(Grade {metrics['maintainability']['maintainability_grade']})")
        
        if "error" not in metrics["duplication"]:
            print(f"📋 Duplication Score: {metrics['duplication']['duplication_score']}/10")

def main():
    if len(sys.argv) < 2:
        print("Usage: python quality-metrics.py [--baseline|--improvement|--generate-report]")
        sys.exit(1)
    
    metrics = QualityMetrics()
    
    if "--baseline" in sys.argv:
        metrics.save_baseline()
    elif "--improvement" in sys.argv:
        metrics.measure_improvement()
    elif "--generate-report" in sys.argv:
        current = metrics.collect_all_metrics()
        metrics._print_metrics_summary(current)
    else:
        print("Unknown option. Use --baseline, --improvement, or --generate-report")

if __name__ == "__main__":
    main()