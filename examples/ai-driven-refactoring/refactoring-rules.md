# Refactoring Rules

## Code Smell Thresholds

### Long Method Smell
- **Max lines**: 20 (excluding docstrings and comments)
- **Max cyclomatic complexity**: 10
- **Detection tools**: `flake8 C901`, `pylint R0915`
- **Refactoring strategy**: Extract Method pattern

### Large Class Smell  
- **Max class lines**: 250
- **Max methods**: 20
- **Max instance variables**: 10
- **Detection tools**: `pylint R0902`, `R0904`
- **Refactoring strategy**: Extract Class pattern

### Primitive Obsession Smell
- **Indicators**:
  - String validation patterns in multiple places
  - Dictionaries used as pseudo-objects
  - Lists of primitives that always travel together
  - Type checking with `isinstance(x, (str, int))`
- **Refactoring strategy**: Replace Primitive with Object

### Duplicate Code Smell
- **Max duplicate lines**: 6 consecutive lines
- **Detection tools**: `pylint R0801`
- **Refactoring strategy**: Extract Method or Extract Class

### Data Clumps Smell
- **Indicators**:
  - Same 3+ parameters passed to multiple methods
  - Groups of fields that are always used together
- **Refactoring strategy**: Introduce Parameter Object

## Refactoring Safety Rules

### Low Risk Refactorings (Can automate)
- Extract Method (single responsibility)
- Rename variables/methods (IDE safe rename)
- Add type hints
- Extract constants
- Remove dead code

### Medium Risk Refactorings (AI + validation)
- Extract Class 
- Replace conditional with polymorphism
- Introduce Parameter Object
- Move method to appropriate class

### High Risk Refactorings (Manual review required)
- Large class decomposition (>5 extracted classes)
- Inheritance hierarchy changes
- Database schema refactoring
- API contract changes

## Quality Gates

### Pre-refactoring Requirements
- Test coverage ≥ 90%
- All tests passing
- No merge conflicts
- Code review approval for high-risk changes

### Post-refactoring Validation
- Test coverage maintained or improved
- All tests still passing
- Static analysis improvements
- Performance regression check (±5%)

## AI Refactoring Prompts

### Extract Method Prompt
```
Refactor this method using Extract Method pattern:
- Method has {line_count} lines (exceeds {threshold})
- Identified responsibilities: {responsibilities}
- Extract logical groups into separate methods
- Maintain original method signature and behavior
- Ensure test coverage is preserved
```

### Extract Class Prompt
```
Extract cohesive classes from {class_name}:
- Class has {metrics} (exceeds thresholds)
- Identify cohesive groups of methods and fields
- Create new classes with single responsibilities
- Maintain public API compatibility
- Update tests to reflect new structure
```

### Replace Primitive Prompt
```
Replace primitive obsession in {context}:
- Create value objects for: {primitives}
- Encapsulate validation logic in objects
- Update method signatures to use objects
- Maintain backward compatibility where needed
```