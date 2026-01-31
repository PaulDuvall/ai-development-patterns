# Experimental AI Development Patterns

A collection of experimental patterns for AI-assisted development that are under active development and evaluation. These patterns represent cutting-edge approaches that may be refined, consolidated, or evolved based on community feedback and real-world usage.

## Pattern Organization

These experimental patterns extend the core AI development patterns with advanced workflows and emerging practices:

- **[Advanced Workflows](#advanced-workflows)** - Complex orchestration patterns for mature AI development teams
- **[Operations Automation](#operations-automation)** - Experimental automation patterns for CI/CD and production management
- **[Monitoring & Intelligence](#monitoring--intelligence)** - Advanced observability and predictive maintenance patterns

## Pattern Exploration

**[NOTES.md](NOTES.md)** - Tracks patterns under early exploration before formalization. This is where new pattern ideas are documented, evaluated, and refined before becoming full experimental patterns. Current explorations include voice-to-code interfaces and other emerging AI development approaches.

## Experimental Pattern Reference

| Pattern | Maturity | Type | Description | Dependencies |
|---------|----------|------|-------------|--------------|
| **[Handoff Protocols](#handoff-protocols)** | Intermediate | Foundation | Clear boundaries and procedures for transitioning work between human developers and AI | Developer Lifecycle |
| **[Testing Orchestration](#testing-orchestration)** | Intermediate | Workflow | Unified approach to test-first development, automated generation, and quality assurance | Spec-Driven Development |
| **[Workflow Orchestration](#workflow-orchestration)** | Advanced | Workflow | Coordinate sequential pipelines, parallel workflows, and hybrid human-AI processes | Testing Orchestration, Tool Integration |
| **[Review Automation](#review-automation)** | Intermediate | Operations | Automate review process for parallel agent outputs using AI to detect conflicts and coordinate integration | Workflow Orchestration, Atomic Decomposition |
| **[Debt Forecasting](#debt-forecasting)** | Intermediate | Operations | Proactively identify and prioritize technical debt using AI-powered code analysis | Guided Refactoring, Guided Architecture, Tool Integration |
| **[Pipeline Synthesis](#pipeline-synthesis)** | Intermediate | Workflow | Convert plain-English build specifications into CI/CD pipeline configurations | Workflow Orchestration, Tool Integration |
| **[Deployment Synthesis](#deployment-synthesis)** | Advanced | Operations | Generate blue-green deployment scripts with validation to prevent AI misconceptions | Pipeline Synthesis |
| **[Drift Remediation](#drift-remediation)** | Advanced | Operations | Detect infrastructure configuration drift and generate corrective patches automatically | Pipeline Synthesis |
| **[Release Synthesis](#release-synthesis)** | Beginner | Operations | Automatically generate structured release notes by analyzing git commit history | Pipeline Synthesis |
| **[Incident Automation](#incident-automation)** | Advanced | Operations | Generate actionable incident response playbooks from historical incident data | Baseline Management |
| **[Suite Health](#suite-health)** | Intermediate | Operations | Analyze build history to identify and remediate flaky tests automatically | Testing Orchestration |
| **[Test Promotion](#test-promotion)** | Intermediate | Development | Separate AI-generated tests from immutable golden tests to prevent AI from weakening test assertions | Testing Orchestration, Spec-Driven Development |
| **[Upgrade Advisor](#upgrade-advisor)** | Intermediate | Operations | Intelligently manage dependency upgrades with compatibility analysis and risk assessment | Debt Forecasting |
| **[Handoff Automation](#handoff-automation)** | Intermediate | Operations | Generate comprehensive handoff briefs that summarize system state and active issues | Incident Automation |
| **[Chaos Engineering](#chaos-engineering)** | Advanced | Operations | Generate targeted chaos experiments based on system architecture and dependencies | Baseline Management |
| **[ChatOps Security](#chatops-security)** | Beginner | Operations | Deploy security scanning capabilities through chat commands for immediate feedback | Security Orchestration |
| **[Evidence Automation](#evidence-automation)** | Advanced | Operations | Generate audit evidence matrices from logs and configuration changes automatically | Security Orchestration |
| **[Context Optimization](#context-optimization)** | Advanced | Development | Match AI tool selection to task complexity and optimize cost/performance trade-offs | Progressive Enhancement |
| **[Image Spec](#image-spec)** | Intermediate | Development | Upload images (diagrams, mockups, flows) as primary specifications for AI coding tools to build accurate implementations from visual context | Spec-Driven Development, Progressive Enhancement, Context Optimization |
| **[Event Automation](#event-automation)** | Intermediate | Development | Execute custom commands automatically at specific lifecycle events in AI coding assistants to enforce policies and automate workflows | Codified Rules, Security Sandbox |
| **[Custom Commands](#custom-commands)** | Intermediate | Development | Discover and use built-in command vocabularies, then extend them with custom commands that encode domain expertise and project-specific workflows | Event Automation, Spec-Driven Development |
| **[Progressive Disclosure](#progressive-disclosure)** | Intermediate | Development | Load AI assistant rules incrementally based on task context to prevent instruction saturation and maintain consistency | Codified Rules, Context Optimization |
| **[Asynchronous Research](#asynchronous-research)** | Intermediate | Development | Use fire-and-forget coding agents in dedicated repositories to conduct autonomous code investigations that prove technical feasibility through executable experiments | Parallel Agents, Context Persistence, Choice Generation |
| **[Centralized Rules](#centralized-rules)** | Advanced | Operations | Enforce organization-wide AI rules through a central gateway service or shared SDK library rather than distributing configuration files | Codified Rules, Policy Generation, Security Orchestration |

---

## Advanced Workflows

### Handoff Protocols

**Maturity**: Intermediate  
**Description**: Clear boundaries and procedures for transitioning work between human developers and AI tools based on complexity, security requirements, and creative problem-solving needs.

**Related Patterns**: [Developer Lifecycle](../README.md#developer-lifecycle), [Observable Development](../README.md#observable-development), [Workflow Orchestration](#workflow-orchestration)

**Handoff Decision Framework**

```mermaid
graph TD
    A[Task Assessment] --> B{Complexity Level}
    B -->|Low| C[AI First]
    B -->|Medium| D[AI with Human Review]
    B -->|High| E[Human First]
    B -->|Critical| F[Human Only]
    
    C --> G{Quality Check}
    D --> H{AI Success?}
    E --> I{Need AI Assistance?}
    F --> J[Human Implementation]
    
    G -->|Pass| K[Deploy]
    G -->|Fail| L[Human Review]
    H -->|Yes| M[Human Verification]
    H -->|No| N[Human Takeover]
    I -->|Yes| O[Collaborative Mode]
    I -->|No| J
```

**Handoff Execution Sequence**

```mermaid
sequenceDiagram
    participant H as Human
    participant AS as Assessment System
    participant AI as AI Assistant
    participant QC as Quality Control
    participant R as Repository
    
    Note over H,R: Task Assessment Phase
    H->>AS: Submit Task Requirements
    AS->>AS: Analyze Complexity & Risk
    AS->>H: Handoff Recommendation (AI First/Human First/Collaborative)
    
    Note over H,R: AI-First Path (Low Complexity)
    alt AI First Recommended
        H->>AI: Execute Task with Constraints
        AI->>AI: Generate Implementation
        AI->>QC: Submit for Quality Check
        QC->>QC: Run Automated Tests & Analysis
        alt Quality Check Passes
            QC->>R: Commit Implementation
            QC->>H: Task Complete
        else Quality Check Fails
            QC->>H: Failed Quality - Human Review Required
            H->>AI: Provide Feedback & Corrections
            AI->>QC: Submit Revised Implementation
            QC->>R: Commit Final Version
        end
    
    Note over H,R: Human-First Path (High Complexity)
    else Human First Recommended
        H->>H: Initial Implementation
        H->>AS: Assess Need for AI Assistance
        alt AI Assistance Needed
            H->>AI: Request Specific AI Help
            AI->>H: Provide Targeted Assistance
            H->>H: Integrate AI Suggestions
            H->>R: Commit Human-Led Implementation
        else No AI Assistance
            H->>R: Commit Human-Only Implementation
        end
    
    Note over H,R: Collaborative Path (Medium Complexity)
    else Collaborative Recommended
        H->>AI: Collaborative Development Session
        loop Until Complete
            AI->>H: Generate Code Segment
            H->>H: Review & Modify
            H->>AI: Provide Feedback
            AI->>AI: Adjust Based on Feedback
        end
        H->>QC: Submit Collaborative Result
        QC->>R: Commit Final Implementation
    end
    
    Note over H,R: Continuous Learning
    R->>AS: Update Success Metrics
    AS->>AS: Refine Handoff Criteria
```

**Anti-pattern: Broken Boundaries**
Allowing AI and humans to work on the same task simultaneously without clear handoff points leads to conflicts, duplicated effort, and inconsistent quality.

---

### Testing Orchestration

**Maturity**: Intermediate  
**Description**: Unified approach combining test-first development, automated test generation, and quality assurance patterns to ensure AI-generated code meets quality and behavioral specifications.

**Pattern Boundary Clarification**:
- **This pattern** focuses on overall testing strategy and test generation
- **Spec-Driven Development** focuses on writing specs before implementation
- **Observable Development** focuses on logging and debugging for AI understanding
- **Automated Traceability** focuses on linking requirements to tests and implementation

**Related Patterns**: [Spec-Driven Development](../README.md#spec-driven-development), [Observable Development](../README.md#observable-development)

**Integrated Testing Framework**

```mermaid
graph TD
    A[Acceptance Tests] --> B[Unit Test Generation]
    B --> C[Integration Tests]
    C --> D[Performance Tests]
    D --> E[Security Tests]
    E --> F[Flakiness Detection]
    F --> G[Quality Gates]
    G --> H{All Tests Pass?}
    H -->|Yes| I[Deploy]
    H -->|No| J[AI Test Refinement]
    J --> B
```

**Testing Workflow Execution Sequence**

```mermaid
sequenceDiagram
    participant D as Developer
    participant AI as AI Assistant
    participant TS as Test Suite
    participant AT as Acceptance Tests
    participant CI as CI/CD Pipeline
    participant QG as Quality Gates
    participant FD as Flakiness Detector
    
    Note over D,FD: Test-First Development Phase
    D->>AI: Generate Acceptance Tests from Requirements
    AI->>AT: Create Gherkin Scenarios + Expected Behaviors
    AT->>D: Review Generated Tests
    D->>AI: Generate Unit Tests from Acceptance Criteria
    AI->>TS: Create Unit Test Suite
    
    Note over D,FD: Implementation & Test Generation
    D->>AI: Implement Feature Following Tests
    AI->>TS: Generate Implementation Code
    D->>AI: Generate Integration Tests
    AI->>TS: Add Integration Test Cases
    D->>AI: Generate Performance Tests (Response Time, Memory)
    AI->>TS: Add Performance Benchmarks
    D->>AI: Generate Security Tests (Auth, Input Validation)
    AI->>TS: Add Security Test Cases
    
    Note over D,FD: Execution & Quality Assessment
    D->>CI: Trigger Test Pipeline
    CI->>TS: Execute All Test Suites
    TS->>TS: Run Unit → Integration → Performance → Security
    alt All Tests Pass
        TS->>QG: Submit Results for Quality Gates
        QG->>QG: Check Coverage, Performance, Security Thresholds
        alt Quality Gates Pass
            QG->>CI: Approve for Deployment
            CI->>D: Ready to Deploy
        else Quality Gates Fail
            QG->>D: Quality Issues (Coverage < 80%, Performance Regression)
            D->>AI: Address Quality Issues
            AI->>TS: Generate Additional Tests
        end
    else Tests Fail
        TS->>FD: Analyze Test Failures
        FD->>FD: Detect Flaky vs Real Failures
        alt Real Failures Detected
            FD->>D: Implementation Issues Found
            D->>AI: Fix Implementation
            AI->>TS: Updated Code
        else Flaky Tests Detected
            FD->>D: Flaky Test Report
            D->>AI: Refine Flaky Tests
            AI->>TS: Stabilized Tests
        end
        TS->>CI: Re-run Test Pipeline
    end
    
    Note over D,FD: Continuous Improvement
    CI->>FD: Archive Test Metrics
    FD->>AI: Update Test Generation Patterns
    AI->>AI: Learn from Test Success/Failure Patterns
```

**Anti-pattern: Scattered Testing**
Generating tests with AI without a coherent strategy leads to poor coverage, flaky tests, and false confidence in code quality.

---

### Workflow Orchestration

**Maturity**: Advanced  
**Description**: Coordinate sequential pipelines, parallel agent workflows, and hybrid human-AI processes for complex development tasks. Transform synchronous single-agent workflows into asynchronous, event-driven multi-agent architectures while maintaining safety and consistency.

**Related Patterns**: [Handoff Protocols](#handoff-protocols), [Tool Integration](../README.md#tool-integration), [Testing Orchestration](#testing-orchestration), [Atomic Decomposition](../README.md#atomic-decomposition)

**Workflow Types & Selection**

```mermaid
graph TD
    A[Task Analysis] --> B{Workflow Type}
    B -->|Sequential| C[Pipeline Workflow]
    B -->|Parallel| D[Multi-Agent Workflow]
    B -->|Complex| E[Hybrid Workflow]
    
    C --> F[Stage 1: Generate]
    F --> G[Stage 2: Review]
    G --> H[Stage 3: Optimize]
    H --> I[Stage 4: Test]
    
    D --> J[Agent 1: Backend]
    D --> K[Agent 2: Frontend]
    D --> L[Agent 3: Tests]
    J --> M[Synchronization]
    K --> M
    L --> M
    
    E --> N[Human Planning]
    N --> O[AI Implementation]
    O --> P[Human Review]
    P --> Q[AI Refinement]
```

**Parallel Agent Coordination Sequence**

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant A1 as Backend Agent
    participant A2 as Frontend Agent  
    participant A3 as Test Agent
    participant C as Coordinator
    participant R as Review System
    participant H as Human
    
    Note over O,H: Task Breakdown & Assignment
    O->>C: Analyze Feature Requirements
    C->>O: Atomic Task Breakdown
    O->>A1: Assign: Auth API (2hrs)
    O->>A2: Assign: Login UI (1.5hrs)
    O->>A3: Assign: Test Suite (2hrs)
    
    Note over O,H: Parallel Execution Phase
    par Backend Development
        A1->>C: Start Backend Task
        A1->>A1: Implement JWT Auth API
        A1->>C: Backend Complete
    and Frontend Development
        A2->>C: Start Frontend Task
        A2->>A2: Build Login Components
        A2->>C: Frontend Complete
    and Test Development
        A3->>C: Start Test Task
        A3->>A3: Generate Test Suite
        A3->>C: Tests Complete
    end
    
    Note over O,H: Synchronization & Review
    C->>R: Trigger Integration Review
    R->>R: Analyze Outputs for Conflicts
    alt No Conflicts Detected
        R->>O: Integration Approved
        O->>H: Ready for Human Review
    else Conflicts Found
        R->>O: Conflict Report (API mismatch)
        O->>A1: Resolve API Contract Issue
        A1->>C: Resolution Complete
        C->>R: Re-trigger Review
        R->>O: Integration Approved
    end
    
    Note over O,H: Final Integration
    H->>O: Approve Integration
    O->>C: Merge All Components
    C->>H: Feature Complete
```

**Parallel Agent Coordination Examples**

```bash
# Atomic task breakdown for parallel execution
ai_task_manager "Break down user authentication feature into atomic tasks:
- Each task <2 hours completion time
- Independent implementation (no shared state)
- Clear input/output contracts
- Parallelizable across agents"

# Parallel agent execution with safety
ai_orchestrator --parallel --safe-mode \
  --task="backend-auth-api" --agent="backend-specialist" \
  --task="frontend-login-ui" --agent="frontend-specialist" \
  --task="integration-tests" --agent="testing-specialist" \
  --sync-point="integration-review"

# Safety-first parallel review
ai_reviewer --parallel-output \
  --check-conflicts \
  --verify-contracts \
  --merge-strategy="human-approval"
```

**Parallel Agent Safety Framework**

```yaml
# .ai/parallel-config.yml
parallel_safety:
  max_concurrent_agents: 3
  conflict_detection: enabled
  shared_resources:
    - "src/shared/"
    - "package.json"
    - "database/migrations/"
  isolation_boundaries:
    - backend: "src/api/"
    - frontend: "src/components/"
    - testing: "tests/"
  sync_points:
    - after_implementation
    - before_integration
    - before_deployment
```

**Anti-pattern: Chaotic Orchestration**
Using multiple AI tools without proper orchestration leads to inconsistent code, integration conflicts, and wasted effort from competing implementations.

**Anti-pattern: Unsafe Parallelism**
Running parallel agents without proper isolation, conflict detection, or sync points risks data corruption, merge conflicts, and system instability.

---

### Context Optimization

**Maturity**: Advanced  
**Description**: Match AI tool selection to task complexity and optimize cost/performance trade-offs by understanding different AI models' context window capabilities and computational costs.

**Related Patterns**: [Progressive Enhancement](../README.md#progressive-enhancement), [Choice Generation](../README.md#choice-generation)

**Tool Selection Decision Matrix**

| Task Complexity | Context Needed | Recommended Tool | Cost Level | Use Case |
|-----------------|----------------|------------------|------------|----------|
| Simple queries | <1K tokens | GPT-3.5, Claude Haiku | Low | Quick questions, simple code |
| Medium features | 1K-8K tokens | GPT-4, Claude Sonnet | Medium | Feature implementation |
| Complex systems | 8K-32K tokens | GPT-4 Turbo, Claude Opus | High | Architecture, large refactors |
| Massive codebases | 32K+ tokens | Claude-100K, GPT-4-128K | Premium | Full system analysis |

**Anti-pattern: Wasteful Context**
Always using the most powerful (expensive) AI model for simple tasks wastes resources and increases latency for routine operations.

---

### Image Spec

**Maturity**: Intermediate
**Description**: Upload images (diagrams, mockups, flows) as primary specifications for AI coding tools to build accurate implementations from visual context.

**Related Patterns**: [Spec-Driven Development](../README.md#spec-driven-development), [Progressive Enhancement](../README.md#progressive-enhancement), [Context Optimization](#context-optimization)

#### Core Implementation

```bash
# 1. Prepare visual specifications
# Create architecture diagram showing microservices structure
# Save as: architecture.png with labeled components:
# - API Gateway (port 8080)
# - User Service (port 3001)
# - Order Service (port 3002)  
# - Payment Service (port 3003)
# - PostgreSQL databases per service
# - RabbitMQ message bus connections

# 2. Upload to AI coding tool with minimal context
# Example prompt for Claude Code:
cat > build-request.txt << 'EOF'
Build this microservices architecture from the attached diagram.
Tech stack: Node.js, Express, PostgreSQL, RabbitMQ
Start with the User Service following the exact structure shown.
Include health check endpoints at /health for each service.
EOF

# 3. Iterate with visual feedback
# After initial generation, screenshot the running system
# Annotate screenshot with required changes
# Example: mark missing authentication flow in red
# Re-upload annotated screenshot with refinement request

# 4. Structure for complex UIs
# For dashboard implementation:
# - dashboard-layout.png (grid measurements, component names)
# - dashboard-interactions.png (click flows, state changes)
# - data-model.png (API responses, field mappings)

# Upload sequence with prompt:
"Implement this dashboard using React and Tailwind.
Match the layout from dashboard-layout.png exactly.
Use the interaction flows from dashboard-interactions.png.
Mock data structure should follow data-model.png."
```

#### Anti-pattern: Overwhelming Visuals

**Problem**: Uploading many diagrams at once (e.g., 15+) without structure or context

```bash
# Wrong approach - overwhelming context
"Here are all my diagrams. Build the system."
# Uploads: erd.png, architecture.png, flow1.png, flow2.png, 
# ui1.png, ui2.png, deployment.png, sequence1.png...

# Why it fails:
# - AI loses focus trying to parse everything
# - Contradictions between diagrams cause confusion
# - Exceeds useful context window
# - No clear starting point

# Correct approach:
# Upload progressively with clear hierarchy
"1. Start with this high-level architecture (architecture.png)
2. Focus on User Service first
3. I'll provide UI mockups after core services work"
```

---

### Event Automation

**Maturity**: Intermediate
**Description**: Execute custom commands automatically at specific lifecycle events (before/after file operations, session start, prompt submission) for workflow automation, validation, and policy enforcement.

**Related Patterns**: [Codified Rules](../README.md#codified-rules), [Security Sandbox](../README.md#security-sandbox)

**Core Concept**

Attach shell commands to AI assistant lifecycle events. Commands receive context via environment variables (file paths, tool names, user prompts) and return exit codes: `0` (allow), `2` (block), or other (warn).

**Event Flow Example**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant AI as AI Assistant
    participant Pre as PreToolUse Hook
    participant Post as PostToolUse Hook

    Dev->>AI: Edit .env file
    AI->>Pre: Run security-hook.sh
    Pre->>Pre: Check if file is sensitive
    Pre-->>AI: Exit 2 (BLOCK)
    AI->>Dev: ❌ Blocked: Cannot edit sensitive file

    Dev->>AI: Edit src/api.js
    AI->>Pre: Run security-hook.sh
    Pre->>Pre: Check if file is sensitive
    Pre-->>AI: Exit 0 (Allow)
    AI->>AI: Execute file edit
    AI->>Post: Run security-hook.sh
    Post->>Post: Scan for secrets with gitleaks
    alt Secret Found
        Post-->>AI: Exit 1 (Warning)
        AI->>Dev: ⚠️ Secret detected! Review before committing
    else No Secret
        Post-->>AI: Exit 0 (Success)
        AI->>Dev: ✅ Edit complete
    end
```

**Simple Security Example**

Prevent editing sensitive files and scan for secrets:

```bash
#!/bin/bash
# security-hook.sh

FILE="$TOOL_INPUT_FILE_PATH"

# Block .env and credentials files
if echo "$FILE" | grep -E "(\.env|secrets\.json|credentials)" > /dev/null; then
  echo "❌ Blocked: Cannot edit sensitive file"
  exit 2
fi

# Scan for hardcoded secrets (requires gitleaks)
if command -v gitleaks > /dev/null; then
  if gitleaks detect --no-git --source="$FILE" 2>&1 | grep -q "leaks found"; then
    echo "⚠️ Secret detected! Review before committing."
    exit 1
  fi
fi

exit 0
```

**Configuration Example (Claude Code)**

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit",
      "hooks": [{"type": "command", "command": "./security-hook.sh"}]
    }],
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{"type": "command", "command": "./security-hook.sh"}]
    }]
  }
}
```

**Common Use Cases**
- Auto-format code after edits (`prettier`, `black`, `gofmt`)
- Block sensitive file modifications
- Log AI interactions for compliance
- Run linters before commits

**Security Warning**

Event commands run with full system access. Always review scripts before enabling. Test in isolated environments first.

**Complete Example**

See [examples/event-automation/](examples/event-automation/) for a working implementation with security scanning and hooks.

**Anti-pattern: Unchecked Events**

Running automation from untrusted sources without review exposes your system to malicious code execution and credential theft. Always audit event scripts before installation.

---

### Custom Commands

**Maturity**: Intermediate
**Description**: Discover and use built-in command vocabularies, then extend them with custom commands that encode domain expertise and sophisticated workflows.

**Related Patterns**: [Event Automation](#event-automation), [Spec-Driven Development](../README.md#spec-driven-development), [Codified Rules](../README.md#codified-rules)

**Core Concept**

AI coding tools provide built-in commands for common operations and support custom commands (markdown files with AI instructions) for project-specific workflows. Commands are manual/on-demand (invoked like `/refactor`), while events fire automatically (see [Event Automation](#event-automation)).

**Command Discovery**

Discover built-in commands first:

```bash
# Claude Code
/help /model /clear /review

# Cursor IDE
Cmd+K /edit /chat

# Gemini CLI
/stats /memory /tools /clear
```

| Use Built-in Commands | Create Custom Commands |
|-----------------------|------------------------|
| Generic operations (clear, help, model) | Domain expertise (refactoring, security analysis) |
| Tool features (review, edit) | Project workflows (deploy, implement-spec) |
| Universal commands | Team standards and conventions |

**Example: Refactoring Assistant**

Encode Martin Fowler's refactoring catalog for systematic code improvement:

```markdown
---
description: Interactive refactoring assistant based on Martin Fowler's refactoring catalog
argument-hint: Optional flags (--smell, --duplicates, --suggest)
---

# Refactoring Assistant

You are helping a developer improve code maintainability by identifying code smells and recommending specific refactoring techniques from Martin Fowler's catalog.

## Usage
/refactor              # Full analysis
/refactor --smell      # Code smells only

## Implementation

### 1. Code Smell Detection
- Long methods (>20 lines), duplicate code, complex conditionals
- For each: location (file:line), severity, specific refactoring, effort estimate

### 2. Bloater Detection
- Excessive parameters (>4), data clumps, primitive obsession

### 3. Refactoring Strategy
1. Name the code smell
2. Recommend technique from Fowler's catalog
3. Show before/after example
4. Estimate maintainability improvement

Generate step-by-step refactoring plan prioritized by impact.
```

**More Examples**

Additional command examples with detailed implementations:

- **[Implement-Spec](examples/custom-commands/implement-spec-example.md)** - Spec-driven implementation with TDD and traceability
- **[Security Review](examples/custom-commands/security-review-example.md)** - Multi-layer security analysis (secrets, vulnerabilities, config)
- **[Safe-Refactor](examples/custom-commands/safe-refactor-example.md)** - Safe refactoring with automated testing and rollback
- **[Test Runner](examples/custom-commands/test-example.md)** - Smart test selection with coverage and health monitoring

**Tool Support**

```bash
# Claude Code: .claude/commands/*.md
mkdir -p .claude/commands
cp commands/refactor.md .claude/commands/

# Cursor IDE: .cursorrules
cat commands/refactor.md >> .cursorrules

# Generic: .ai/commands/ (tool-agnostic)
mkdir -p .ai/commands
```

**Complete Implementation**

See [examples/custom-commands/](examples/custom-commands/) for ready-to-use commands, configuration files, and setup guide.

**Anti-pattern: Redundant Commands**

Creating `/clear` when the tool already provides it. Always discover built-in commands first.

**Anti-pattern: Shallow Commands**

```markdown
# Bad: Just wraps shell command
Run: npm run deploy:staging

# Good: Encodes expertise
1. Verify staging environment health
2. Check for active incidents
3. Review recent commits for risk
4. Run deployment with rollback plan
```

**Anti-pattern: Hardcoded Context**

```markdown
# Bad: Hardcoded values
Deploy to prod-db-instance-1.us-east-1.rds.amazonaws.com

# Good: Parameterized
Deploy to database: $1 (default: $STAGING_DB)
```

---

### Progressive Disclosure

**Maturity**: Intermediate
**Description**: Load AI assistant rules incrementally based on task context rather than bundling all instructions upfront, preventing context bloat and maintaining instruction-following consistency across any AI coding assistant (Claude Code, Cursor, Codex, Gemini, etc.).

**Related Patterns**: [Codified Rules](../README.md#codified-rules), [Context Optimization](#context-optimization), [Custom Commands](#custom-commands), [Event Automation](#event-automation)

**Source**: HumanLayer, "Context engineering: Why your CLAUDE.md is probably too long" (research on instruction limits and context optimization)

#### Core Problem

**Instruction saturation**: LLMs can follow ~150-200 instructions with reasonable consistency. AI coding assistants' system prompts already contain ~50 instructions, leaving ~100-150 for your project rules. Loading all rules every session causes:

- Linear decay in instruction-following accuracy
- Context window waste on irrelevant rules
- Cognitive overload for the AI
- Slower response times from processing unnecessary context

**Example of bloat**: A 500-line configuration file (CLAUDE.md, AGENTS.md, .cursorrules, etc.) with security rules, deployment procedures, architecture patterns, testing standards, code style guides, API conventions, database migration rules, monitoring setup, and team workflows—but only 10% is relevant to any single task.

#### Implementation Strategy

**Three-tier rule architecture:**

This pattern works with any AI assistant configuration file. Examples shown use CLAUDE.md, but apply equally to .cursorrules (Cursor), AGENTS.md, or other AI coding assistant configuration files (Codex, Gemini, etc.).

```
.ai/
├── CLAUDE.md                    # Main rules file: Universal rules only (<60 lines)
│                                # (or AGENTS.md, .cursorrules, etc.)
├── rules/                       # Specialized rules loaded on-demand
│   ├── security/
│   │   ├── secrets.md          # Load when: editing .env, credentials
│   │   ├── dependencies.md     # Load when: package.json, requirements.txt
│   │   └── authentication.md   # Load when: auth/ directory work
│   ├── development/
│   │   ├── api-design.md       # Load when: working in api/ or routes/
│   │   ├── database.md         # Load when: migrations/, models/
│   │   ├── testing.md          # Load when: tests/ or spec files
│   │   └── frontend.md         # Load when: components/, styles/
│   ├── operations/
│   │   ├── deployment.md       # Load when: Dockerfile, k8s/, terraform/
│   │   ├── monitoring.md       # Load when: logs, metrics, alerts
│   │   └── cicd.md            # Load when: .github/workflows/
│   └── architecture/
│       ├── patterns.md         # Load when: major refactoring
│       └── performance.md      # Load when: optimization tasks
└── prompts/                     # Reusable task templates
    ├── implement-feature.md
    └── fix-bug.md
```

#### Main Rules File

**Keep it minimal** - only universally applicable rules.

This example uses CLAUDE.md, but the same structure applies to AGENTS.md, .cursorrules, or any AI assistant configuration file:

```markdown
# AI Development Rules

## Universal Principles (Always Apply)

### Code Quality
- Write clear, self-documenting code with meaningful names
- Follow existing patterns in the codebase
- Include error handling for all external calls

### Communication
- Ask clarifying questions before major changes
- Explain non-obvious decisions in comments
- Reference task/issue numbers in commits

### Safety
- Never commit secrets, API keys, or credentials
- Run tests before committing code changes
- Check git diff before every commit

### Context Loading (Progressive Disclosure)
When working in specific areas, load specialized rules:

- **Security work** (auth/, .env, credentials): Read .ai/rules/security/
- **API development** (api/, routes/): Read .ai/rules/development/api-design.md
- **Database changes** (migrations/, models/): Read .ai/rules/development/database.md
- **Testing** (tests/, specs/): Read .ai/rules/development/testing.md
- **Frontend** (components/, styles/): Read .ai/rules/development/frontend.md
- **Deployment** (Dockerfile, k8s/): Read .ai/rules/operations/deployment.md
- **CI/CD** (.github/workflows/): Read .ai/rules/operations/cicd.md

**How to load**: "Before proceeding, read the relevant rules from .ai/rules/[category]/"
```

**Key insight**: The main file becomes a **router** that tells the AI which specialized rules to load based on context.

#### Specialized Rules Examples

**Example: .ai/rules/security/secrets.md**

```markdown
# Security: Secret Management Rules

## When to Load
Load this file when working with:
- .env files or environment variables
- credentials.json, secrets.yaml, config files with sensitive data
- Authentication tokens or API keys
- Deployment configurations with passwords

## Rules

### Secret Detection
1. Run `gitleaks detect --no-git --source=<file>` before committing
2. Block commits containing patterns: AWS keys, JWT tokens, database passwords
3. Use environment variable references, never hardcoded values

### Environment Variables
# CORRECT: Reference variables
DATABASE_URL=${DATABASE_URL}
API_KEY=${STRIPE_API_KEY}

# WRONG: Hardcoded secrets
DATABASE_URL=postgresql://admin:password123@prod-db.com
API_KEY=sk_live_abc123xyz

### Credential Files
- NEVER edit .env files directly
- Use .env.example templates with placeholder values
- All secrets go in secret management (AWS Secrets Manager, 1Password)

### Validation
Before committing, verify:
# No secrets in staged files
git diff --cached | gitleaks detect --no-git --verbose --source=/dev/stdin

# No .env files staged
git diff --cached --name-only | grep -E "(\.env$|credentials)" && exit 1
```

**Example: .ai/rules/development/api-design.md**

```markdown
# Development: API Design Rules

## When to Load
Load this file when working with:
- api/, routes/, controllers/ directories
- HTTP endpoint implementation
- API contract changes

## Rules

### RESTful Design
- Use standard HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE
- Plural nouns for resources: `/users`, `/orders`, not `/getUser`
- Nest related resources: `/users/:id/orders` for user-specific orders

### Response Format
All API responses must use this structure:
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "abc-123"
  }
}

### Error Handling
// CORRECT: Structured errors
res.status(404).json({
  success: false,
  data: null,
  error: {
    code: "USER_NOT_FOUND",
    message: "User with ID 123 not found",
    details: { user_id: 123 }
  }
});

// WRONG: Generic errors
res.status(500).send("Error");

### Validation
- Validate all inputs at API boundary
- Return 400 Bad Request with specific validation errors
- Document all endpoints in OpenAPI/Swagger spec
```

#### Decision Framework for Rule Loading

```mermaid
graph TD
    A[AI Assistant Receives Task] --> B{Analyze Task Context}

    B -->|File paths mentioned| C[Extract directory/file patterns]
    B -->|Task description keywords| D[Identify domain area]

    C --> E{Match Pattern}
    D --> E

    E -->|auth/, .env, credentials| F[Load security/ rules]
    E -->|api/, routes/| G[Load api-design.md]
    E -->|migrations/, models/| H[Load database.md]
    E -->|tests/, spec/| I[Load testing.md]
    E -->|components/, styles/| J[Load frontend.md]
    E -->|Dockerfile, k8s/| K[Load deployment.md]
    E -->|.github/workflows/| L[Load cicd.md]
    E -->|No specific pattern| M[Use main rules only]

    F --> N[Execute Task with Specialized Context]
    G --> N
    H --> N
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N
```

#### Automatic Loading with Event Hooks

Combine Progressive Disclosure with [Event Automation](#event-automation) for automatic context loading:

```bash
#!/bin/bash
# .ai/hooks/auto-load-context.sh
# Runs before AI tool use to automatically load relevant rules

FILE_PATH="$TOOL_INPUT_FILE_PATH"
LOADED_RULES=""

# Security context
if echo "$FILE_PATH" | grep -E "(\.env|credentials|secrets|auth/)" > /dev/null; then
  LOADED_RULES="$LOADED_RULES .ai/rules/security/"
fi

# API development context
if echo "$FILE_PATH" | grep -E "(api/|routes/|controllers/)" > /dev/null; then
  LOADED_RULES="$LOADED_RULES .ai/rules/development/api-design.md"
fi

# Database context
if echo "$FILE_PATH" | grep -E "(migrations/|models/|database/)" > /dev/null; then
  LOADED_RULES="$LOADED_RULES .ai/rules/development/database.md"
fi

# Testing context
if echo "$FILE_PATH" | grep -E "(tests?/|spec/|\.test\.|\.spec\.)" > /dev/null; then
  LOADED_RULES="$LOADED_RULES .ai/rules/development/testing.md"
fi

# Output loaded context as AI message
if [ -n "$LOADED_RULES" ]; then
  echo "📋 Auto-loading specialized rules for this context:"
  for rule in $LOADED_RULES; do
    echo "  - $rule"
  done
  echo ""
  echo "AI: Please read these files before proceeding: $LOADED_RULES"
fi

exit 0  # Allow operation to continue
```

**Hook configuration (example for Claude Code, adapt for your AI assistant)**:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": ".ai/hooks/auto-load-context.sh"}]
    }]
  }
}
```

#### Integration with Custom Commands

Create commands that automatically load relevant context:

```markdown
---
description: Implement API endpoint with auto-loaded API design rules
argument-hint: endpoint_name (e.g., "GET /users/:id")
---

# API Implementation with Progressive Disclosure

Before implementing the API endpoint, I will:

1. **Auto-load specialized context**:
   - Read `.ai/rules/development/api-design.md` for API standards
   - Read `.ai/rules/security/authentication.md` if endpoint requires auth
   - Read `.ai/rules/development/testing.md` for test requirements

2. **Implement endpoint** following loaded rules:
   - RESTful design patterns from api-design.md
   - Error handling standards
   - Input validation requirements
   - Response format consistency

3. **Generate tests** following testing.md:
   - Happy path tests
   - Error case coverage
   - Authentication/authorization tests
   - Input validation tests

4. **Verify compliance**:
   - Check against API design rules
   - Run security validation
   - Ensure test coverage >80%

Implement: $ARGUMENTS
```

#### Validation & Metrics

**Measure effectiveness**:

```bash
# Count instructions in main file (target: <60 lines of actual rules)
grep -v "^#" .ai/CLAUDE.md | grep -v "^$" | wc -l

# Count specialized rule files (aim for 5-10 domain areas)
find .ai/rules -name "*.md" | wc -l

# Track context loading patterns (add to event hooks)
echo "$(date): Loaded $LOADED_RULES for $FILE_PATH" >> .ai/context-usage.log

# Analyze which rules are most frequently loaded
cat .ai/context-usage.log | grep -oE "rules/[^/]+/[^ ]+" | sort | uniq -c | sort -rn
```

**Success criteria**:
- Main CLAUDE.md: <60 lines of actual instructions (excluding comments/blank lines)
- Specialized rules: 5-10 focused files, each <100 lines
- Context loading: Automatic via hooks or explicit in commands
- Instruction count per session: <150 total (main + loaded specializations)

#### Anti-pattern: Bloated Configuration

**Problem**: Putting all rules in a single configuration file regardless of relevance.

```markdown
# AI Configuration File - WRONG APPROACH (500+ lines)
# (applies to CLAUDE.md, AGENTS.md, .cursorrules, etc.)

## Security Rules (100 lines)
- Secret management for .env files
- Dependency scanning procedures
- Authentication implementation standards
- OAuth flow requirements
- API key rotation policies
...

## Database Rules (80 lines)
- Migration file naming
- Model relationship patterns
- Query optimization guidelines
- Index creation standards
...

## API Design Rules (90 lines)
- RESTful endpoint patterns
- Response format requirements
- Error handling standards
...

## Frontend Rules (110 lines)
- Component structure
- State management patterns
- CSS conventions
...

## Deployment Rules (70 lines)
- Docker build optimization
- Kubernetes manifests
- Blue-green deployment
...

## Testing Rules (50 lines)
...
```

**Why it fails**:
- AI task: "Fix typo in README.md"
- Loaded context: ALL 500 lines of rules (security, database, API, frontend, deployment, testing)
- Relevant context: Maybe 10 lines about code quality and git commit messages
- Result: 490 lines of wasted context, reduced instruction-following accuracy
- Performance: Slower responses, more hallucinations, missed critical instructions

**Consequences**:
1. **Instruction decay**: With 500+ instructions loaded, AI follows maybe 60-70% accurately
2. **Context waste**: 90% of loaded rules are irrelevant to the task
3. **Maintenance burden**: Editing security rules requires opening 500-line file
4. **Slow responses**: AI processes unnecessary context before every response
5. **Higher costs**: More tokens consumed per interaction
6. **Cognitive overload**: New team members overwhelmed by monolithic config

**Correct approach**: Progressive Disclosure
- Main file: 40 lines of universal rules + routing instructions
- Specialized files: 8 files × 60 lines = 480 lines total
- Per-task context: 40 (main) + 60 (relevant specialization) = 100 instructions
- Result: 3x better instruction-following, faster responses, easier maintenance

#### Anti-pattern: Over-Fragmentation

**Problem**: Creating too many tiny rule files that require constant loading.

```
.ai/rules/
├── api/
│   ├── get-endpoints.md      # 10 lines
│   ├── post-endpoints.md     # 12 lines
│   ├── put-endpoints.md      # 11 lines
│   ├── delete-endpoints.md   # 9 lines
│   ├── error-handling.md     # 8 lines
│   ├── validation.md         # 15 lines
│   ├── response-format.md    # 10 lines
│   └── versioning.md         # 7 lines
...
```

**Why it fails**:
- API implementation task requires loading 8 different files
- Overhead of reading 8 files > benefit of separation
- Harder to maintain consistency across related rules
- AI must constantly re-read interconnected files

**Correct approach**: Balance granularity
- Combine related rules: api-design.md (all API rules, ~80 lines)
- Split by clear domains: security/, development/, operations/
- Aim for 5-10 specialized files, not 50

#### Anti-pattern: Missing Guidance

**Problem**: Creating specialized rule files but not telling the AI when to load them.

```markdown
# Main Configuration File (no routing)
# (CLAUDE.md, AGENTS.md, .cursorrules, etc.)
Follow the project coding standards.

# (Specialized rules exist in .ai/rules/ but AI never knows to load them)
```

**Why it fails**:
- AI doesn't know specialized rules exist
- Relies on human to remember: "also read .ai/rules/security/secrets.md"
- No automation or consistency

**Correct approach**: Explicit routing in main file
- Document WHEN to load each specialized file
- Provide file path patterns that trigger loading
- Use event hooks for automatic loading
- Include loading instructions in custom commands

---

### Asynchronous Research

**Maturity**: Intermediate
**Description**: Use fire-and-forget coding agents in dedicated repositories to conduct autonomous code investigations that prove technical feasibility through executable experiments.

**Related Patterns**: [Parallel Agents](../README.md#parallel-agents), [Context Persistence](../README.md#context-persistence), [Choice Generation](../README.md#choice-generation)

**Source**: Simon Willison, "[Code research projects with async coding agents](https://simonwillison.net/2025/Nov/6/async-code-research/)", November 6, 2025

#### Core Concept

**"Code research"** - answering technical questions definitively by writing and executing code. Simon's key insight: *"The great thing about questions about code is that they can often be definitively answered by writing and executing code."*

Use asynchronous coding agents (Claude Code for web, Codex Cloud, Gemini Jules, GitHub Copilot) to conduct autonomous investigations in dedicated research repositories. Fire-and-forget execution allows 2-3 research tasks per day with minimal human oversight.

**Why it works**: *"LLMs hallucinate and make mistakes. This is far less important for code research tasks because the code itself doesn't lie: if they write code and execute it and it does the right things then they've demonstrated to both themselves and to you that something really does work."*

#### Implementation Pattern

**1. Dedicated Research Repository**

Create separate repository from production code to enable unrestricted experimentation:

```bash
# Create dedicated research repo (public or private)
gh repo create my-research --private

# Configure for unrestricted network access
# Claude Code: Settings → Enable network access
# Codex Cloud: Enable full sandbox permissions
# Jules: Default unrestricted access
```

**Key benefits:**
- Safe to grant full network access (no production secrets)
- One folder per research task
- Archive of explorations for future reference
- "Slop containment" - keeps AI-generated content separate

**2. Research Question Formulation**

Convert technical curiosity into testable hypothesis with clear deliverables:

**Good research questions (from Simon's examples):**
- "Could Redis Streams handle 10k concurrent notification subscribers?"
- "How do 7 Python Markdown libraries compare on performance?"
- "Can cmarkgfm C extension compile for Pyodide WebAssembly?"

**Example prompt (Simon's markdown comparison):**
```
Create a performance benchmark and feature comparison report on PyPI cmarkgfm
compared to other popular Python markdown libraries—check all of them out from
github and read the source to get an idea for features, then design and run a
benchmark including generating some charts, then create a report in a new
python-markdown-comparison folder. Make sure the performance chart images are
directly displayed in the README.md in the folder.
```

**3. Asynchronous Execution Workflow**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Agent as Async Agent
    participant Repo as Research Repo

    Note over Dev,Repo: Fire and Forget Pattern
    Dev->>Agent: Submit research prompt (2-3 paragraphs)
    Agent->>Agent: Autonomous execution (10-30 min)
    Agent->>Agent: Install deps, fetch data, run experiments
    Agent->>Repo: Commit results via PR

    Note over Dev,Repo: Minimal Human Review
    Repo->>Dev: Notification: Research complete
    Dev->>Repo: Skim report for key insights
    Dev->>Repo: Merge if useful, discard if not

    Note over Dev,Repo: Cumulative Learning
    Dev->>Agent: New research building on previous
    Agent->>Repo: Reference earlier research findings
    Agent->>Repo: Commit enhanced results
```

**4. Network Access Configuration**

Simon's critical insight: For dedicated research repos, **unrestricted network access is safe and essential**.

**Why it's safe:** "Lethal trifecta" prompt injection attacks only matter if there are secrets to steal. Research repos have no production credentials.

**What unrestricted access enables:**
- Install any dependencies (pip, npm, cargo, apt-get)
- Fetch data from web APIs and documentation
- Clone external repositories
- Download datasets for benchmarking
- Access Stack Overflow, documentation sites

**5. Result Capture & Deliverables**

**Typical agent outputs:**
- Working proof-of-concept code
- Benchmark results with charts/visualizations
- Test scripts proving functionality
- Markdown reports explaining findings
- JSON data files with measurements

**Simon's example results:**

**python-markdown-comparison:**
- Benchmarked 7 Markdown libraries
- Generated performance bar charts
- Found cmarkgfm 10-52x faster than alternatives
- Feature comparison matrix

**cmarkgfm-in-pyodide:**
- Compiled 88.4KB `.whl` with C extension for WebAssembly
- Proved it loads in Pyodide inside Node.js
- When stuck, Simon prompted: *"Complete this project, actually run emscripten, I do not care how long it takes"*

**blog-tags-scikit-learn:**
- Downloaded SQLite database, trained ML models
- Generated JSON results for multiple approaches
- Python scripts for reproduction

**Human review approach:**
- Skim report for key insights
- Verify research question was answered
- Don't audit code line-by-line (it's exploratory)
- Accept as "slop" (AI-generated, not production-quality)

**6. Cross-Project Learning**

Research tasks build on each other within same repository:

```bash
# Research task 1: Prove Node.js can run Pyodide
# Result: node-pyodide/ folder with working example

# Research task 2: Build on previous finding
# Prompt: "Building on the node-pyodide example, compile cmarkgfm
# C extension for Pyodide and prove it works in Node.js"
# Result: cmarkgfm-in-pyodide/ folder reusing earlier work
```

Simon added `AGENTS.md` to his research repo with guidance for future agent runs—creating institutional memory.

#### Example Research Tasks

**Performance Benchmark:**
```
Work in new folder: redis-performance/

Build Redis Streams notification system.
Simulate 10,000 users receiving 100 notifications/second.
Run for 1 hour and measure:
- Memory usage over time
- P95 latency for delivery
- Behavior under network partition
- Recovery after Redis restart

Produce Python code, charts, detailed markdown report.
```

**Library Comparison:**
```
Work in new folder: python-markdown-comparison/

Benchmark these Python Markdown libraries:
- cmarkgfm, mistune, markdown2, commonmark, mistletoe, marko, markdown

For each library:
1. Clone from GitHub, analyze features from source
2. Run performance tests (small/medium/large documents)
3. Measure parsing speed, memory usage
4. Generate comparison charts
5. Create feature matrix

Output: README.md with embedded charts, raw benchmark data as JSON.
```

**Feasibility Study:**
```
Work in new folder: rust-wasm-integration/

Investigate if Rust crate 'pulldown-cmark' can compile to WebAssembly
and run in browser with acceptable performance.

Tasks:
1. Compile pulldown-cmark to wasm32-unknown-unknown target
2. Create minimal HTML page loading the WASM module
3. Benchmark parse time vs JavaScript alternatives
4. Document build process and dependencies
5. Identify any browser compatibility issues

Deliverable: Working demo + performance comparison + build guide.
```

#### Platforms (as of November 2025)

| Platform | Free Tier | Network Access | Best For |
|----------|-----------|----------------|----------|
| **Claude Code (web)** | $250 credits for $20/month users (until Nov 18, 2025) | Configurable | Complex research, multi-file projects |
| **Gemini Jules** | Free tier available | Default unrestricted | Quick explorations, proof-of-concepts |
| **Codex Cloud** | Pay-as-you-go | Configurable | Enterprise research workflows |
| **GitHub Copilot Agent** | Enterprise plans | Configurable | GitHub-integrated research |

#### Simon's Success Metrics

From 2 weeks of practice (as of November 6, 2025):

- **13 research projects** completed in 2 weeks (~1/day average)
- **2-3 research tasks/day** at peak
- **Minutes of human time** per task (just prompt formulation + review)
- **10-30 minutes** typical agent execution time
- **Frequent useful results** informing development decisions

**Quote from Simon:** *"I'm firing off 2-3 code research projects a day right now. My own time commitment is minimal and they frequently come back with useful or interesting results."*

#### Integration with Development Workflow

**Research → Decision → Implementation cycle:**

```
Technical Question
  ↓
Research Prompt (2-3 paragraphs)
  ↓
Async Agent Execution (10-30 min)
  ↓
Working Code + Findings
  ↓
Informed Decision
  ↓
Choice Generation / Planned Implementation
  ↓
Production Code
```

**How it complements other patterns:**

- **Before Choice Generation**: Validate which options are technically feasible
- **Before Planned Implementation**: Provide real performance data for planning
- **With Context Persistence**: Archive research for future sessions
- **With Parallel Agents**: Run multiple research questions simultaneously

#### Complete Example

See [examples/asynchronous-research/](examples/asynchronous-research/) for:
- Setup scripts for research repositories
- Platform configuration guides (Claude Code, Jules, Codex)
- Reusable prompt templates
- Sample research projects
- GitHub Action for auto-generating research index

#### Anti-pattern: Blind Investigation

**Problem**: Vague research prompts without clear goals or success criteria.

```bash
# Bad - No clear objective
"Investigate Redis and try some stuff with notifications"

# Why it fails:
# - Agent doesn't know what to prove
# - No measurable success criteria
# - Results won't connect to actual use case
# - Wastes compute on unfocused exploration

# Good - Specific, testable hypothesis
"Build proof-of-concept notification system using Redis Streams.
Simulate 10,000 concurrent users, 100 notifications/second.
Measure memory, P95 latency, partition behavior over 1 hour.
Produce Python code, charts, detailed report."
```

#### Anti-pattern: Uncontained Slop

**Problem**: Publishing AI-generated research directly to main documentation without review.

Simon's approach:
- Keep research in dedicated repo
- Mark repo as `noindex` for search engines
- *"I still like to keep AI-generated content out of search, to avoid contributing more to the dead internet."*

#### Anti-pattern: Leaked Secrets

**Problem**: Running unrestricted agents on production repos containing credentials.

Simon warns: *"A prompt injection attack of the lethal trifecta variety could easily be used to steal sensitive code or environment variables."*

**Solution**: Only use unrestricted access on dedicated, secret-free research repos.

#### Anti-pattern: Unfounded Impossibility

**Problem**: Expecting agents to prove something can't be done.

Simon's caveat: *"They can't prove something is impossible—just because the coding agent couldn't find a way to do something doesn't mean it can't be done."*

**Use for**: Proving feasibility, not impossibility.

---

## Operations Automation

### Centralized Rules

**Maturity**: Advanced
**Description**: Enforce organization-wide AI rules through a central Git repository that syncs to standard AI assistant configuration files (CLAUDE.md, AGENTS.md, .cursorrules) with automatic language and framework detection.

**Related Patterns**: [Codified Rules](../README.md#codified-rules), [Progressive Disclosure](#progressive-disclosure), [Security Orchestration](../README.md#security-orchestration)

#### Core Implementation

**Sync-based Architecture** (Recommended):

```
Central Rules Repository (Git)
  ├── base/universal-rules.md
  ├── languages/ (python.md, typescript.md, go.md)
  └── frameworks/ (react.md, django.md, fastapi.md)
           ↓
    [sync-ai-rules.sh]
           ↓
  Project Repository
    ├── CLAUDE.md (auto-generated)
    ├── AGENTS.md (auto-generated)
    └── .cursorrules (auto-generated)
```

**How it works**:

1. **Central repository** stores organization rules organized by language/framework
2. **Sync script** detects project language (Python, TypeScript, Go) and framework (React, Django, FastAPI)
3. **Auto-generates** standard config files (CLAUDE.md, .cursorrules, etc.) with relevant rules
4. **Works offline** - no API calls, no internet dependencies after initial sync

**Example sync**:
```bash
# One-time setup per project
curl -O https://yourorg.com/sync-ai-rules.sh
chmod +x sync-ai-rules.sh

# Run sync (manual or via pre-commit hook)
./sync-ai-rules.sh

# Generates CLAUDE.md with:
# - Universal org rules
# - Python-specific rules (auto-detected from pyproject.toml)
# - FastAPI rules (auto-detected from dependencies)
```

**Key benefits**:
- ✅ **Works with existing AI tools** - Claude Code, Cursor, Gemini all read standard config files
- ✅ **Offline-friendly** - No API gateway, no internet dependencies
- ✅ **Simple** - Single bash script, no Node.js services to deploy
- ✅ **Language-aware** - Auto-detects Python/TypeScript/Go and pulls relevant rules
- ✅ **Version-controlled** - Rules in Git, changes are auditable

**Alternative: Gateway Pattern** (for advanced use cases):

For organizations needing input/output filtering, policy enforcement, or usage logging, see [examples/centralized-rules/gateway-strategy/](examples/centralized-rules/gateway-strategy/) for API gateway approach with:
- Request/response filtering
- Policy-as-code integration (OPA/Cedar)
- Centralized audit logging
- Usage metrics aggregation

Complete Examples:
- **[Sync Strategy](examples/centralized-rules/sync-strategy/)** - Simple Git-based sync (recommended)
- **[Gateway Strategy](examples/centralized-rules/gateway-strategy/)** - Advanced API gateway pattern

#### Anti-pattern: Scattered Configuration

Copying AI rule files into every repository without central source:

```
repo-a/.cursorrules    # v1.2 of org rules
repo-b/CLAUDE.md       # v1.1 (outdated)
repo-c/.ai/rules/      # Custom fork, diverged
```

**Problems**:
- Rules drift across repositories
- Manual updates required for every repo
- No consistency enforcement
- Difficult to track which repos have current rules

**Solution**: Use centralized sync approach where rules are maintained in one place and automatically distributed to projects.

---

### Review Automation

**Maturity**: Intermediate  
**Description**: Automate review process for parallel agent outputs using AI to detect conflicts and coordinate integration.

**Related Patterns**: [Workflow Orchestration](#workflow-orchestration), [Atomic Decomposition](../README.md#atomic-decomposition), [Parallel Agents](../README.md#parallel-agents)

**Automated Review and Merge System**

```bash
#!/bin/bash
# automated-review.sh - Complete parallel agent review and integration

echo "=== Review Automation for Parallel Agents ==="

# 1. Detect conflicts between agent outputs
echo "Scanning for conflicts across agent workspaces..."

ai "Analyze parallel agent outputs for integration issues:

Agent workspaces: $(ls -d workspace/agent-* 2>/dev/null || echo 'none')

Check for:
1. File conflicts (same files modified by multiple agents)
2. API contract mismatches (function signatures, return types)
3. Dependency version conflicts
4. Naming collisions (classes, functions, variables)
5. Integration compatibility issues

For each conflict found:
- Identify which agents are involved
- Assess conflict severity (critical/medium/low)
- Suggest resolution strategy
- Generate merge commands when possible

Output structured JSON with conflicts and resolutions."

# 2. Run quality gates and validation
echo "Running quality gates on combined outputs..."

ai "Validate merged agent outputs meet quality standards:

Quality checks:
- Syntax validation (python -m py_compile)
- Type checking (mypy)
- Security scan (bandit)
- Test coverage (>80% requirement)
- Performance regression check

Generate integration tests that:
- Import all agent outputs without conflicts
- Test cross-agent functionality
- Verify API compatibility
- Check end-to-end workflows

Return pass/fail status with specific issues found."

# 3. Auto-merge or request human review
if [ $? -eq 0 ]; then
    echo "✅ Quality gates passed - proceeding with automatic merge"
    
    # Merge agent outputs
    mkdir -p workspace/merged
    for agent_dir in workspace/agent-*; do
        rsync -av --ignore-existing "$agent_dir/" workspace/merged/
    done
    
    # Run integration tests
    cd workspace/merged && python -m pytest tests/integration/ -v
    
    if [ $? -eq 0 ]; then
        echo "✅ Integration tests passed - merge complete"
        rsync -av workspace/merged/ src/
        rm -rf workspace/agent-*
    else
        echo "❌ Integration tests failed - manual review required"
    fi
else
    echo "⚠️ Quality gates failed - human review required"
    # Create review report for humans
    ai "Generate human-readable review report with:
    - Summary of all conflicts found
    - Recommended resolution steps
    - Risk assessment for each issue
    - Estimated effort to resolve manually"
fi
```

**Anti-pattern: Manual Reviews**
Relying entirely on human reviewers for parallel agent outputs creates bottlenecks and misses systematic integration issues that automated tools can catch.

---

### Debt Forecasting

**Maturity**: Intermediate  
**Description**: Proactively identify and prioritize technical debt using AI-powered code analysis.

**Related Patterns**: [Guided Refactoring](../README.md#guided-refactoring), [Guided Architecture](../README.md#guided-architecture), [Tool Integration](../README.md#tool-integration)

```bash
ai "Analyze codebase for technical debt indicators and forecast maintenance burden:
1. Code complexity hotspots
2. Cyclomatic complexity trends  
3. Dependency staleness
4. Test coverage gaps
5. Documentation drift
Prioritize by maintenance cost and business impact."
```

**Anti-pattern: Reactive Debt**
Waiting until technical debt becomes a crisis instead of continuously monitoring and addressing it through predictive analysis.

---

### Pipeline Synthesis

**Maturity**: Intermediate  
**Description**: Convert plain-English build specifications into CI/CD pipeline configurations.

**Related Patterns**: [Workflow Orchestration](#workflow-orchestration), [Tool Integration](../README.md#tool-integration)

```bash
ai "Generate GitHub Actions workflow from specification:
Build Requirements:
- Node.js 18 with npm ci
- Run tests with jest
- Deploy to AWS on main branch push
- Require test coverage >80%

Output complete .github/workflows/ci.yml with security best practices."
```

**Anti-pattern: Manual Pipelines**
Hand-crafting and updating CI/CD configurations instead of generating them from requirements specifications leads to inconsistency and maintenance burden.

---

### Deployment Synthesis

**Maturity**: Advanced  
**Description**: Generate blue-green deployment scripts with validation to prevent AI misconceptions about deployment strategies.

**Related Patterns**: [Pipeline Synthesis](#pipeline-synthesis)

**Important**: AI tools often confuse blue-green with canary deployments. Blue-green requires full environment duplication and instant traffic switching.

```yaml
# blue-green-deploy.yml - Full environment switch pattern
deployment_strategy: "blue-green"
traffic_routing:
  method: "dns_switch"  # Instant 100% traffic switch
  rollback_time: "< 30 seconds"
environments:
  blue:
    infrastructure: "complete duplicate"
    traffic_percentage: "100% OR 0%"  # Never split
  green:
    infrastructure: "complete duplicate" 
    traffic_percentage: "0% OR 100%"  # Never split
validation:
  health_checks: ["api_health", "database_connection"]
  smoke_tests: ["critical_user_flows"]
  approval_required: true
```

**Anti-pattern: Confused Deployment**
AI-generated deployment scripts that mix blue-green and canary strategies, resulting in complex traffic splitting instead of simple environment switching.

---

### Drift Remediation

**Maturity**: Advanced  
**Description**: Detect infrastructure configuration drift and generate corrective patches automatically.

**Related Patterns**: [Pipeline Synthesis](#pipeline-synthesis)

```bash
ai "Compare current AWS infrastructure against Terraform state:
1. Identify configuration drift in EC2, RDS, S3
2. Generate corrective Terraform plan
3. Assess drift risk level (critical/medium/low)
4. Create automated remediation script with approval gates"
```

**Anti-pattern: Manual Drift**
Relying on periodic manual infrastructure audits instead of continuous automated drift detection and remediation.

---

### Release Synthesis

**Maturity**: Beginner  
**Description**: Automatically generate structured release notes by analyzing git commit history.

**Related Patterns**: [Pipeline Synthesis](#pipeline-synthesis)

```bash
ai "Generate release notes from git log --since='2 weeks ago':
Format:
## Features
## Bug Fixes  
## Breaking Changes
## Dependencies

Group by conventional commit prefixes and business impact."
```

**Anti-pattern: Manual Releases**
Writing release notes manually from memory instead of systematically analyzing commit history and pull request descriptions.

---

## Monitoring & Intelligence

### Incident Automation

**Maturity**: Advanced  
**Description**: Generate actionable incident response playbooks from historical incident data.

**Related Patterns**: [Baseline Management](../README.md#baseline-management)

```bash
ai "Analyze last 50 incidents in PagerDuty/AWS CloudWatch to:
1. Identify common failure patterns
2. Generate step-by-step runbooks
3. Create automated triage rules
4. Suggest preventive monitoring alerts"
```

**Anti-pattern: Static Runbooks**
Maintaining outdated incident response procedures instead of continuously improving them based on actual incident patterns and outcomes.

---

### Suite Health

**Maturity**: Intermediate  
**Description**: Analyze build history to identify and remediate flaky tests automatically.

**Related Patterns**: [Testing Orchestration](#testing-orchestration)

```bash
ai "Analyze Jenkins/GitHub Actions history for flaky tests:
1. Calculate test reliability scores
2. Identify environmental vs code-related failures  
3. Generate test stabilization patches
4. Recommend test suite restructuring"
```

**Anti-pattern: Ignored Flakiness**
Accepting unreliable tests as normal instead of systematically identifying and fixing test suite stability issues.

---

### Test Promotion

**Maturity**: Intermediate
**Description**: Separate AI-generated tests from immutable golden tests to prevent AI from weakening test assertions, with human-approved promotion ensuring only validated tests become behavioral contracts.

**Related Patterns**: [Testing Orchestration](#testing-orchestration), [Spec-Driven Development](../README.md#spec-driven-development), [Suite Health](#suite-health)

**Core Problem**

When AI generates both code AND tests, it can make tests pass by weakening them—the "self-grading student" problem. This applies to all AI code generation: new features, bug fixes, refactoring, or any implementation task.

**Test Separation Architecture**

```
tests/
├── golden/          # Immutable (444 permissions) - AI blocked
│   ├── auth/
│   │   └── test_jwt_validation.py
│   └── api/
│       └── test_payment.py
└── generated/       # Mutable - AI can freely generate/modify
    ├── test_edge_cases.py
    └── test_new_feature.py
```

**Defense-in-Depth Enforcement**

The pattern uses multiple enforcement layers because **file permissions alone are insufficient** - AI with bash access could bypass them with `chmod`.

```bash
# Layer 1: File permissions (prevents accidental edits)
chmod 444 tests/golden/**/*.py
# ⚠️  NOT SUFFICIENT: AI can run "chmod 644" via Bash to bypass

# Layer 2: AI hooks (blocks Edit/Write tools)
# .ai/hooks/protect-golden.sh
[[ "$TOOL_INPUT_FILE_PATH" =~ ^tests/golden/ ]] && exit 2  # BLOCK
# ⚠️  NOT SUFFICIENT: AI can still modify via Bash commands

# Layer 3: CI/CD enforcement (detects ANY git diff)
git diff --name-only origin/main...HEAD | grep '^tests/golden/' && {
  echo "❌ BLOCKED: Golden tests cannot be modified"
  exit 1
}
# ✅ RELIABLE: Catches all modifications regardless of method

# Layer 4: CODEOWNERS (requires human approval)
# .github/CODEOWNERS
tests/golden/**  @tech-leads @qa-leads
# ✅ RELIABLE: Human gate prevents merge even if AI commits changes
```

**Threat Model:**
- **Accidental Edit**: Blocked by file permissions (444)
- **AI Edit/Write Tool**: Blocked by AI hooks
- **AI Bash Bypass**: Detected by CI/CD git diff check
- **Committed Changes**: Blocked by CODEOWNERS requiring human approval

**Primary Enforcement**: CI/CD + CODEOWNERS, not file permissions.

**Promotion Workflow**

```bash
# AI generates test freely in tests/generated/
ai "Write payment idempotency test in tests/generated/test_payment.py"

# Human reviews and promotes
./scripts/promote-test.sh tests/generated/test_payment.py
# → Runs pytest validation
# → Interactive quality checklist
# → Copies to tests/golden/ with 444 permissions
# → Creates promotion PR requiring 2+ approvals
```

**Example: Golden Test Protection**

```python
# AI generates test freely
# tests/generated/test_new_feature.py
def test_payment_idempotency():
    """Payment processing should prevent duplicate charges."""
    process_payment(id="123", amount=100)
    with pytest.raises(DuplicateTransactionError):
        process_payment(id="123", amount=100)

# Human reviews → promotes to golden
# tests/golden/test_payment.py (444 perms, AI blocked)
```

**Complete Implementation**

See [examples/test-promotion/](examples/test-promotion/) for:
- Complete promotion workflow scripts
- CI/CD enforcement configuration
- AI protection hooks
- Example application demonstrating the pattern

**Anti-pattern: Mutable Baselines**

Allowing AI to modify existing tests to make its code pass, removing critical assertions.

```python
# BEFORE (correct test):
def test_payment_idempotency():
    process_payment(id="123", amount=100)
    with pytest.raises(DuplicateTransactionError):
        process_payment(id="123", amount=100)

# AFTER AI weakens test to pass buggy code:
def test_payment_idempotency():
    process_payment(id="123", amount=100)
    process_payment(id="123", amount=100)  # No error check!
    # BUG: Allows double-charging customers in production
```

Without immutable golden tests, AI can weaken assertions to make failing tests pass, eliminating regression protection.

**Anti-pattern: Permission-Only Protection**

Relying solely on file permissions (444) without CI/CD enforcement.

```bash
# INSUFFICIENT: AI can bypass via Bash
chmod 444 tests/golden/**  # AI runs: chmod 644 && edit && chmod 444

# REQUIRED: CI/CD + CODEOWNERS as primary enforcement
git diff tests/golden/ → CI blocks merge
tests/golden/** → CODEOWNERS requires human approval
```

File permissions provide defense-in-depth but are not sufficient alone. CI/CD git diff detection and CODEOWNERS are the primary enforcement mechanisms.

---

### Upgrade Advisor

**Maturity**: Intermediate  
**Description**: Intelligently manage dependency upgrades with compatibility analysis and risk assessment.

**Related Patterns**: [Debt Forecasting](#debt-forecasting)

```bash
ai "Analyze package.json/requirements.txt for upgrade opportunities:
1. Check security vulnerabilities (npm audit, safety)
2. Assess breaking change risk
3. Generate staged upgrade plan
4. Create rollback procedures"
```

**Anti-pattern: Reckless Upgrades**
Upgrading all dependencies simultaneously without risk assessment or staged rollout plans.

---

### Handoff Automation

**Maturity**: Intermediate  
**Description**: Generate comprehensive handoff briefs that summarize system state and active issues.

**Related Patterns**: [Incident Automation](#incident-automation)

```bash
ai "Generate on-call handoff brief from last 24h:
1. Active alerts and their context
2. Recent deployments and their status
3. Known issues and workarounds
4. Escalation contacts and procedures
Include trending metrics and anomaly detection."
```

**Anti-pattern: Undocumented Handoffs**
Relying on informal verbal communication for critical system state transfer instead of structured, documented handoff procedures.

---

### Chaos Engineering

**Maturity**: Advanced  
**Description**: Generate targeted chaos experiments based on system architecture and dependencies.

**Related Patterns**: [Baseline Management](../README.md#baseline-management)

```bash
ai "Design chaos experiments for microservices architecture:
1. Service dependency mapping
2. Failure mode identification (network, CPU, memory)
3. Blast radius calculation
4. Recovery validation scenarios
Generate Chaos Monkey/Litmus configurations."
```

**Anti-pattern: Random Chaos**
Running unfocused chaos experiments without clear hypotheses or measurement criteria instead of systematic resilience testing.

---

### ChatOps Security

**Maturity**: Beginner  
**Description**: Deploy security scanning capabilities through chat commands for immediate feedback.

**Related Patterns**: [Security Orchestration](../README.md#security-orchestration)

```bash
# Slack bot integration for security scanning
ai "Create Slack command handlers for:
/security-scan [repo] - Run full security audit
/vulnerability-check [package] - Check specific dependency
/compliance-status [environment] - Check policy compliance
Include results formatting and alert escalation."
```

**Anti-pattern: Delayed Security**
Waiting for scheduled security scans instead of enabling on-demand security validation through developer workflows.

---

### Evidence Automation

**Maturity**: Advanced  
**Description**: Generate audit evidence matrices from logs and configuration changes automatically.

**Related Patterns**: [Security Orchestration](../README.md#security-orchestration)

```bash
ai "Generate SOC 2 compliance evidence from AWS CloudTrail:
1. Access control changes (IAM policy modifications)
2. Data encryption validation (S3 bucket policies)
3. Network security controls (Security Group changes)
4. Monitoring coverage (CloudWatch alarm configurations)
Format as audit-ready evidence matrix with timestamps and responsible parties."
```

**Anti-pattern: Manual Evidence**
Manually gathering compliance evidence during audits instead of continuously collecting and organizing audit trail data.
