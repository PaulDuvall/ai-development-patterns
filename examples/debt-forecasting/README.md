# Debt Forecasting Example

Supporting material for the [Debt Forecasting](../../README.md#debt-forecasting) pattern: forecast maintenance burden from code, dependency, coverage, and documentation trends so teams can prioritize technical debt.

## Files in This Directory

- **[`debt_analysis.md`](debt_analysis.md)** - Technical debt analysis and forecasting reference covering a debt detection framework (quality metrics and automated discovery), debt categorization (architecture, testing, performance, and security debt), business impact analysis with AI-assisted prioritization, remediation strategies, predictive forecasting models, and debt metrics dashboards. Its scripts, configurations, and code samples are illustrative implementations to adapt, not tooling shipped in this directory.

For complete pattern documentation, see: [Debt Forecasting](../../README.md#debt-forecasting)

## What Debt Forecasting Provides

- Proactively identify technical debt before it becomes critical
- Prioritize debt remediation by business impact and maintenance cost
- Forecast future maintenance burden and resource requirements
- Track technical debt trends and improvement progress

## Technical Debt Categories

### Code Complexity
- Cyclomatic complexity hotspots
- Method and class size violations
- Deep inheritance hierarchies
- Excessive parameter counts

### Architecture Debt
- Circular dependencies
- Tight coupling between modules
- Missing abstraction layers
- Architectural pattern violations

### Documentation Debt
- Missing or outdated documentation
- Code without comments
- API documentation gaps
- Architectural decision records missing

### Test Debt
- Low test coverage areas
- Flaky or brittle tests
- Missing integration tests
- Outdated test dependencies

## Illustrative Workflow

The pattern combines deterministic trend data with an AI-assisted explanation instead of asking a model to guess debt from a snapshot:

```bash
# Collect deterministic trend data with standard tools
python -m radon cc src --json > metrics/complexity.json
python -m pytest --cov=src --cov-report=json:metrics/coverage.json
git log --since='90 days ago' --numstat > metrics/churn.txt

# AI-assisted ranking grounded in the collected metrics
ai "Rank maintenance risks using the attached complexity, coverage, churn,
dependency, and documentation-drift trends. Cite the metric behind every rank." \
  > debt-forecast.md
```

Review forecast accuracy against later incidents and maintenance work, then adjust weights rather than treating model rankings as objective measurements. [`debt_analysis.md`](debt_analysis.md) expands this approach with debt scan scripts, impact calculators, prioritization prompts, and dashboard KPIs to adapt to your own toolchain.
