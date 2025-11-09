# AI-Driven Refactoring Example

This directory contains a complete implementation of the AI-Driven Refactoring pattern with automated code smell detection, refactoring pipeline, and quality metrics tracking.

## Directory Structure

```
ai-driven-refactoring/
├── README.md                    # This file
├── refactoring-rules.md        # Configurable refactoring rules and thresholds
├── refactor-pipeline.sh        # Automated refactoring pipeline script
├── spec_validator.py           # Code smell detection and validation
├── quality-metrics.py          # Before/after metrics tracking
├── rollback-procedures.md      # Risk assessment and rollback guidelines
└── examples/                   # Example refactoring scenarios
    ├── long-method-example.py  # Long method refactoring example
    ├── large-class-example.py  # Large class extraction example
    └── primitive-obsession.py  # Primitive to object refactoring
```

## Quick Start

1. **Define refactoring rules:**
   ```bash
   cp refactoring-rules.md .ai/rules/refactoring.md
   ```

2. **Run automated refactoring pipeline:**
   ```bash
   ./refactor-pipeline.sh
   ```

3. **Track quality improvements:**
   ```bash
   python quality-metrics.py --before --after
   ```

## Features

- **Automated code smell detection** with configurable thresholds
- **AI-guided refactoring** with safety validation
- **Quality metrics tracking** with before/after comparisons
- **Risk assessment** for refactoring timing and complexity
- **Rollback procedures** for safe refactoring experiments
- **CI integration** with pre-commit hooks and quality gates

## Integration

This example integrates with:
- Static analysis tools (flake8, pylint, radon)
- Test runners (pytest) with coverage tracking
- Git workflow with atomic commits
- CI/CD pipelines for automated quality gates

See individual files for detailed implementation and usage instructions.