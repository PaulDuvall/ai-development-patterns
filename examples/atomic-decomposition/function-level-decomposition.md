# Function-Level Decomposition Techniques

This guide provides detailed techniques for decomposing atomic tasks into individual functions when AI struggles with larger implementations, as referenced in the [Atomic Decomposition](../../README.md#atomic-decomposition) pattern.

## Overview

When AI cannot successfully implement an atomic task after multiple attempts, further decomposition to the function level often resolves implementation difficulties. This approach breaks complex logic into focused, independently implementable functions.

## Decomposition Trigger Indicators

Apply function-level decomposition when you encounter these situations:

### AI Implementation Struggles
- **AI fails to implement task after 3-4 attempts**
- **Generated code contains logical errors or incomplete implementations**
- **AI produces overly complex or difficult-to-understand code**
- **Implementation attempts result in inconsistent behavior**

### Code Complexity Indicators
- **Generated code exceeds 50 lines for a single function**
- **Single function handles multiple distinct responsibilities**
- **Function requires complex state management or multiple side effects**
- **Implementation involves multiple algorithms or validation steps**

### Task Characteristics
- **Task involves multiple distinct algorithms or operations**
- **Business logic includes several validation or transformation steps**
- **Implementation requires coordination between different data sources**
- **Testing requires complex setup or multiple test scenarios**

## Function Breakdown Process

### 1. Identify Core Operations

Start by identifying the distinct operations within the failing task:

```bash
# Original failing task: "Implement password validation with complexity rules"
# Identify core operations:
# - Length validation
# - Character complexity checking
# - Common password blacklist checking
# - Result aggregation and formatting
```

### 2. Design Individual Function Contracts

Create clear, focused contracts for each operation:

```typescript
// Clear function contracts enable successful AI implementation
interface PasswordLengthValidator {
  (password: string, minLength: number, maxLength: number): {
    isValid: boolean;
    errorMessage?: string;
  };
}

interface PasswordComplexityValidator {
  (password: string, requirements: ComplexityRequirements): {
    isValid: boolean;
    missingRequirements: string[];
  };
}

interface PasswordBlacklistValidator {
  (password: string, blacklist: string[]): {
    isValid: boolean;
    matchedPattern?: string;
  };
}
```

### 3. Implement Functions Individually

Request implementation of each function in isolation:

```bash
# Function 1: Length Validation
ai "Implement password length validation function:

Function signature:
function validatePasswordLength(password: string, minLength: number, maxLength: number): {
  isValid: boolean;
  errorMessage?: string;
}

Requirements:
- Input: password string, min/max length numbers
- Output: validation result with specific error message
- Pure function with no side effects
- Handle edge cases: null/undefined inputs, negative lengths"

# Function 2: Complexity Validation
ai "Implement password character complexity validation:

Function signature:
function validatePasswordComplexity(password: string, requirements: ComplexityRequirements): {
  isValid: boolean;
  missingRequirements: string[];
}

Requirements:
- Check uppercase, lowercase, numbers, special characters
- Return specific list of missing character types
- Configurable requirements via requirements object
- Handle empty passwords and Unicode characters"

# Function 3: Blacklist Validation
ai "Implement common password blacklist check:

Function signature:
function validatePasswordBlacklist(password: string, blacklist: string[]): {
  isValid: boolean;
  matchedPattern?: string;
}

Requirements:
- Case-insensitive matching against blacklist
- Support partial pattern matching
- Return specific matched pattern for user feedback
- Efficient lookup for large blacklists"
```

### 4. Create Integration Function

Once individual functions work, combine them:

```bash
# Integration function
ai "Combine password validation functions into comprehensive service:

Use existing functions:
- validatePasswordLength()
- validatePasswordComplexity()
- validatePasswordBlacklist()

Create:
function validatePassword(password: string, config: ValidationConfig): PasswordValidationResult

Requirements:
- Call all validation functions
- Aggregate results into comprehensive response
- Prioritize error messages by severity
- Include overall validity and detailed feedback"
```

## Practical Examples

### Example 1: User Registration Validation

**Original Failing Task:**
```bash
# This task fails after 3-4 AI attempts
ai "Implement user registration validation with email verification, password strength, username uniqueness, and age verification"
```

**Function-Level Breakdown:**
```bash
# Function 1: Email Validation
ai "Implement email format validation:
- Input: email string
- Output: {isValid: boolean, normalizedEmail?: string}
- Use RFC 5322 standard, normalize to lowercase"

# Function 2: Username Uniqueness
ai "Implement username uniqueness check:
- Input: username string, database connection
- Output: {isAvailable: boolean, suggestedAlternatives?: string[]}
- Case-insensitive checking, generate alternatives if taken"

# Function 3: Age Verification
ai "Implement age verification from birthdate:
- Input: birthDate string, minimumAge number
- Output: {isOldEnough: boolean, actualAge?: number}
- Handle date parsing, timezone considerations"

# Integration Function
ai "Combine all validation functions into user registration validator:
- Use all individual validators
- Return comprehensive validation result
- Include field-specific error messages"
```

### Example 2: Order Processing Pipeline

**Original Failing Task:**
```bash
# This task is too complex for single implementation
ai "Implement order processing with inventory check, payment validation, shipping calculation, tax computation, and notification sending"
```

**Function-Level Breakdown:**
```bash
# Function 1: Inventory Validation
ai "Implement inventory availability check:
- Input: items array with quantities
- Output: {available: boolean, unavailableItems: string[]}
- Check stock levels, handle reserved inventory"

# Function 2: Payment Validation
ai "Implement payment method validation:
- Input: payment details object
- Output: {isValid: boolean, errors: string[]}
- Validate card numbers, expiration, CVV format"

# Function 3: Shipping Cost Calculation
ai "Implement shipping cost calculator:
- Input: items, destination address, shipping method
- Output: {cost: number, estimatedDays: number}
- Calculate by weight, distance, shipping speed"

# Function 4: Tax Computation
ai "Implement tax calculation:
- Input: order total, shipping address, item categories
- Output: {taxAmount: number, breakdown: TaxBreakdown}
- Handle state/local taxes, tax-exempt items"

# Integration Function
ai "Combine order processing functions:
- Orchestrate inventory, payment, shipping, tax validation
- Handle partial failures and rollback logic
- Return comprehensive order processing result"
```

## Function Integration Strategy

### 1. Test Functions Individually

Create comprehensive unit tests for each function before integration:

```javascript
// Test individual functions first
describe('Password Length Validation', () => {
  test('accepts valid length passwords', () => {
    const result = validatePasswordLength('password123', 8, 20);
    expect(result.isValid).toBe(true);
  });

  test('rejects too short passwords', () => {
    const result = validatePasswordLength('abc', 8, 20);
    expect(result.isValid).toBe(false);
    expect(result.errorMessage).toContain('minimum 8 characters');
  });
});
```

### 2. Implement Progressive Integration

Combine functions incrementally with integration tests at each step:

```bash
# Step 1: Combine first two functions
ai "Create intermediate validator combining length and complexity validation"

# Step 2: Add third function
ai "Enhance validator to include blacklist checking"

# Step 3: Add final function and complete integration
ai "Complete validator with all validation functions and comprehensive error handling"
```

### 3. Validate Function Contracts

Ensure each function adheres to its designed interface:

```typescript
// Runtime contract validation
function validateContract<T>(
  functionName: string,
  expectedInput: any,
  actualOutput: T,
  expectedOutputShape: any
): void {
  // Validate function output matches expected contract
  // Throw descriptive errors for contract violations
}
```

## When to Use Function-Level Decomposition

### Recommended Scenarios
- **AI Implementation Struggles**: After 3-4 failed attempts on larger tasks
- **Complex Business Logic**: Tasks involving multiple validation or transformation steps
- **Algorithm Implementation**: Mathematical or complex computational logic
- **Testing Requirements**: When comprehensive unit test coverage is essential
- **Code Reusability**: When functions might be reused across multiple features
- **Performance Optimization**: When individual functions need specific performance tuning

### Avoid Over-Decomposition
- **Simple operations**: Don't decompose basic CRUD operations
- **Tightly coupled logic**: When operations cannot be meaningfully separated
- **Overhead concerns**: When function call overhead impacts performance
- **Single-use logic**: When functions won't be reused or tested independently

## Success Metrics

### Function Implementation Success
- **Individual functions**: Each function should implement successfully within 1-2 AI attempts
- **Clear contracts**: Function interfaces should be immediately understandable
- **Independent testing**: Each function should be testable in isolation
- **Minimal coupling**: Functions should have minimal dependencies on external state

### Integration Success
- **Progressive integration**: Integration should proceed smoothly step-by-step
- **Comprehensive testing**: Integration tests should cover all function combinations
- **Performance validation**: Combined functions should meet performance requirements
- **Error handling**: Integration should handle individual function failures gracefully

This systematic approach to function-level decomposition enables successful AI implementation of complex tasks that would otherwise fail due to excessive complexity or unclear requirements.
