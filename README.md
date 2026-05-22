# AI Development Patterns

[![Tests](https://github.com/PaulDuvall/ai-development-patterns/actions/workflows/pattern-validation.yml/badge.svg)](https://github.com/PaulDuvall/ai-development-patterns/actions/workflows/pattern-validation.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](https://github.com/PaulDuvall/ai-development-patterns#ai-development-patterns)
[![Patterns](https://img.shields.io/badge/patterns-24-blue.svg)](#complete-pattern-reference)
[![Quality Gate](https://img.shields.io/badge/quality%20gate-passing-brightgreen.svg)](https://github.com/PaulDuvall/ai-development-patterns/tree/main/tests)
[![Hyperlinks](https://img.shields.io/badge/hyperlinks-validated-brightgreen.svg)](https://github.com/PaulDuvall/ai-development-patterns/actions/workflows/pattern-validation.yml)

> **📋 How ready is your team for AI-assisted development?** Take the free [AI Development Readiness Scorecard](https://redactedventures.com/scorecard) to find out — and discover which patterns to adopt first.

A comprehensive collection of patterns based on my experience for building software with AI assistance, organized by implementation maturity and development lifecycle phases. These patterns are subject to change as the field evolves.

```mermaid
graph TB
    %% ROW 1: Foundation start (left to right)
    RA([Readiness<br/>Assessment]) --> CR([Codified<br/>Rules])
    CR --> SS([Security<br/>Sandbox])
    SS --> DL([Developer<br/>Lifecycle])
    DL --> TI([Tool<br/>Integration])

    %% ROW 2: Operations & branches (loops back)
    SS --> SO([Security<br/>Orchestration])
    SS --> PG([Policy<br/>Generation])
    SO --> CZR([Centralized<br/>Rules])

    %% ROW 3: Development patterns (flows forward again)
    DL --> OD([Observable<br/>Development])
    DL --> SD([Spec-Driven<br/>Development])
    CR --> GR([Guided<br/>Refactoring])
    CR --> CP([Context<br/>Persistence])
    RA --> IG([Issue<br/>Generation])
    CR --> EA([Event<br/>Automation])
    SS --> EA
    EA --> CC([Custom<br/>Commands])
    SD --> CC
    CP --> PD([Progressive<br/>Disclosure])
    CR --> PD
    SD --> IS([Image<br/>Spec])
    PD --> CZR

    %% ROW 4: Development chain
    PE([Progressive<br/>Enhancement]) --> AD([Atomic<br/>Decomposition])
    AD --> PA([Parallel<br/>Agents])
    PE --> IS

    %% ROW 5: Additional development patterns
    PE --> CMV([Cross-Model<br/>Validation])
    DL --> ER([Error<br/>Resolution])
    OD --> ER
    TI --> ER
    EA --> AR([Autonomous<br/>Remediation])
    CR --> AR
    GR --> AR
    ER --> AR
    PI([Planned<br/>Implementation])

    %% STYLING
    classDef foundation fill:#a8d5ba,stroke:#2d5a3f,stroke-width:2px,color:#1a3a25
    classDef development fill:#f9e79f,stroke:#b7950b,stroke-width:2px,color:#7d6608
    classDef operations fill:#f5b7b1,stroke:#c0392b,stroke-width:2px,color:#78281f

    class RA,CR,SS,DL,TI,IG foundation
    class PE,SD,AD,PA,OD,GR,EA,CC,PD,IS,CP,CMV,ER,PI,AR development
    class PG,SO,CZR operations

    %% CLICKABLE LINKS
    click RA "https://github.com/PaulDuvall/ai-development-patterns#readiness-assessment"
    click CR "https://github.com/PaulDuvall/ai-development-patterns#codified-rules"
    click SS "https://github.com/PaulDuvall/ai-development-patterns#security-sandbox"
    click DL "https://github.com/PaulDuvall/ai-development-patterns#developer-lifecycle"
    click TI "https://github.com/PaulDuvall/ai-development-patterns#tool-integration"
    click IG "https://github.com/PaulDuvall/ai-development-patterns#issue-generation"
    click CP "https://github.com/PaulDuvall/ai-development-patterns#context-persistence"
    click PE "https://github.com/PaulDuvall/ai-development-patterns#progressive-enhancement"
    click SD "https://github.com/PaulDuvall/ai-development-patterns#spec-driven-development"
    click AD "https://github.com/PaulDuvall/ai-development-patterns#atomic-decomposition"
    click PA "https://github.com/PaulDuvall/ai-development-patterns#parallel-agents"
    click OD "https://github.com/PaulDuvall/ai-development-patterns#observable-development"
    click GR "https://github.com/PaulDuvall/ai-development-patterns#guided-refactoring"
    click EA "https://github.com/PaulDuvall/ai-development-patterns#event-automation"
    click CC "https://github.com/PaulDuvall/ai-development-patterns#custom-commands"
    click PD "https://github.com/PaulDuvall/ai-development-patterns#progressive-disclosure"
    click IS "https://github.com/PaulDuvall/ai-development-patterns#image-spec"
    click PG "https://github.com/PaulDuvall/ai-development-patterns#policy-generation"
    click SO "https://github.com/PaulDuvall/ai-development-patterns#security-orchestration"
    click CZR "https://github.com/PaulDuvall/ai-development-patterns#centralized-rules"
    click PI "https://github.com/PaulDuvall/ai-development-patterns#planned-implementation"
    click CMV "https://github.com/PaulDuvall/ai-development-patterns#cross-model-validation"
    click ER "https://github.com/PaulDuvall/ai-development-patterns#error-resolution"
    click AR "https://github.com/PaulDuvall/ai-development-patterns#autonomous-remediation"
```

**Legend**: 🟢 Foundation | 🟡 Development | 🔴 Operations

## Pattern Organization

This repository provides a structured approach to AI-assisted development through three pattern categories:

- **[Foundation Patterns](#foundation-patterns)** - Essential patterns for team readiness and basic AI integration
- **[Development Patterns](#development-patterns)** - Daily practice patterns for AI-assisted coding workflows  
- **[Operations Patterns](#operations-patterns)** - CI/CD, security, and production management with AI
- **[Experimental Patterns](experiments/)** - Advanced and experimental patterns under active development and/or consideration.

## Pattern Dependencies & Implementation Order

**Important**: These phases represent a **learning progression** for teams new to AI development, not a waterfall approach. Teams with existing DevOps/security expertise should implement patterns continuously across all phases from day one, following a "continuous everything" model.

```mermaid
graph TD
    subgraph "Phase 1: Foundation (Weeks 1-2)"
        A[Readiness Assessment] --> B[Codified Rules]
        B --> C[Security Sandbox]
        C --> D[Developer Lifecycle]
        A --> E[Issue Generation]
        D --> F[Tool Integration]
    end

    subgraph "Phase 2: Development (Weeks 3-4)"
        D --> G[Spec-Driven Development]
        H[Planned Implementation]
        I[Progressive Enhancement]
        I --> J[Cross-Model Validation]
        Q[Event Automation]
        R[Custom Commands]
        S[Progressive Disclosure]
        U[Image Spec]
        V[Autonomous Remediation]
        I --> K[Atomic Decomposition]
        K --> L[Parallel Agents]
    end

    subgraph "Phase 3: Operations (Weeks 5-6)"
        C --> M[Policy Generation]
        M --> N[Security Orchestration]
        N --> T[Centralized Rules]
    end

    B --> Q
    C --> Q
    Q --> R
    G --> R
    B --> S
    R --> S
    B --> T
    S --> T
    G --> U
    I --> U
    Q --> V
    B --> V
```

**Continuous Implementation Note**: Security patterns ([Security Sandbox](#security-sandbox), AI Security & Compliance) and deployment patterns should be implemented continuously throughout development, not delayed until specific phases. The dependencies shown represent learning prerequisites, not deployment gates.

## Complete Pattern Reference

| Pattern | Maturity | Type | Description | Dependencies |
|---------|----------|------|-------------|--------------|
| **[Readiness Assessment](#readiness-assessment)** | Beginner | Foundation | Systematic evaluation of codebase and team readiness for AI integration | None |
| **[Codified Rules](#codified-rules)** | Beginner | Foundation | Version and maintain AI coding standards as explicit configuration files | Readiness Assessment |
| **[Security Sandbox](#security-sandbox)** | Beginner | Foundation | Run AI tools in isolated environments without access to secrets or sensitive data | Codified Rules |
| **[Developer Lifecycle](#developer-lifecycle)** | Intermediate | Workflow | Structured 9-stage process from problem definition through deployment with AI assistance | Codified Rules, Security Sandbox |
| **[Tool Integration](#tool-integration)** | Intermediate | Foundation | Connect AI systems to external data sources, APIs, and tools for enhanced capabilities beyond prompt-only interactions | Security Sandbox, Developer Lifecycle |
| **[Issue Generation](#issue-generation)** | Intermediate | Foundation | Generate Kanban-optimized work items (4-8 hours max) from requirements using AI to ensure continuous flow with clear acceptance criteria and dependencies | Readiness Assessment |
| **[Spec-Driven Development](#spec-driven-development)** | Intermediate | Development | Use executable specifications to guide AI code generation with clear acceptance criteria before implementation | Developer Lifecycle |
| **[Image Spec](#image-spec)** | Intermediate | Development | Upload images (diagrams, mockups, flows) as primary specifications for AI coding tools to build accurate implementations from visual context | Spec-Driven Development, Progressive Enhancement |
| **[Planned Implementation](#planned-implementation)** | Beginner | Development | Interview, constrain, and plan before writing code so AI implementation matches actual requirements instead of confident-sounding assumptions | None |
| **[Progressive Enhancement](#progressive-enhancement)** | Beginner | Development | Build complex features through small, deployable iterations rather than big-bang generation | None |
| **[Cross-Model Validation](#cross-model-validation)** | Intermediate | Development | Run the same task across multiple frontier models and use their agreements, disagreements, and divergences as eval signal for high-stakes decisions | Progressive Enhancement |
| **[Atomic Decomposition](#atomic-decomposition)** | Intermediate | Development | Break complex features into atomic, independently implementable tasks for parallel AI agent execution | Progressive Enhancement |
| **[Parallel Agents](#parallel-agents)** | Advanced | Development | Run multiple AI agents concurrently on isolated tasks or environments to maximize development speed and exploration | Atomic Decomposition |
| **[Context Persistence](#context-persistence)** | Intermediate | Development | Manage AI context as a finite resource through structured memory schemas, prompt pattern capture, and session continuity protocols | Codified Rules |
| **[Event Automation](#event-automation)** | Intermediate | Development | Execute custom commands automatically at assistant lifecycle events to enforce policies and automate workflows | Codified Rules, Security Sandbox |
| **[Custom Commands](#custom-commands)** | Intermediate | Development | Discover and use built-in command vocabularies, then extend them with custom commands that encode domain expertise and sophisticated workflows | Event Automation, Spec-Driven Development, Codified Rules |
| **[Progressive Disclosure](#progressive-disclosure)** | Intermediate | Development | Load AI assistant rules incrementally based on task context to prevent instruction saturation and context bloat | Codified Rules, Context Persistence |
| **[Observable Development](#observable-development)** | Intermediate | Development | Strategic logging and debugging that makes system behavior visible to AI | Developer Lifecycle |
| **[Guided Refactoring](#guided-refactoring)** | Intermediate | Development | Systematic code improvement using AI to detect and resolve code smells with measurable quality metrics | Codified Rules |
| **[Error Resolution](#error-resolution)** | Intermediate | Development | Automatically collect error context from logs, system state, and git history, then use AI to diagnose root causes and generate validated fixes | Developer Lifecycle, Observable Development, Tool Integration |
| **[Autonomous Remediation](#autonomous-remediation)** | Intermediate | Development | Pair deterministic rule-based detectors with LLM remediators inside an event-driven loop so codified rule violations are caught and fixed automatically before the AI session continues | Codified Rules, Event Automation |
| **Security & Compliance** | | Operations | *Category containing security and compliance patterns* | |
| **[Policy Generation](#policy-generation)** | Advanced | Operations | Transform compliance requirements into executable Cedar/OPA policy files with AI assistance | Security Sandbox |
| **[Security Orchestration](#security-orchestration)** | Intermediate | Workflow | Aggregate multiple security tools and use AI to summarize findings for actionable insights | Security Sandbox |
| **[Centralized Rules](#centralized-rules)** | Advanced | Operations | Enforce organization-wide AI rules through a central Git repository that syncs to standard AI assistant configuration files with automatic language and framework detection | Codified Rules, Progressive Disclosure, Security Orchestration |
| **Deployment Automation** | | Operations | *Category containing deployment and pipeline patterns* | |

---

## Pattern Maturity Levels

Patterns are classified by implementation complexity and prerequisite knowledge:

**Beginner**: Basic AI tool usage with minimal setup required
- Prerequisites: Basic programming skills, access to AI tools
- Complexity: Single tool usage, straightforward prompts
- Examples: Simple code generation, basic constraint setting

**Intermediate**: Multi-tool coordination and process integration  
- Prerequisites: Development workflow experience, team coordination
- Complexity: Multiple tools, orchestration patterns, quality gates
- Examples: Testing strategies, parallel workflows, choice generation

**Advanced**: Complex systems with enterprise concerns
- Prerequisites: Architecture experience, security/compliance knowledge  
- Complexity: Multi-agent systems, advanced safety, compliance automation
- Examples: Enterprise security, compliance automation, chaos engineering

## Task Sizing Framework

The patterns use different task sizing approaches based on their purpose and context:

```mermaid
graph TD
    A[Feature Request] --> B[Issue Generation]
    B --> C[4-8 Hour Work Items]
    C --> D{Parallel Implementation?}
    D -->|Yes| E[Atomic Decomposition]
    D -->|No| F[Progressive Enhancement]
    E --> G[1-2 Hour Atomic Tasks]
    F --> H[Daily Deployment Cycles]

    G --> I[Parallel Agent Execution]
    H --> J[Sequential Enhancement]
    C --> K[Standard Kanban Flow]
```

**Task Sizing Hierarchy**:

- **[Issue Generation](#issue-generation)** (4-8 hours): Standard Kanban work items for continuous flow and rapid feedback
- **[Atomic Decomposition](#atomic-decomposition)** (1-2 hours): Ultra-small tasks for parallel agent execution without conflicts
- **[Progressive Enhancement](#progressive-enhancement)** (Daily cycles): Deployment-focused iterations that may contain multiple work items

**When to Use Each Approach**:
- Use **[Issue Generation](#issue-generation)** for standard team development with human developers
- Use **[Atomic Decomposition](#atomic-decomposition)** when implementing with parallel AI agents
- Use **[Progressive Enhancement](#progressive-enhancement)** when prioritizing rapid market feedback over task granularity

**Pattern Differentiation**:
- **[Issue Generation](#issue-generation)**: Creates Kanban work items (4-8 hours) for human team workflows
- **[Atomic Decomposition](#atomic-decomposition)**: Creates ultra-small tasks (1-2 hours) for parallel AI agents
- **[Progressive Enhancement](#progressive-enhancement)**: Creates deployment cycles (daily) focused on user feedback

## Pattern Selection Decision Framework

Choose the right patterns based on your team's context, project requirements, and AI development maturity:

### Decision Tree

```mermaid
graph TD
    A[Starting AI Development] --> B{Team AI Experience?}
    B -->|New to AI| C[Start with Foundation Patterns]
    B -->|Some Experience| D[Focus on Development Patterns]
    B -->|Advanced| E[Implement Operations Patterns]

    C --> F[Readiness Assessment]
    F --> G[Codified Rules]
    G --> H[Security Sandbox]
    H --> I{Need Structured Development?}
    I -->|Yes| J[Developer Lifecycle]
    I -->|No| K[Planned Implementation]
    K --> L[Progressive Enhancement]

    D --> M{Multiple Developers/Agents?}
    M -->|Yes| N[Parallel Agents]
    M -->|No| O[Spec-Driven Development]
    N --> P[Atomic Decomposition]

    E --> R{Enterprise Requirements?}
    R -->|Compliance| S[Policy Generation]
    R -->|Scale| T[Centralized Rules]
    R -->|Quality| U[Debt Forecasting]
```

### Context-Based Pattern Selection

**For New Teams (First 2 weeks)**:
1. **[Readiness Assessment](#readiness-assessment)** - Evaluate current state
2. **[Codified Rules](#codified-rules)** - Establish consistent standards
3. **[Security Sandbox](#security-sandbox)** - Ensure safe experimentation
4. **[Planned Implementation](#planned-implementation)** - Learn structured planning approaches
5. **[Progressive Enhancement](#progressive-enhancement)** - Start with simple iterations

**For Development Teams (Weeks 3-8)**:
1. **[Developer Lifecycle](#developer-lifecycle)** - Structured development process
2. **[Spec-Driven Development](#spec-driven-development)** - Quality-focused development
3. **[Issue Generation](#issue-generation)** - Organized work breakdown
4. **[Testing Orchestration](experiments/README.md#testing-orchestration)** - Quality assurance

**For Parallel Implementation**:
1. **[Atomic Decomposition](#atomic-decomposition)** - Ultra-small independent tasks
2. **[Workflow Orchestration](experiments/README.md#workflow-orchestration)** - Agent coordination
3. **[Review Automation](experiments/README.md#review-automation)** - Automated integration
4. **[Security Sandbox](#security-sandbox)** - Enhanced with parallel safety

**For Enterprise/Production (Month 2+)**:
1. **[Policy Generation](#policy-generation)** - Compliance automation
2. **[Security Orchestration](#security-orchestration)** - Integrated security
3. **[Centralized Rules](#centralized-rules)** - Organization-wide AI standards
4. **[Debt Forecasting](experiments/README.md#debt-forecasting)** - Proactive maintenance

### Project Type Recommendations

**MVP/Startup Projects**:
- **Primary**: [Progressive Enhancement](#progressive-enhancement), [Planned Implementation](#planned-implementation)
- **Secondary**: [Security Sandbox](#security-sandbox), [Cross-Model Validation](#cross-model-validation)
- **Avoid**: Complex orchestration patterns until scale demands

**Enterprise Applications**:
- **Primary**: [Developer Lifecycle](#developer-lifecycle), [Policy Generation](#policy-generation)
- **Secondary**: [Spec-Driven Development](#spec-driven-development), [Security Orchestration](#security-orchestration)
- **Essential**: All foundation patterns before development patterns

**Research/Experimental Projects**:
- **Primary**: [Cross-Model Validation](#cross-model-validation), [Observable Development](#observable-development)
- **Secondary**: [Context Persistence](#context-persistence), [Context Optimization](experiments/README.md#context-optimization)
- **Focus**: Learning and exploration over production readiness

**High-Scale Production**:
- **Primary**: [Parallel Agents](#parallel-agents), [Observable Development](#observable-development)
- **Secondary**: Chaos Engineering, Incident Automation
- **Critical**: All security and monitoring patterns

### Team Size Considerations

**Solo Teams**:
- Focus on **[Progressive Enhancement](#progressive-enhancement)** and **[Cross-Model Validation](#cross-model-validation)**
- Add **[Observable Development](#observable-development)** for debugging
- Skip parallel orchestration patterns

**Two-Pizza Teams** (small, autonomous teams):
- Implement **[Issue Generation](#issue-generation)** for coordination
- Use **[Spec-Driven Development](#spec-driven-development)** for quality
- Consider **[Tool Integration](#tool-integration)** for role clarity
- Full **[Developer Lifecycle](#developer-lifecycle)** implementation
- **[Parallel Agents](#parallel-agents)** for complex features
- **[Spec-Driven Development](#spec-driven-development)** for quality gates and traceability

**Multi Two-Pizza Team Organizations**:
- **[Atomic Decomposition](#atomic-decomposition)** for parallel work across teams
- **[Spec-Driven Development](#spec-driven-development)** for coordination at scale via shared specifications
- All **Operations Patterns** for organizational management

### Technology Stack Considerations

**Cloud-Native Applications**:
- Emphasize **[Policy Generation](#policy-generation)** and **Evidence Automation**
- Implement **Drift Remediation** for infrastructure
- Use **Deployment Synthesis** for safe releases

**On-Premise Systems**:
- Focus on **[Security Sandbox](#security-sandbox)** with network isolation
- Implement **[Context Persistence](#context-persistence)** for institutional knowledge
- Use **Debt Forecasting** for maintenance planning

**Microservices Architecture**:
- **[Parallel Agents](#parallel-agents)** for service coordination
- **[Observable Development](#observable-development)** across service boundaries
- **[Autonomous Remediation](#autonomous-remediation)** for cross-service code-quality consistency

**Monolithic Applications**:
- **[Progressive Enhancement](#progressive-enhancement)** for gradual modernization
- **[Guided Refactoring](#guided-refactoring)** for code quality improvement
- **[Planned Implementation](#planned-implementation)** to prevent over-engineering through its constraint phase

---

# Foundation Patterns

Foundation patterns establish the essential infrastructure and team readiness required for successful AI-assisted development. These patterns must be implemented first as they enable all subsequent patterns.

## Readiness Assessment

**Maturity**: Beginner
**Description**: Systematic evaluation of codebase and team readiness for AI-assisted development before implementing AI patterns.

**Related Patterns**: [Codified Rules](#codified-rules), [Issue Generation](#issue-generation)

> 📋 **Quick start**: Use the free [AI Development Readiness Scorecard](https://www.redactedventures.com/scorecard) to score your team against this framework in about 10 minutes and get a tailored pattern adoption sequence.

**Assessment Framework**

```mermaid
graph TD
    A[Codebase Assessment] --> B[Team Assessment]
    B --> C[Infrastructure Assessment]
    C --> D[Readiness Score]
    D --> E[Implementation Plan]
```

**Codebase Readiness Checklist**
```markdown
## Code Quality Prerequisites
□ Consistent code formatting and style guide
□ Comprehensive test coverage (>80% for critical paths)
□ Clear separation of concerns and modular architecture
□ Documented APIs and interfaces
□ Version-controlled configuration and secrets management

## Documentation Standards
□ README with setup and development instructions
□ API documentation (OpenAPI/Swagger)
□ Architecture decision records (ADRs)
□ Coding standards and conventions documented
□ Deployment and operational procedures
```

**Anti-pattern: Premature Adoption**
Starting AI adoption without proper assessment leads to inconsistent practices, security vulnerabilities, and team frustration.

---

## Codified Rules

**Maturity**: Beginner
**Description**: Version and maintain AI coding standards as explicit configuration files that persist across sessions and team members.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Context Persistence](#context-persistence), [Progressive Disclosure](#progressive-disclosure), [Event Automation](#event-automation), [Custom Commands](#custom-commands), [Centralized Rules](#centralized-rules)

**Standardized Project Structure**
```bash
project/
├── .ai/                          # AI configuration directory
│   ├── rules/                    # Modular rule sets
│   │   ├── security.md          # Security standards
│   │   ├── testing.md           # Testing requirements
│   │   ├── style.md             # Code style guide
│   │   └── architecture.md      # Architectural patterns
│   ├── prompts/                 # Reusable prompt templates
│   │   ├── implementation.md    # Implementation prompts
│   │   ├── review.md            # Code review prompts
│   │   └── testing.md           # Test generation prompts
│   └── knowledge/               # Captured patterns and gotchas
│       ├── successful.md        # Proven successful patterns
│       └── failures.md          # Known failure patterns
├── .cursorrules                 # Cursor IDE configuration
├── CLAUDE.md                    # Claude Code session context
└── .windsurf/                   # Windsurf configuration
    └── rules.md
```

**Complete Example**: See [examples/codified-rules/](examples/codified-rules/) for:
- Comprehensive development workflow rules and standards
- Pipeline automation and CI/CD rules
- Code quality standards and enforcement guidelines
- Claude Code configuration for rules-as-code implementation

**Anti-pattern: Broken Context**
Each developer maintains their own prompts and preferences, leading to inconsistent code across the team.

---

## Security Sandbox

**Maturity**: Beginner
**Description**: Run AI tools in isolated environments without access to secrets or sensitive data to prevent credential leaks and maintain security compliance.

**Related Patterns**: [Security & Compliance Patterns](#security--compliance-patterns), [Codified Rules](#codified-rules), [Event Automation](#event-automation)

**Core Security Implementation**

**Claude Code Users**: Use the `/sandbox` command to instantly create isolated environments without manual Docker configuration:
```bash
/sandbox
# Creates a secure, isolated environment with:
# - No access to credentials or sensitive files
# - Restricted network access
# - Controlled file system permissions
```

**Docker-Based Implementation**: For custom isolation or multi-agent scenarios:
```yaml
# Basic AI isolation with complete network isolation
services:
  ai-development:
    network_mode: none                    # Zero network access
    cap_drop: [ALL]                       # No system privileges
    volumes:
      - ./src:/workspace/src:ro           # Read-only source code
      # DO NOT mount ~/.aws, .env, secrets/, etc.
```

**Complete Example**: See [examples/security-sandbox/](examples/security-sandbox/) for:
- Complete Docker isolation configurations for single and multi-agent setups
- Resource locking and emergency shutdown procedures
- Security monitoring and violation detection
- Multi-agent coordination with conflict resolution

**Production Implementations**

Modern AI development platforms provide enterprise-grade implementations of these security controls:

**Cloud-Based Sandboxes**:
- **[Claude Code for the web](https://www.claude.ai/code)**: Sandboxed AI coding with isolated execution environments
- **[Google Jules](https://jules.google/)**: Google's AI coding assistant with secure development environments
- **[OpenAI Codex](https://chatgpt.com/codex)**: Cloud-based AI coding with secure execution environments
- **[Google Vertex AI Agent Engine Code Execution](https://cloud.google.com/vertex-ai/agent-builder/docs/code-execution)**: Managed secure runtimes for AI agent code execution
- **[GitHub Codespaces](https://docs.github.com/en/codespaces/overview)**: Isolated cloud development VMs with configurable security policies
- **[E2B](https://e2b.dev)**: Specialized AI agent sandboxes with microVM isolation

**Cloud & Self-Hosted Options**:
- **[Daytona](https://www.daytona.io)**: microVM-based isolation for development environments (available as cloud service or self-hosted)
- **[Coder](https://coder.com)**: Cloud development environments with enterprise security controls (available as cloud service or self-hosted)

**Anti-pattern: Unrestricted Access**
Allowing AI tools full system access risks credential leaks, data breaches, and security compliance violations.

**Anti-pattern: Conflicting Workspaces**
Allowing multiple parallel agents to write to the same directories creates race conditions, file conflicts, and unpredictable behavior that can corrupt the development environment.

---

## Developer Lifecycle

**Maturity**: Intermediate
**Description**: Structured 9-stage process from problem definition through deployment with AI assistance.

**Related Patterns**: [Codified Rules](#codified-rules), [Spec-Driven Development](#spec-driven-development), [Planned Implementation](#planned-implementation), [Atomic Decomposition](#atomic-decomposition), [Observable Development](#observable-development)

**Workflow Interaction Sequence**

```mermaid
sequenceDiagram
    participant D as Developer
    participant AI as AI Assistant
    participant S as System/CI
    participant T as Tests
    participant M as Monitoring
    
    Note over D,M: Stage 1-3: Problem → Plan → Requirements
    D->>AI: Problem Definition (e.g., JWT Authentication)
    AI->>D: Technical Architecture Plan
    D->>AI: Requirements Clarification
    AI->>D: API Specs + Kanban Tasks + Security Requirements
    
    Note over D,M: Stage 4-5: Issues → Specifications
    D->>AI: Generate Executable Tests
    AI->>T: Gherkin Scenarios + API Tests + Security Tests
    T->>D: Test Suite Ready (Performance Criteria: <200ms)
    
    Note over D,M: Stage 6: Implementation
    D->>AI: Implement Following Specifications
    AI->>S: Code + Tests + Error Handling + Logging
    S->>D: Implementation Results
    
    Note over D,M: Stage 7-9: Testing → Deployment → Monitoring
    D->>S: Run All Tests
    S->>D: Test Results + Security Scan + Performance Benchmark
    alt Tests Pass
        S->>S: Deploy to Production
        S->>M: Setup Monitoring Alerts
        M->>D: Deployment Complete + Monitoring Active
    else Tests Fail
        S->>D: Failure Report
        D->>AI: Fix Issues
        AI->>S: Updated Implementation
    end
    
    Note over D,M: Continuous Monitoring
    M->>D: Performance Alerts + Security Events
```

**Core Workflow Implementation**

```bash
# Stage 1-3: Problem → Plan → Requirements
ai "Analyze request → Generate architecture, tasks, API specs"

# Stage 4-5: Issues → Specifications  
ai "Generate executable tests → Gherkin scenarios, API tests, security tests"

# Stage 6: Implementation
ai "Implement following specifications → Use tests as guide, security best practices"

# Stage 7-9: Testing → Deployment → Monitoring  
ai "Complete QA → Run tests, security scan, deploy, monitor"
```

**Complete Implementation**: See [examples/developer-lifecycle/](examples/developer-lifecycle/) for full 9-stage workflow scripts, detailed prompts for each stage, enhanced implementation techniques ([Five-Try Rule](https://www.linkedin.com/posts/jessicakerr_the-implementation-is-a-test-of-the-design-activity-7367649800193761281-LzCu/), markdown iteration, function decomposition), and integration with CI/CD pipelines.

**Anti-pattern: Unplanned Development**
Jumping straight to coding with AI without proper planning, requirements, or testing strategy. Also avoid continuing with the same AI approach after 3-4 failures without decomposing the problem or changing strategy.

---

## Tool Integration

**Maturity**: Intermediate  
**Description**: Connect AI systems to external data sources, APIs, and tools for enhanced capabilities beyond prompt-only interactions.

**Related Patterns**: [Security Sandbox](#security-sandbox), [Developer Lifecycle](#developer-lifecycle), [Observable Development](#observable-development)

**Core Concept**

Modern AI development requires more than chat-based interactions. AI systems become significantly more capable when connected to real-world data sources and tools. This pattern demonstrates the architectural shift from isolated prompt-only AI to tool-augmented AI systems.

**Implementation Overview**

```python
# Core tool-augmented AI system with security controls
class ToolAugmentedAI:
    def __init__(self, config_path: str = ".ai/tools.json"):
        self.available_tools = {
            "database_query": self._query_database,     # Read-only SQL queries
            "file_operations": self._file_operations,   # Controlled file access
            "api_requests": self._api_requests,         # Allowlisted HTTP requests
            "system_info": self._system_info            # Safe system information
        }
    
    def execute_with_tools(self, ai_request: str, tool_calls: list) -> dict:
        """Execute AI request with secure tool access"""
        # Process tool calls with security validation
        # Return structured results with error handling
```

**Tool Categories & Security**

- **Database Access**: Read-only queries with operation whitelisting (`SELECT`, `WITH` only)
- **File Operations**: Path-restricted read/write within configured directories
- **API Integration**: HTTP requests limited to allowlisted domains with timeouts
- **System Information**: Safe environment data without sensitive details

**Configuration Example**
```json
{
  "allowed_apis": ["api.github.com", "api.openweathermap.org"],
  "file_access_paths": ["./data/", "./logs/", "./generated/"],
  "max_query_results": 100,
  "security": {
    "read_only_database": true,
    "api_rate_limits": true,
    "file_size_limits": "10MB"
  }
}
```

**Model Context Protocol (MCP) Integration**

This pattern can be implemented using [Anthropic's Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) for standardized tool integration across AI systems:

```json
{
  "mcp_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "./data"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-sqlite", "app_data.db"]
    }
  }
}
```

**What [Tool Integration](#tool-integration) Enables**

- **Real-time data access**: AI queries current database state, not training data
- **File system interaction**: Read logs, write generated code, manage project files
- **API integration**: Fetch live data from external services and APIs
- **System awareness**: Access to current environment state and configuration
- **Enhanced context**: AI decisions based on actual system state, not assumptions

**Complete Implementation**

See [examples/tool-integration/](examples/tool-integration/) for:
- Full Python implementation with security controls
- Configuration examples and MCP integration
- Usage patterns and deployment guidelines
- Integration with [Security Sandbox](#security-sandbox)

**Anti-pattern: Disconnected Prompting**
Attempting to solve complex data analysis, system integration, or real-time problems using only natural language prompts without providing AI access to actual data sources, APIs, or system tools. This leads to hallucinated responses, outdated information, and inability to interact with real systems.

---


## Issue Generation

**Maturity**: Intermediate
**Description**: Generate small, deployable work items (<1 hour with AI assistance) from requirements using AI to ensure continuous delivery with clear acceptance criteria and dependency tracking.

**Methodology Note**: This pattern aligns well with Kanban principles (continuous flow, small batches) but works with any development methodology including Scrum, Scrumban, or ad-hoc workflows.

**Related Patterns**: [Readiness Assessment](#readiness-assessment), [Spec-Driven Development](#spec-driven-development)

**[Issue Generation](#issue-generation) Framework**

```mermaid
graph TD
    A[Requirements Document] --> B[AI Feature Analysis]
    B --> C[Work Item Splitting]
    C --> D{<1 hour?}
    D -->|No| E[Split Further]
    E --> C
    D -->|Yes| F[Story Generation]
    F --> G[Acceptance Criteria]
    G --> H[Cycle Time Target]
    H --> I[Dependency Mapping]
    I --> J[Work Item Creation]
```

**Core Principles**

- **Small Batch Sizing**: Each work item sized for 4-8 hours max to enable continuous delivery and rapid feedback
- **AI-Assisted Decomposition**: Use AI to break down requirements into implementable tasks
- **Traceability Integration**: Connect issues to implementation files and CI workflows
- **Dependency Mapping**: Establish clear relationships between work items and epics
- **Acceptance-Driven**: Each task includes specific, testable acceptance criteria

**Work Item Attributes**

Generated issues must include:
- **Title**: Specific, actionable description of the work
- **Cycle Time Target**: Estimated completion time (<1 hour with AI assistance)
- **Acceptance Criteria**: Testable conditions for completion
- **File Scope**: Which files will be added, updated, or removed
- **CI Requirements**: Test coverage, pipeline steps, quality gates
- **Dependencies**: Blocking and enabling relationships with other issues

**Epic Relationship Management**

- **Bidirectional Linking**: Parent-child references maintained automatically
- **Progress Tracking**: Epic completion calculated from subissue status
- **Dependency Validation**: Automated checking for circular dependencies
- **Status Propagation**: Subissue changes update epic progress

**Implementation Examples**: See [examples/issue-generation/](examples/issue-generation/) for detailed AI prompts, epic breakdown workflows, CI integration patterns, and traceability implementations. For AI-first workflows, see [Beads guide](examples/issue-generation/beads-guide.md) - a git-native issue tracker with CLI access and persistent agent memory.

> "Small, frequent deliveries expose issues early and keep teams aligned."
> – Agile Alliance

**Kanban Context**: This pattern embodies Kanban principles of continuous flow and small batch sizes. If using Kanban: "If a task takes more than one day, split it." (Kanban Guide, Lean Kanban University). However, the pattern works equally well with Scrum sprints, continuous delivery, or any methodology that values incremental progress.

**Anti-pattern: Under-Specified Issues**
Creating generic tasks without specific acceptance criteria, proper sizing, or clear dependencies leads to scope creep and estimation errors.

**Anti-pattern: Broken Integration**
Creating issues without CI workflow integration, file tracking, or traceability requirements leads to disconnected development cycles and poor visibility into implementation progress.

**Anti-pattern Examples:**
```markdown
❌ "Fix the login page"
❌ "Make the dashboard better"
❌ "Add some tests"
❌ "AUTH-002: Implement password validation" (no file tracking or CI requirements)

✅ "Add OAuth 2.0 token validation endpoint (<1 hour with AI)"
✅ "Implement dashboard metric WebSocket connection (45 minutes)"
✅ "Write unit tests for user service login method (30 minutes)"
✅ "AUTH-002: Password validation service with CI integration"
   - Files: src/auth/validators.py, tests/test_validators.py
   - Coverage: 95%, unit + integration tests
   - CI: lint, test, security-scan must pass
   - AI-assisted: Use AI for implementation and test generation
```

---

# Development Patterns

Development patterns provide tactical approaches for day-to-day AI-assisted coding workflows, focusing on quality, maintainability, and team collaboration.

## Spec-Driven Development

**Maturity**: Intermediate
**Description**: Use executable specifications to guide AI code generation with clear acceptance criteria before implementation.

**Core Principle: Precision Enables Productivity**

SpecDriven AI combines three key elements:
- **Machine-readable specifications** with unique identifiers and authority levels
- **Rigorous Test-Driven Development** with coverage tracking and automated validation
- **AI-powered implementation** with persistent context through structured specifications

**Key Innovation: Authority Level System**

Specifications use authority levels to resolve conflicts and establish precedence:
- **`authority=system`**: Core business logic and security requirements (highest precedence)
- **`authority=platform`**: Infrastructure and technical architecture decisions  
- **`authority=feature`**: User interface and experience requirements (lowest precedence)

When requirements conflict, higher authority levels take precedence, enabling clear decision-making for AI implementation.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Tool Integration](#tool-integration), [Custom Commands](#custom-commands), [Image Spec](#image-spec), [Testing Orchestration](experiments/README.md#testing-orchestration), [Observable Development](#observable-development)

**SpecDriven AI Workflow**

```mermaid
graph TD
    A[Machine-Readable Specifications<br/>with Authority Levels] --> B[Coverage Tracking<br/>& Validation]
    B --> C[AI Implementation<br/>with Ephemeral Prompts]
    C --> D[Automated Testing<br/>& Compliance Check]
    D --> E{Specs Pass?}
    E -->|No| F[Refine Prompts<br/>Not Specs]
    F --> C
    E -->|Yes| G[Coverage Report<br/>& Deployment]
    G --> H[Specification Persistence<br/>for Regression]
    
    style A fill:#e1f5e1
    style B fill:#e1f5e1
    style H fill:#e1f5e1
    style C fill:#ffe6e6
    style F fill:#ffe6e6
```

**Core Implementation**

**Machine-Readable Specification with Authority Levels**
```markdown
# IAM Policy Generator Specification {#iam_policy_gen}

## CLI Requirements {#cli_requirements authority=system}
The system MUST provide a command-line interface that:
- Accepts policy type via `--policy-type` flag
- Validates input parameters against AWS IAM constraints
- Generates syntactically correct IAM policy JSON [^test_iam_syntax]
- Returns exit code 0 for success, 1 for validation errors

## Input Validation {#input_validation authority=platform}  
The system MUST:
- Reject invalid AWS service names with clear error messages
- Validate resource ARN format before policy generation
- Implement rate limiting for API calls [^test_rate_limit]

[^test_iam_syntax]: tests/test_iam_policy_syntax.py
[^test_rate_limit]: tests/test_rate_limiting.py
```

**Automated Coverage Tracking**
```bash
# Run specification compliance validation
pytest --cov=src --cov-report=html --spec-coverage
python spec_validator.py --check-coverage --authority-conflicts

# Output shows specification coverage
# Specification Coverage Report:
# ✅ cli_requirements: 100% (3/3 tests linked)
# ✅ input_validation: 85% (6/7 tests linked) 
# ⚠️  Missing test: [^test_malformed_arn] in line 23
```

**Tooling Integration**

```bash
# Pre-commit hook validates specification compliance
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: spec-coverage
        name: Specification Coverage Check
        entry: python spec_validator.py --check-coverage
        language: python
        pass_filenames: false

# Git workflow with specification traceability  
git commit -m "feat: implement rate limiting [spec:rl2c]
  
Implements rate limiting requirement from input_validation
section. Closes specification anchor #failed_auth.

Coverage: 94% (31/33 spec requirements covered)"
```

**Key Benefits**
- **Authority-based conflict resolution** prevents requirement ambiguity
- **Automated coverage tracking** ensures no specifications are missed
- **AI tool independence** through persistent, machine-readable requirements
- **Precise traceability** from specification anchors to test implementations
- **Living documentation** that evolves with the system

**Automated Traceability**

Specification anchors (`{#cli_requirements}`) and test footnotes (`[^test_iam_syntax]`) are the link layer that ties requirements to tests to code to docs. Maintain those links automatically on every change instead of in a spreadsheet:

```bash
# After each commit, validate anchor coverage and flag drift
git diff --name-only HEAD~1 | while read file; do
    ai "For $file: confirm referenced spec anchors still exist, propose new
        anchor links for any uncovered behavior, and emit an impact list of
        which downstream tests and docs need updating."
done
```

When a spec section moves or a test is renamed, the same loop surfaces the broken link before it ships. The result is a living traceability graph that stays accurate without manual upkeep — the alternative (traceability in a spreadsheet) is stale within a week.

**Anti-pattern: Broken Traceability**
Maintaining requirement-to-test links in spreadsheets or manual documentation that becomes stale and inaccurate within days of being written.

**Complete Implementation**

See [examples/spec-driven-development/](examples/spec-driven-development/) for:
- Complete IAM Policy Generator implementation
- spec_validator.py tool for automated compliance checking
- Pre-commit hooks and Git workflow integration
- Full specification examples with authority levels
- Coverage tracking and reporting tools

**Anti-pattern: Spec-Ignored**
Writing code with AI first, then trying to retrofit tests, resulting in tests that mirror implementation rather than specify behavior.

**Anti-pattern: Over-Prompting**
Saving collections of prompts as if they were specifications. Prompts are implementation details; specifications are behavioral contracts.

---

## Image Spec

**Maturity**: Intermediate
**Description**: Upload images (diagrams, mockups, flows) as primary specifications for AI coding tools to build accurate implementations from visual context.

**Related Patterns**: [Spec-Driven Development](#spec-driven-development), [Progressive Enhancement](#progressive-enhancement), [Context Optimization](experiments/README.md#context-optimization)

**Core Implementation**

Use images as the source of truth for structure and intent, then supplement with minimal text constraints:

```bash
# 1. Prepare visual specifications
# - architecture.png (components + labeled ports)
# - data-model.png (fields + relationships)
# - ui-mock.png (layout + key interactions)

# 2. Attach images and provide a minimal build request
cat > build-request.txt << 'EOF'
Build the system from the attached diagrams.
Tech stack: Node.js + Express + PostgreSQL
Start with the User Service exactly as shown.
Include /health endpoints for every service.
EOF

# 3. Iterate with visual feedback
# - Screenshot the running output
# - Annotate with required changes
# - Re-attach and request the next iteration
```

**Complete Implementation**

See [examples/image-spec/](examples/image-spec/) for prompt templates, diagram checklists, and a repeatable image-first iteration loop.

**Anti-pattern: Overwhelming Visuals**

Uploading many diagrams at once without hierarchy or a clear starting point overwhelms context, increases contradictions, and reduces accuracy. Start with one high-level diagram, implement one slice, then add more visuals progressively.

---

## Planned Implementation

**Maturity**: Beginner
**Description**: Interview, constrain, and plan before writing code so AI implementation matches actual requirements instead of confident-sounding assumptions.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Spec-Driven Development](#spec-driven-development), [Progressive Enhancement](#progressive-enhancement), [Cross-Model Validation](#cross-model-validation)

**Core Principle: Think Before You Code**

The costliest bugs come from building the wrong thing, not building it wrong. This pattern front-loads three activities before any code is written:

1. **Interview** — have AI ask structured questions to surface tacit knowledge, hidden constraints, and decisions that would otherwise emerge mid-implementation.
2. **Constrain** — translate the interview answers into explicit boundaries the AI must respect (line counts, dependencies, performance budgets, prohibited approaches).
3. **Plan** — generate an explicit step-by-step implementation plan, review it, and iterate before any code is generated.

**Planning Workflow**

```mermaid
graph TD
    A[Idea or Request] --> B[AI Interviews You<br/>Clarifying Questions]
    B --> C{Gaps Remain?}
    C -->|Yes| B
    C -->|No| D[Define Explicit Constraints<br/>Line count, deps, perf budget]
    D --> E[Generate Initial Plan]
    E --> F[Review & Refine Plan]
    F --> G{Plan Approved?}
    G -->|No| E
    G -->|Yes| H[Execute Implementation]
    H --> I[Validate Against Plan]
    I --> J{Meets Plan?}
    J -->|No| H
    J -->|Yes| K[Complete]

    style B fill:#e1f5e1
    style D fill:#e1f5e1
    style F fill:#e1f5e1
    style H fill:#ffe6e6
    style K fill:#e1f5e1
```

**Interview Phase**

Before writing any plan, have AI act as an interviewer:

```bash
ai "I want to build a notification system for our app.

Before writing any code or plan, interview me:
1. Ask clarifying questions about requirements I haven't stated
2. Identify constraints I should decide on upfront
3. Surface assumptions that could cause rework later
4. Group your questions by category (scope, technical, users, edge cases)

Ask one category at a time. Wait for my answers before continuing."
```

Typical interview output groups questions by category — scope ("Which channels? In-app, email, SMS?"), technical ("Expected volume — 10/day vs 10,000/hour changes architecture"), users ("Can users configure preferences?"), edge cases ("What happens when delivery fails?"). After answers are collected, ask AI to consolidate them into a requirements summary, an explicit non-goals list, and remaining open questions — that document becomes the input to the planning phase.

**Constraint Phase**

Translate the interview answers into the boundaries the AI must respect. Constraints prevent over-engineering more reliably than instructions to "keep it simple":

```
Bad:  "Create user service"
Good: "Create user service: <100 lines, 3 methods max, only bcrypt dependency"

Bad:  "Add caching"
Good: "Add caching using Map, max 1000 entries, LRU eviction"

Bad:  "Improve performance"
Good: "Reduce p99 latency to <50ms without new dependencies"
```

Carry these constraints into every subsequent prompt — they're the steering, not the suggestion.

**Core Implementation**

**1. Plan Generation Phase**
```bash
# Example planning prompt structure
CONTEXT: "Building user authentication for SaaS application"
REQUIREMENTS: "JWT tokens, password reset, rate limiting"
CONSTRAINTS: "Must integrate with existing user table, 2-hour time limit"

REQUEST: "Generate step-by-step implementation plan with:
- Database changes needed
- API endpoints to create/modify
- Security considerations
- Testing approach
- Rollback strategy"
```

**2. Plan Review and Iteration**
```markdown
# Generated Plan Review Checklist

### Technical Approach
- [ ] Database schema changes are backwards compatible
- [ ] API design follows existing conventions
- [ ] Security measures address OWASP top 10
- [ ] Performance impact is minimal

### Implementation Strategy
- [ ] Tasks are broken into deployable increments
- [ ] Dependencies are clearly identified
- [ ] Rollback plan is feasible
- [ ] Testing strategy covers edge cases

### Resource Requirements
- [ ] Time estimate is realistic
- [ ] Required permissions are available
- [ ] External dependencies are identified
```

**3. Execution with Plan Validation**
```bash
# During implementation, validate against plan
echo "✓ Step 1: Created user_sessions table (matches plan)"
echo "✓ Step 2: Added JWT service (matches plan)"
echo "⚠ Step 3: Rate limiting - using Redis instead of in-memory (plan deviation documented)"
```

**Tool-Agnostic Planning Approach**

**Planning Session Structure**
```markdown
## 1. Problem Definition (2-3 sentences)
Clear statement of what needs to be built and why

## 2. Constraints & Requirements
- Technical constraints (existing systems, performance, security)
- Business requirements (timeline, user experience, compliance)
- Resource constraints (team size, expertise, budget)

## 3. Implementation Options
- Option A: [Brief description, pros/cons, time estimate]
- Option B: [Brief description, pros/cons, time estimate]
- Recommended: [Choice with justification]

## 4. Detailed Plan
- [ ] Step 1: [Concrete action with acceptance criteria]
- [ ] Step 2: [Concrete action with acceptance criteria]
- [ ] Step 3: [Concrete action with acceptance criteria]

## 5. Validation Strategy
How to verify each step works and overall solution meets requirements
```


**When to Use Plan-First Development**

- **Complex Features**: Multi-step implementations requiring coordination
- **Unknown Domains**: Working in unfamiliar technologies or business areas
- **Team Collaboration**: When multiple developers need to understand the approach
- **High-Stakes Changes**: Security, performance, or business-critical modifications
- **Learning Contexts**: When using AI to explore new implementation approaches

**Complete Implementation**

See [examples/planned-implementation/](examples/planned-implementation/) for:
- Tool-specific planning examples (Claude Code, Cursor)
- Planning templates and checklists
- Markdown iteration techniques and stakeholder review cycles
- Integration with existing development workflows
- Plan validation and iteration strategies

**Anti-pattern: Blind Generation**
Jumping straight from a vague idea to code generation without interviewing for requirements or setting constraints. AI fills the gaps with assumptions — often reasonable-sounding but wrong for your context — and you discover requirements through failed implementations instead of conversation.

**Anti-pattern: Unconstrained Generation**
Skipping the constraint phase. Telling AI to "make it good" or "add features" without explicit boundaries produces over-engineered solutions that are hard to review.

**Anti-pattern: Over-Constrained**
Stacking so many constraints ("exactly 50 lines, 2 methods, no dependencies, 100% test coverage, sub-10ms response time") that AI can't find a coherent solution. Constraints are budgets, not handcuffs — pick the ones that matter for this task.

**Anti-pattern: Over-Analysis**
Spending excessive time refining plans without moving to implementation, missing opportunities for rapid feedback and iterative improvement.

---


## Progressive Enhancement

**Maturity**: Beginner  
**Description**: Build complex features through small, deployable iterations rather than big-bang generation.

**Related Patterns**: [Planned Implementation](#planned-implementation), [Developer Lifecycle](#developer-lifecycle), [Image Spec](#image-spec), [Cross-Model Validation](#cross-model-validation)

**Examples**
Building authentication progressively:
```bash
# Day 1: Minimal login
"Create POST /login that returns 200 for admin/admin, 401 otherwise"
→ Deploy

# Day 2: Real password check
"Modify login to check passwords against users table. Keep existing API."
→ Deploy

# Day 3: Add security
"Add bcrypt hashing to login. Support both hashed and plain passwords temporarily."
→ Deploy

# Day 4: Modern tokens
"Replace session with JWT. Keep session endpoint for backward compatibility."
→ Deploy
```

**Developer Review Required**: Each iteration requires developer review and testing of AI-generated code before deployment.

**When to Use [Progressive Enhancement](#progressive-enhancement)**

- **MVP Development**: When you need to get to market quickly with minimal features
- **Uncertain Requirements**: When requirements are likely to change based on user feedback  
- **Risk Mitigation**: When you want to reduce the risk of large, complex implementations
- **Continuous Delivery**: When you have automated deployment and want rapid iterations
- **Learning Projects**: When the team is learning new technologies or domains

**Anti-pattern: Monolithic Generation**
Asking AI to "create a complete user management system" results in 5000 lines of coupled, untested code that takes days to review and debug.

---

## Cross-Model Validation

**Maturity**: Intermediate
**Description**: Run the same task across multiple frontier models and use their agreements, disagreements, and divergences as eval signal for high-stakes decisions, risk-bearing prompts, and design reviews.

**Related Patterns**: [Planned Implementation](#planned-implementation), [Progressive Enhancement](#progressive-enhancement), [Spec-Driven Development](#spec-driven-development)

**Core Loop**

```mermaid
graph TD
    A[High-Stakes Prompt] --> B[Fan Out to N Models]
    B --> C1[Claude Opus]
    B --> C2[GPT-5]
    B --> C3[Gemini]
    C1 --> D[Side-by-Side Outputs]
    C2 --> D
    C3 --> D
    D --> E{Convergent?}
    E -->|Yes| F[Stronger Prior<br/>Proceed With Confidence]
    E -->|No| G[Investigate the Divergence<br/>Disagreement IS the Finding]
    G --> H[Choose, Synthesize, or Re-Prompt]

    style D fill:#a8d5ba,stroke:#2d5a3f,color:#1a3a25
    style G fill:#f9e79f,stroke:#b7950b,color:#7d6608
    style F fill:#f5b7b1,stroke:#c0392b,color:#78281f
```

**When to Use**

Cost grows linearly with the number of models, so don't fan out every prompt. Use this pattern when:

- **Irreversible decisions**: schema migrations, public API contracts, security model changes
- **High-stakes reviews**: pre-merge architecture review, threat modeling, incident post-mortems
- **Eval-style spot-checks**: validating a single canonical prompt that drives downstream automation
- **Onboarding a new model**: comparing a candidate model's output against your trusted baseline before adopting it

For routine prompts, the single-model alternatives form (below) is sufficient and cheaper.

**Core Implementation**

```bash
#!/usr/bin/env bash
# fan-out.sh — run the same prompt across multiple models
PROMPT_FILE="$1"
mkdir -p .cross-model/$(date +%Y%m%d-%H%M%S)
RUN_DIR=$(ls -td .cross-model/* | head -1)

for model in \
  "claude-opus-4-7" \
  "gpt-5" \
  "gemini-2.5-pro"; do
    echo "→ $model"
    llm -m "$model" < "$PROMPT_FILE" > "$RUN_DIR/${model}.md"
done

# Diff the outputs to surface divergence quickly
diff -u "$RUN_DIR/claude-opus-4-7.md" "$RUN_DIR/gpt-5.md"     > "$RUN_DIR/claude-vs-gpt.diff"  || true
diff -u "$RUN_DIR/gpt-5.md"           "$RUN_DIR/gemini-2.5-pro.md" > "$RUN_DIR/gpt-vs-gemini.diff" || true

echo "Outputs in $RUN_DIR — review the .diff files first."
```

**Reading the Results**

| Outcome | What it means | Action |
|---|---|---|
| All models agree | Stronger prior than any single model alone | Proceed |
| 2 agree, 1 disagrees | The minority report may be catching something the majority missed | Read the dissent carefully before discarding |
| All three disagree | The prompt is underspecified, the task is genuinely ambiguous, or you're at the frontier of model capability | Re-prompt with sharper constraints, or treat as a human-judgment call |

**The disagreement IS the signal.** Don't reduce three rich outputs to a vote count — investigate *why* the models split. That investigation is the value the pattern delivers, not the "winning" answer.

**Single-Model Alternatives (Degenerate Form)**

When the cost of fanning out across providers isn't justified, ask one model for multiple options in a single call:

```
"Generate 3 different authentication approaches. For each: performance profile,
security trade-offs, implementation complexity, and when to choose it.
Then recommend one based on a typical SaaS startup's constraints."
```

This is cheaper but provides weaker signal — the alternatives share a single model's training biases. Modern IDE assistants offer this natively as "alternative completions"; named pattern status is unwarranted on its own, but it's worth knowing as the budget-friendly cousin of the full pattern.

**Anti-pattern: Single-Model Bias**

Committing irreversible decisions on a single model's output without ever checking whether another frontier model would have made the same call. The decision feels well-reasoned because the model's prose is confident — but confidence is not correctness, and one model's blind spots become the project's blind spots.

**Anti-pattern: Voting Theater**

Running three models and treating majority rule as truth. Frontier models are trained on overlapping data and exhibit correlated errors; 2-of-3 agreement on a wrong answer is common when the wrong answer is the most plausible-sounding one. Use the votes as a *prompt for investigation*, never as a verdict.

---


## Parallel Agents

**Maturity**: Advanced  
**Description**: Run multiple AI agents concurrently on isolated tasks or environments to maximize development speed and exploration.

**Related Patterns**: [Workflow Orchestration](experiments/README.md#workflow-orchestration), [Atomic Decomposition](#atomic-decomposition), [Security Sandbox](#security-sandbox)

**Agent Coordination Lifecycle**

```mermaid
sequenceDiagram
    participant M as Manager
    participant A1 as Auth Agent
    participant A2 as API Agent  
    participant A3 as Test Agent
    participant SM as Shared Memory
    participant CS as Conflict Scanner
    
    M->>A1: Start (OAuth2 Task)
    M->>A2: Start (REST API Task)
    M->>A3: Start (Test Suite Task)
    
    par Parallel Development
        A1->>A1: Implement OAuth2 Flow
        A1->>SM: Record Learning
    and
        A2->>A2: Implement REST Endpoints
        A2->>SM: Record API Patterns
    and
        A3->>A3: Generate Integration Tests
        A3->>SM: Record Test Patterns
    end
    
    SM->>CS: Trigger Conflict Analysis
    CS->>M: Report Conflicts/All Clear
    M->>M: Merge Components & Cleanup
```

**Core Implementation Approaches**

```yaml
# Container-based isolation
# docker-compose.parallel-agents.yml
services:
  agent-auth:
    image: ai-dev-environment:latest
    volumes:
      - ./feature-auth:/workspace:rw
      - shared-memory:/shared:ro
    environment:
      - AGENT_ID=auth-feature
      - TASK_ID=implement-oauth2
    networks:
      - agent-network

  agent-api:
    image: ai-dev-environment:latest
    volumes:
      - ./feature-api:/workspace:rw
      - shared-memory:/shared:ro
    environment:
      - AGENT_ID=api-feature
      - TASK_ID=implement-rest-endpoints

volumes:
  shared-memory:
    driver: local
networks:
  agent-network:
    driver: bridge
    internal: true
```

**Git Worktree Parallelization**

```bash
# Create isolated branches for parallel work
git worktree add -b agent/auth ../agent-auth
git worktree add -b agent/api ../agent-api
git worktree add -b agent/tests ../agent-tests

# Launch agents in parallel
parallel --jobs 3 << EOF
cd ../agent-auth && ai-agent implement-oauth2
cd ../agent-api && ai-agent implement-rest-endpoints
cd ../agent-tests && ai-agent generate-integration-tests
EOF

# Automated conflict detection and merge
for branch in $(git branch -r | grep 'agent/'); do
  git checkout -b temp-merge main
  if git merge --no-commit --no-ff $branch; then
    echo "✓ No conflicts in $branch"
    git merge --abort
  else
    echo "⚠ Conflicts detected - using AI resolution"
    ai-agent resolve-conflicts --branch $branch
  fi
  git checkout main && git branch -D temp-merge
done

# Cleanup
git worktree remove ../agent-auth
git worktree remove ../agent-api
git worktree remove ../agent-tests
```

**Shared Memory & Coordination**

```python
import fcntl

# Agent coordination with shared knowledge
class AgentMemory:
    def record_learning(self, agent_id, key, value):
        """Thread-safe learning capture with file locking"""
        with fcntl.flock(self.lock_file, fcntl.LOCK_EX):
            self.memory[agent_id][key] = value
        
    def get_shared_knowledge(self):
        """Consolidated knowledge from all agents"""
        return self.consolidated_memory

# Task definition
tasks = {
    "auth-service": {
        "agent_count": 1,
        "isolation": "container", 
        "dependencies": [],
        "instructions": "Implement OAuth2 with JWT tokens"
    },
    "api-endpoints": {
        "agent_count": 2,
        "isolation": "worktree",
        "dependencies": ["auth-service"],
        "instructions": "REST endpoints: user mgmt + CRUD"
    }
}
```

**Complete Implementation**: See [examples/parallel-agents/](examples/parallel-agents/) for:
- Full Docker isolation and coordination setup
- Git worktree management and conflict resolution
- Shared memory system with file locking
- Emergency shutdown and safety monitoring
- Task distribution and dependency management

**When to Use [Parallel Agents](#parallel-agents)**
- **Complex features** requiring multiple specialized implementations
- **Time-critical projects** where speed trumps coordination overhead
- **Exploration phases** testing multiple approaches simultaneously
- **Large teams** with strong DevOps and coordination processes

**Source**: [AI Native Dev - How to Parallelize AI Coding Agents](https://ainativedev.io/news/how-to-parallelize-ai-coding-agents)

**Anti-pattern: Uncoordinated Agents**
Running multiple agents without isolation, shared memory, or conflict resolution leads to race conditions, lost work, and system instability.

---


## Context Persistence

**Maturity**: Intermediate
**Description**: Manage AI context as a finite resource through structured memory schemas, prompt pattern capture, and session continuity protocols for efficient multi-session development.

**Related Patterns**: [Codified Rules](#codified-rules), [Progressive Disclosure](#progressive-disclosure), [Spec-Driven Development](#spec-driven-development), [Parallel Agents](#parallel-agents)

**Core Principles**

AI context is a finite resource with diminishing returns. Effective context engineering requires:
- **Minimal High-Signal Tokens**: Find the smallest set of information that maximizes outcomes
- **Just-in-Time Retrieval**: Load context dynamically rather than pre-loading everything
- **[Progressive Disclosure](#progressive-disclosure)**: Explore and discover information as needed, not upfront

**Structured Memory Schemas**

Persist information outside the context window using standardized memory formats:

```markdown
# TODO.md - Task tracking across sessions
- [ ] Implement JWT middleware (blocked: key rotation design)
- [x] Add bcrypt password hashing (2024-01-15)
- [ ] Rate limiting (next: research token bucket vs sliding window)

# DECISIONS.log - Architectural decisions with timestamp
2024-01-15 10:30: Use RS256 for JWT (not HS256)
Rationale: Asymmetric keys enable better key rotation
Alternatives: HS256 (simpler but less flexible)
Impact: auth-service, api-gateway

# NOTES.md - Session continuity and discoveries
Session 2024-01-15:
  Context: Implementing authentication system
  Discoveries: bcrypt has performance issues >100 req/s
  Blockers: Need to decide on refresh token storage
  Next: Benchmark argon2 as bcrypt alternative

# scratchpad.md - Working memory (cleared after task)
Exploring JWT refresh token flow...
- httpOnly cookies prevent XSS
- Need CSRF protection for cookie-based auth
```

**Prompt Pattern Library**

Capture successful prompts and failures with success rates for reuse:

```bash
# Initialize knowledge structure
./knowledge-capture.sh --init

# Capture successful pattern
./knowledge-capture.sh --success \
  --domain "auth" \
  --pattern "JWT Auth" \
  --prompt "JWT with RS256, 15min access, httpOnly cookie" \
  --success-rate "95%"

# Document failure to avoid repeating
./knowledge-capture.sh --failure \
  --domain "auth" \
  --bad-prompt "Make auth secure" \
  --problem "Too vague → AI over-engineers" \
  --solution "Specify exact JWT requirements"
```

**Context Window Management**

**Compaction Strategy** - When context approaches limits:
1. Distill critical decisions to `DECISIONS.log`
2. Summarize key discoveries in `NOTES.md`
3. Update `TODO.md` with current state and blockers
4. Create "Previously on..." recap for session continuity

**Session Continuity Protocol** - Resume work across sessions:
1. Read `NOTES.md` for previous session context
2. Review `TODO.md` for current tasks and blockers
3. Check `DECISIONS.log` for recent architectural choices
4. Scan `scratchpad.md` for active explorations

```bash
# Compact context when nearing limits
./context-compact.sh --summarize

# Resume from previous session
./session-resume.sh  # Displays TODO + recent decisions + notes recap
```

**Complete Implementation**: See [examples/context-persistence/](examples/context-persistence/) for:
- Memory schema templates (TODO.md, DECISIONS.log, NOTES.md, scratchpad.md)
- Context compaction and session resume automation scripts
- Prompt pattern capture and maintenance tools
- Working examples of memory schemas in use

**Anti-pattern: Over-Documentation**

Creating extensive knowledge bases that become maintenance burdens instead of accelerating development through selective, actionable knowledge capture.

**Why it's problematic:**
- Knowledge bases become outdated and misleading
- Developers spend more time documenting than developing
- Overly detailed entries are ignored in favor of quick experimentation
- Knowledge becomes siloed and not easily discoverable

**Instead, focus on:**
- Capture only high-impact patterns (>80% success rate)
- Document failures that wasted significant time (>30 minutes)
- Keep entries concise and immediately actionable
- Review and prune knowledge quarterly

**Anti-pattern: Bloated Context**

Loading entire codebases, documentation, or conversation history into context rather than using structured memory and just-in-time retrieval.

**Why it's problematic:**
- Wastes tokens on low-signal information
- Degrades AI performance due to information overload
- Slows interaction latency and increases costs
- Misses the forest for the trees

**Instead:**
- Use lightweight identifiers (file paths, links) rather than full content
- Load context progressively as needed
- Externalize detailed information to memory schemas
- Prefer 3-5 high-quality examples over exhaustive documentation

---

## Event Automation

**Maturity**: Intermediate
**Description**: Execute custom commands automatically at assistant lifecycle events (pre/post tool use, session start, prompt submission) for workflow automation, validation, and policy enforcement.

**Related Patterns**: [Codified Rules](#codified-rules), [Security Sandbox](#security-sandbox), [Custom Commands](#custom-commands), [Autonomous Remediation](#autonomous-remediation)

**Core Concept**

Attach shell commands to AI assistant lifecycle events. Commands receive context via environment variables (file paths, tool names, user prompts) and return exit codes to allow/block/warn.

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
if echo "$FILE" | grep -E "(\\.env|secrets\\.json|credentials)" > /dev/null; then
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

**Complete Implementation**

See [examples/event-automation/](examples/event-automation/) for a working implementation with security scanning and hooks.

**Anti-pattern: Unchecked Events**

Running automation from untrusted sources without review exposes your system to malicious code execution and credential theft. Always audit event scripts before installation.

---

## Custom Commands

**Maturity**: Intermediate
**Description**: Discover and use built-in command vocabularies, then extend them with custom commands that encode domain expertise and sophisticated workflows.

**Related Patterns**: [Event Automation](#event-automation), [Spec-Driven Development](#spec-driven-development), [Codified Rules](#codified-rules), [Progressive Disclosure](#progressive-disclosure)

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

| Use Built-in Commands | Create [Custom Commands](#custom-commands) |
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

# Usage
/refactor              # Full analysis
/refactor --smell      # Code smells only

# Implementation

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
cp examples/custom-commands/commands/*.md .claude/commands/

# Cursor IDE: .cursorrules
cat examples/custom-commands/commands/refactor.md >> .cursorrules

# Generic: .ai/commands/ (tool-agnostic)
mkdir -p .ai/commands
cp examples/custom-commands/commands/*.md .ai/commands/
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

## Progressive Disclosure

**Maturity**: Intermediate
**Description**: Load AI assistant rules incrementally based on task context rather than bundling all instructions upfront, preventing context bloat and improving instruction-following consistency.

**Related Patterns**: [Codified Rules](#codified-rules), [Context Persistence](#context-persistence), [Custom Commands](#custom-commands), [Event Automation](#event-automation), [Centralized Rules](#centralized-rules), [Context Optimization](experiments/README.md#context-optimization)

**Core Problem**

AI coding assistants already consume part of their context window with built-in system instructions. When a project loads a single, monolithic rules file (hundreds of lines) for every task, instruction-following accuracy drops and irrelevant guidance crowds out what the model needs right now.

**Implementation Strategy: Three-Tier Rule Architecture**

Keep a small universal rules file, and load specialized rules only when the task touches the relevant area:

```
.ai/
├── CLAUDE.md                    # Universal rules only (<60 lines)
├── rules/                       # Specialized rules loaded on-demand
│   ├── security/                # secrets, auth, dependencies
│   ├── development/             # api-design, database, testing
│   ├── operations/              # deployment, monitoring, cicd
│   └── architecture/            # patterns, performance
└── prompts/                     # Reusable task templates
```

**Main Rules File = Router**

The main file should explicitly tell the assistant what to load based on context:

```markdown
# AI Development Rules

# Universal Principles (Always Apply)
- Follow existing patterns in the codebase
- Never commit secrets or credentials
- Run tests after code changes

# Progressive Disclosure (Context Loading)
- **Security work** (auth/, .env, credentials): Read `.ai/rules/security/`
- **API development** (api/, routes/): Read `.ai/rules/development/api-design.md`
- **Database changes** (migrations/, models/): Read `.ai/rules/development/database.md`
- **Testing** (tests/, specs/): Read `.ai/rules/development/testing.md`
- **CI/CD** (.github/workflows/): Read `.ai/rules/operations/cicd.md`
```

**Automatic Loading with Hooks**

Combine with [Event Automation](#event-automation) to auto-load the right rules before tool use:

```bash
#!/bin/bash
# .ai/hooks/auto-load-context.sh

FILE_PATH="$TOOL_INPUT_FILE_PATH"
LOADED_RULES=""

if echo "$FILE_PATH" | grep -Eq "(\\.env|credentials|secrets|auth/)"; then
  LOADED_RULES="$LOADED_RULES .ai/rules/security/"
fi

if echo "$FILE_PATH" | grep -Eq "(api/|routes/|controllers/)"; then
  LOADED_RULES="$LOADED_RULES .ai/rules/development/api-design.md"
fi

if echo "$FILE_PATH" | grep -Eq "(tests?/|spec/|\\.test\\.|\\.spec\\.)"; then
  LOADED_RULES="$LOADED_RULES .ai/rules/development/testing.md"
fi

if [ -n "$LOADED_RULES" ]; then
  echo "AI: Before proceeding, read these files: $LOADED_RULES"
fi
```

**Complete Implementation**

See [examples/progressive-disclosure/](examples/progressive-disclosure/) for templates and a ready-to-adapt rules router + directory layout.

**Anti-pattern: Bloated Configuration**

Loading a single, massive rules file for every task wastes context and reduces instruction-following accuracy—especially for small edits that need only a handful of universal rules.

**Anti-pattern: Missing Guidance**

Creating specialized rule files but never documenting when/how to load them forces humans to remember the routing and prevents consistent, automated context loading.

---

## Atomic Decomposition

**Maturity**: Intermediate  
**Description**: Break complex features into atomic, independently implementable tasks for parallel AI agent execution.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Workflow Orchestration](experiments/README.md#workflow-orchestration), [Progressive Enhancement](#progressive-enhancement), [Issue Generation](#issue-generation), [Parallel Agents](#parallel-agents)

**Atomic Task Criteria**

```mermaid
graph TD
    A[Feature Requirement] --> B[Task Analysis]
    B --> C{Atomic Task Check}
    C -->|✓ Independent| D[Can run in parallel]
    C -->|✓ <2 hours| E[Rapid feedback cycle]
    C -->|✓ Clear I/O| F[Testable interface]
    C -->|✓ No shared state| G[Conflict-free]
    C -->|✗ Fails check| H[Split Further]
    H --> B
    
    D --> I[Ready for Agent]
    E --> I
    F --> I
    G --> I
```

**Core Decomposition Process**

```bash
# Feature: User Authentication System
# Bad: Monolithic task
❌ "Implement complete user authentication with JWT, password hashing, rate limiting, and email verification"

# Good: Atomic breakdown with AI validation
ai_decompose "Break down user authentication into atomic tasks:

Task 1: Password validation service (1.5h)
- Input: plain text password, validation rules
- Output: validation result object
- Dependencies: None (pure function)

Task 2: JWT token generation service (1h)  
- Input: user ID, role, expiration config
- Output: signed JWT token
- Dependencies: None (crypto operations only)

Task 3: Rate limiting middleware (2h)
- Input: request metadata, rate limit config
- Output: allow/deny decision
- Dependencies: None (stateless logic)

Task 4: Login endpoint integration (1h)
- Input: credentials, services from tasks 1-3
- Output: HTTP response with token/error
- Dependencies: Tasks 1-3 (integration only)"

# Validate atomicity
ai_task_validator "Check each task for:
1. <2 hour completion time
2. No shared mutable state
3. Clear input/output contracts
4. Testable in isolation
5. No circular dependencies"
```


**Agent Assignment & Coordination**

```yaml
# .ai/task-assignment.yml
authentication_feature:
  parallel_tasks:
    - id: "auth-001" # Password validation
      agent: "backend-specialist-1"
      estimated_hours: 1.5
      dependencies: []
      
    - id: "auth-002" # JWT generation
      agent: "security-specialist"
      estimated_hours: 1
      dependencies: []
      
    - id: "auth-003" # Rate limiting
      agent: "backend-specialist-2"
      estimated_hours: 2
      dependencies: []
      
  integration_tasks:
    - id: "auth-004" # Login endpoint
      agent: "integration-specialist"
      estimated_hours: 1
      dependencies: ["auth-001", "auth-002", "auth-003"]
```

**Task Contract Validation**

```python
# Ensure tasks meet atomic criteria
class TaskContract:
    def validate_atomic(self) -> bool:
        return all([
            len(self.side_effects) == 0,    # No side effects
            self.estimated_hours <= 2,      # Rapid completion
            self.has_clear_io_contract()    # Testable interface
        ])

# Example validation
task = TaskContract("auth-001")
task.inputs = {"password": str, "rules": PasswordRules}  
task.outputs = {"is_valid": bool, "errors": List[str]}
assert task.validate_atomic()  # ✓ Passes atomic criteria
```

**Complete Implementation**: See [examples/atomic-decomposition/](examples/atomic-decomposition/) for:
- Contract validation system with automated checking
- Function-level decomposition techniques and trigger indicators
- Task dependency resolution and scheduling
- Parallel execution coordination and monitoring
- Agent assignment and resource management

**When to Use [Atomic Decomposition](#atomic-decomposition)**
- **Parallel Agent Implementation**: Multiple AI agents working simultaneously
- **Complex Feature Development**: Large features benefiting from parallel work
- **Time-Critical Projects**: Speed through parallelization essential
- **Risk Mitigation**: Reduce blast radius of individual task failures

**Anti-pattern: False Atomicity**
Creating tasks that appear independent but secretly share state, require specific execution order, or have hidden dependencies on other concurrent work.

**Anti-pattern: Over-Decomposition**  
Breaking tasks so small that coordination overhead exceeds the benefits of parallelization, leading to more complexity than value.

---

## Observable Development

**Maturity**: Intermediate  
**Description**: Design systems with comprehensive logging, tracing, and debugging capabilities that enable AI to understand system behavior and diagnose issues effectively.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Tool Integration](#tool-integration), [Testing Orchestration](experiments/README.md#testing-orchestration), [Spec-Driven Development](#spec-driven-development)

**Core Implementation**

```python
# AI-friendly structured logging
def log_operation(operation, **context):
    logging.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "context": context
    }))

# Observable business logic with comprehensive context
def process_order(order):
    log_operation("order_start", order_id=order.id, total=order.total)
    try:
        validate_order(order)
        log_operation("validation_success")
        result = charge_payment(order)
        log_operation("payment_success", transaction_id=result.id)
        return result
    except PaymentError as e:
        log_operation("payment_error", error=str(e), code=e.code)
        raise
```

**Complete Implementation**: See [examples/observable-development/](examples/observable-development/) for:
- Full structured logging framework with correlation IDs
- Performance monitoring decorators and utilities  
- AI-friendly debug tools and log analysis scripts
- Integration examples for e-commerce and authentication systems

**Anti-pattern: Blind Development**

Building systems with minimal observability that provide insufficient context for AI to understand system behavior, diagnose issues, or suggest improvements.

**Why it's problematic:** AI cannot debug systems with generic logs like "Payment failed" or "Something went wrong" - it needs specific context, timing, and error details.

```python
# Bad: Black box logging
def process_payment(amount):
    try:
        result = payment_service.charge(amount)
        logger.info("Payment processed")
        return result
    except Exception:
        logger.error("Payment failed")
        raise

# Good: Observable implementation  
def process_payment(amount):
    log_operation("payment_start", amount=amount)
    try:
        result = payment_service.charge(amount)
        log_operation("payment_success", transaction_id=result.id)
        return result
    except Exception as e:
        log_operation("payment_error", error=str(e), amount=amount)
        raise
```

---

## Guided Refactoring

**Maturity**: Intermediate  
**Description**: Systematic code improvement using AI to detect and resolve code smells with measurable quality metrics, following established refactoring rules and maintaining test coverage throughout the process.

**Related Patterns**: [Codified Rules](#codified-rules), [Autonomous Remediation](#autonomous-remediation), [Testing Orchestration](experiments/README.md#testing-orchestration), [Debt Forecasting](experiments/README.md#debt-forecasting)

**Code Smell Detection Framework**

```mermaid
graph TD
    A[Code Analysis] --> B[Smell Detection]
    B --> C[Refactoring Strategy]
    C --> D[AI Implementation]
    D --> E[Test Validation]
    E --> F[Quality Metrics]
    F --> G{Improvement?}
    G -->|Yes| H[Commit Changes]
    G -->|No| I[Revert & Retry]
    H --> J[Update Knowledge Base]
    I --> C
```

**Core Workflow**

```bash
# 1. Define refactoring rules
cat > .ai/rules/refactoring.md << 'EOF'
## Long Method Smell
- Max lines: 20 (excluding docstrings)
- Max cyclomatic complexity: 10
- Detection: flake8 C901, pylint R0915

## Large Class Smell  
- Max class lines: 250, Max methods: 20
- Detection: pylint R0902, R0904
EOF

# 2. Detect code smells with AI
flake8 --select=C901 src/ > smells.txt
pylint src/ --disable=all --enable=R0915,R0902,R0904 >> smells.txt

ai "Analyze smells.txt using .ai/rules/refactoring.md:
1. Prioritize by impact and complexity
2. Suggest specific refactoring strategy for each smell
3. Generate implementation plan with risk assessment"

# 3. Apply refactoring with test preservation
pytest --cov=src tests/  # Baseline coverage

ai "Refactor process_user_data() method (35 lines, exceeds threshold):
- Apply Extract Method pattern for validation, database, notifications
- Maintain test coverage >90% and API contract
- Create atomic commits for each extracted method"

# 4. Validate and track improvements
pytest --cov=src tests/
flake8 src/ && pylint src/

ai "Generate refactoring impact report:
Before: complexity=12, length=35 lines, coverage=85%
After: complexity=4+2+2, length=8+6+7 lines, coverage=92%
Document lessons learned in .ai/knowledge/refactoring.md"
```

**Common Refactoring Patterns**

- **Extract Method**: Break down long methods (>20 lines)
- **Extract Class**: Split large classes (>250 lines, >20 methods)  
- **Replace Primitive**: Convert strings/dicts to value objects
- **Consolidate Duplicates**: Merge similar code patterns

**Complete Implementation**: See [examples/guided-refactoring/](examples/guided-refactoring/) for:
- Automated refactoring pipeline with CI integration
- Quality metrics tracking and reporting
- Risk assessment guidelines and rollback procedures
- Knowledge base templates for refactoring outcomes

**Anti-pattern: Scattered Refactoring**
Making widespread changes without systematic analysis leads to introduced bugs and degraded code quality.

**Anti-pattern: Premature Refactoring**
Refactoring code for hypothetical future requirements rather than addressing current code smells and quality issues.

----

## Error Resolution

**Maturity**: Intermediate
**Description**: Automatically collect comprehensive error context from logs, system state, and git history, then use AI to diagnose root causes and generate validated fixes.

**Related Patterns**: [Developer Lifecycle](#developer-lifecycle), [Observable Development](#observable-development), [Tool Integration](#tool-integration), [Autonomous Remediation](#autonomous-remediation), [Testing Orchestration](experiments/README.md#testing-orchestration)

**[Error Resolution](#error-resolution) Workflow**

```mermaid
graph TD
    A[Error Occurs] --> B[Collect Error Context]
    B --> C[Enrich with Git History]
    C --> D[AI Diagnosis]
    D --> E[Generate Fix Proposals]
    E --> F{Human Review}
    F -->|Approved| G[Apply Fix]
    F -->|Rejected| H[Refine Context]
    G --> I[Run Tests]
    I --> J{Tests Pass?}
    J -->|Yes| K[Commit Fix]
    J -->|No| L[Rollback]
    H --> D
    L --> D

    style B fill:#e1f5e1
    style D fill:#ffe6e6
    style G fill:#ffe6e6
    style K fill:#e1f5e1
```

**Core Implementation**

**Step 1: Collect Error Context**

```bash
# Create comprehensive error context file
cat > .error-context.md << EOF
# Error Analysis

**Error Output:**
[Complete error message, stack trace, and exit codes]

**Recent Changes:**
$(git log --oneline -5)

**Affected Files:**
$(git diff --name-only HEAD~1)

**File Contents:**
$(cat path/to/affected/file.ext)

**Environment:**
- OS: $(uname -s)
- Shell: $SHELL
- Working Directory: $(pwd)
EOF
```

**Step 2: AI-Powered Diagnosis**

```bash
# Send structured context to AI for analysis
ai "Analyze this error and provide actionable fixes:

CONTEXT:
$(cat .error-context.md)

REQUIRED OUTPUT:
1. Root cause analysis
2. Specific fix commands (copy-pasteable)
3. Prevention strategy (pre-commit hooks, tests, etc.)

Format fixes as executable bash commands."
```

**Step 3: Validate and Apply Fixes**

```bash
# Create checkpoint before applying fixes
git stash push -m "Pre-fix checkpoint"

# Review AI suggestions
cat ai-suggestions.md

# Apply fixes with validation
bash fix-commands.sh

# Verify with tests
./run-tests.sh

# Commit if successful, rollback if not
if [ $? -eq 0 ]; then
    git add .
    git commit -m "fix: [description based on AI analysis]"
    git stash drop
else
    git stash pop
    echo "Fix failed validation, rolled back"
fi
```

**Practical Workflow Example**

```bash
# 1. Capture error from any source (CI, terminal, logs)
ERROR_LOG="path/to/error.log"

# 2. Enrich with context
cat > error-analysis.md << EOF
**Error:**
$(cat $ERROR_LOG)

**Recent Commits:**
$(git log --oneline -3)

**Changed Files:**
$(git diff --name-only HEAD~1)

**File Contents:**
$(for file in $(git diff --name-only HEAD~1); do
    echo "**$file:**"
    cat $file
done)
EOF

# 3. AI diagnosis
ai "Diagnose and fix:
$(cat error-analysis.md)

Provide:
1. Root cause
2. Exact fix commands
3. How to prevent recurrence"

# 4. Apply and validate
# [Review AI output]
# [Execute suggested fixes]
# [Run tests]
# [Commit]
```

**When to Use [Error Resolution](#error-resolution)**

- **CI/CD Failures**: Diagnose build, test, or deployment failures
- **Local Development Errors**: Debug unexpected errors during development
- **Configuration Issues**: Resolve environment or configuration problems
- **Dependency Conflicts**: Analyze and resolve version conflicts
- **Integration Failures**: Debug issues with external services or APIs

**Complete Implementation**: See [examples/error-resolution/](examples/error-resolution/) for:
- Reusable templates for error context collection and AI prompts
- Common error scenarios (test failures, dependency conflicts, configuration errors)
- GitHub Actions integration for CI/CD error diagnosis
- Automated context extraction and diagnosis workflows

**Anti-pattern: Blind Diagnosis**

Sending only the error message to AI without surrounding context.

```bash
# ❌ Bad: No context
ai "Fix error: Process completed with exit code 1"
```

**Why it's problematic**: AI cannot diagnose the issue without seeing:
- What command failed
- Recent changes that might have caused it
- File contents or configuration
- System environment

**Instead, provide full context:**

```bash
# ✅ Good: Comprehensive context
ai "Fix this error:

Error: Process completed with exit code 1

Command that failed: terraform fmt -check -recursive
Files affected: main.tf, outputs.tf

Recent change:
$(git log -1 --oneline)

File content:
$(cat terraform/main.tf)

Environment: Terraform v1.6.0"
```

**Anti-pattern: Brittle Fixes**

Applying AI-suggested fixes without validation or rollback strategy.

```bash
# ❌ Bad: Apply without review or rollback
ai "Fix this error" | bash
```

**Why it's problematic**:
- AI suggestions may introduce new bugs
- May break existing functionality
- Could make security or data loss mistakes
- No rollback strategy if fix fails

**Instead, validate fixes before applying:**

```bash
# ✅ Good: Validate before applying with rollback
git stash push -m "Pre-fix checkpoint"

# Generate fix
ai "Fix this error" > proposed-fix.sh

# Review the proposed changes
cat proposed-fix.sh

# Apply fix
bash proposed-fix.sh

# Verify changes
git diff

# Run tests to validate
./run-tests.sh

# Commit or rollback
if [ $? -eq 0 ]; then
    git add .
    git commit -m "fix: [description]"
    git stash drop
else
    git stash pop
    echo "Fix failed validation, rolled back"
fi
```

---

## Autonomous Remediation

**Maturity**: Intermediate
**Description**: Pair deterministic rule-based detectors with LLM remediators inside an event-driven loop so codified rule violations are caught and fixed automatically before the AI session continues.

**Related Patterns**: [Codified Rules](#codified-rules), [Event Automation](#event-automation), [Guided Refactoring](#guided-refactoring), [Error Resolution](#error-resolution)

**Source**: Paul Duvall, "[Code Quality Gates: Using Claude Code Hooks to Block Code Smells on Every Write](https://www.paulmduvall.com/claude-code-hooks-code-quality-guardrails/)", February 24, 2026

**Core Loop**

```mermaid
graph TD
    A[AI Writes or Edits File] --> B[PostToolUse Hook Fires]
    B --> C[Deterministic Detector<br/>AST, Linter, Scanner, Policy Engine]
    C --> D{Violations?}
    D -->|No| E[AI Continues]
    D -->|Yes| F[Structured Violation Report<br/>+ Prescribed Fix Hint]
    F --> G[LLM Remediator<br/>Same Session Context]
    G --> A
    D -->|Retry Budget Exhausted| H[Escape Hatch<br/>Raise Threshold, Skip, or Suppress]

    style C fill:#a8d5ba,stroke:#2d5a3f,color:#1a3a25
    style G fill:#f9e79f,stroke:#b7950b,color:#7d6608
    style H fill:#f5b7b1,stroke:#c0392b,color:#78281f
```

**Pattern Anatomy**

Four components must be present for the loop to close:

1. **Deterministic detector**. Codified rules executed by non-LLM logic (AST walker, linter, scanner, type checker, policy engine). Output is reproducible across runs.
2. **Structured violation report**. Machine-parseable list of findings with file path, line number, rule ID, severity, and a prescribed fix hint.
3. **LLM remediator**. The same model that produced the violation, fed the report as feedback. Runs in the same session so prior context carries forward.
4. **Retry budget and escape hatch**. Bounded loop count, per-rule threshold override, or per-file suppression marker. Without this, the loop can run indefinitely on legitimate edge cases.

**Core Implementation**

PostToolUse hook (the mechanism comes from [Event Automation](#event-automation)):

```python
#!/usr/bin/env python3
# ~/.claude/hooks/auto-remediate.py
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detectors import run_all_detectors
from fixes import FIX_HINTS, format_report

event = json.load(sys.stdin)
file_path = event.get("tool_input", {}).get("file_path", "")
if not file_path or not os.path.isfile(file_path):
    sys.exit(0)

violations = run_all_detectors(file_path)
if not violations:
    sys.exit(0)

report = format_report(file_path, violations, FIX_HINTS)
print(json.dumps({"decision": "block", "reason": report}))
sys.exit(0)
```

Each detector emits both the finding AND the prescribed fix, so the LLM remediator gets a concrete starting point instead of guessing which technique to apply:

```python
# detectors/fixes.py
FIX_HINTS = {
    "complexity":      "Use extract-method, early returns, guard clauses, or lookup tables.",
    "long_function":   "Extract helper functions for distinct logical steps.",
    "deep_nesting":    "Use guard clauses and early returns to flatten control flow.",
    "duplicate_block": "Extract repeated code into a shared helper function.",
    "vuln_dependency": "Upgrade to the patched version listed in the advisory.",
    "secret_leak":     "Move the value to a secret manager and reference via env var.",
}
```

Loop semantics:

| Condition | Behavior |
|---|---|
| Clean detector run | Exit 0, AI continues |
| Violations found | Exit with `block` decision and structured report; LLM re-attempts |
| Same file blocked more than 3 consecutive times | Surface to developer; suggest threshold raise or skip-list entry |
| Hook itself crashes | Fail open (exit 0); never silently disable a rule without telling the developer |

**When to Use**

| Use Autonomous Remediation when... | Use plain [Event Automation](#event-automation) when... |
|---|---|
| Violation has a deterministic fix the LLM can apply | Violation is a hard policy ("never edit .env") with no fix path |
| Rule is mechanical (complexity, nesting, dep version, secret pattern) | Rule requires human judgment (architecture, business logic, security tradeoff) |
| Fix can be verified by re-running the same detector | Fix needs out-of-band verification (manual review, production test) |

**Domain Instances**

This pattern recurs across the catalog under domain-specific names. Each is a concrete instantiation of the same detect-fix-verify loop:

| Domain | Detector | LLM Remediator Output | Existing Pattern |
|---|---|---|---|
| Code smells | AST or Lizard complexity rules | Refactored function | [Guided Refactoring](#guided-refactoring) |
| Runtime errors | Stack trace + log scanner | Validated bug fix | [Error Resolution](#error-resolution) |
| Infrastructure drift | Terraform plan diff | Corrective patch | [Drift Remediation](experiments/README.md#drift-remediation) |
| Flaky tests | Build history analyzer | Stabilization patch | [Suite Health](experiments/README.md#suite-health) |
| Stale or vulnerable deps | npm audit, pip-audit, dependabot | Staged upgrade PR | [Upgrade Advisor](experiments/README.md#upgrade-advisor) |
| Security findings | Bandit, Semgrep, gitleaks | Patched code | New instance |

**Complete Example**: See [examples/autonomous-remediation/](examples/autonomous-remediation/) for a working PostToolUse hook with code-smell detectors, fix-hint dictionary, retry budget, multi-language support via Lizard, and skip-list configuration.

**Anti-pattern: Manual Remediation**

Detecting violations with codified rules but leaving the fix to a human reviewer or a separate CI cycle. AI sessions write dozens of files between commits. Violations compound faster than humans can triage them. By the time a reviewer flags one issue, three more have been built on top of it. This converts AI write velocity from an asset into a liability.

```bash
# Bad: detect at commit time, human fixes later
git commit  # pre-commit linter fails, dev manually fixes 12 files

# Good: detect at write time, LLM fixes immediately
# PostToolUse hook blocks, LLM remediates, next file starts clean
```

**Anti-pattern: Unbounded Loop**

Configuring the loop without a retry budget or escape hatch. When the LLM and detector legitimately disagree (a 12-state machine that genuinely needs cyclomatic complexity 14, a wrapper function with 6 parameters mapping to an external API), they ping-pong indefinitely. Each retry costs roughly one model turn of tokens and wall-clock time.

```yaml
# Bad: no exit condition
retry_budget: unlimited
suppression: none

# Good: bounded with explicit escape paths
retry_budget: 3
on_exhaustion: surface_to_developer
suppression:
  directory_skip_list: [tests/, generated/, vendored/]
  threshold_override: .ai/thresholds.yml  # per-file or per-rule
  inline_marker: "# rule: ignore"          # per-call-site
```

---

# Operations Patterns

Operations patterns focus on CI/CD, security, compliance, and production management with AI assistance, building on the foundation and development patterns.

## Security & Compliance Patterns

### Policy Generation

**Maturity**: Advanced
**Description**: Transform compliance requirements into executable policy files with AI assistance, ensuring regulatory requirements become testable code.

**Related Patterns**: [Security Sandbox](#security-sandbox), [Codified Rules](#codified-rules), [Centralized Rules](#centralized-rules)

```bash
# Transform compliance requirements into executable policies
ai "Convert compliance requirements into Cedar policy code:
SOC 2: Data at rest must be AES-256 encrypted" > encryption.cedar

# Validate generated Cedar policies
cedar validate --schema schema.cedarschema encryption.cedar
```

**Complete Implementation**: See [examples/policy-generation/](examples/policy-generation/) for:
- Complete policy generation pipeline with AI assistance
- Cedar/OPA policy templates and compliance mapping
- Policy testing and validation frameworks
- CI/CD integration examples

**Anti-pattern: Untested Policies**
Hand-coding policies from written requirements introduces inconsistencies and interpretation errors.

---

### Security Orchestration

**Maturity**: Intermediate  
**Description**: Aggregate multiple security tools and use AI to summarize findings for actionable insights, reducing alert fatigue while maintaining security rigor.

**Related Patterns**: [Policy Generation](#policy-generation), [Centralized Rules](#centralized-rules)

```bash
# Orchestrate multiple security tools
snyk test --json > snyk.json
bandit -r src -f json > bandit.json
trivy fs --format json . > trivy.json

# AI-powered summarization for actionable insights
ai "Summarize security findings; focus on CRITICAL issues" > pr-comment.txt
gh pr comment --body-file pr-comment.txt
```

**Complete Implementation**: See [examples/security-orchestration/](examples/security-orchestration/) for:
- Complete security scanning pipeline with tool orchestration
- AI-powered report summarization and prioritization
- CI/CD integration and automated PR commenting
- Custom security tool configurations and reporting

**Anti-pattern: Over-Alerting**
Posting every low-severity finding buries real issues and frustrates developers.

---

### Centralized Rules

**Maturity**: Advanced
**Description**: Enforce organization-wide AI rules through a central Git repository that syncs language- and framework-specific guidance into standard assistant configuration files.

**Related Patterns**: [Codified Rules](#codified-rules), [Progressive Disclosure](#progressive-disclosure), [Security Orchestration](#security-orchestration)

**Core Implementation**

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
1. A central repository stores organization rules organized by language/framework.
2. A sync script detects the project language/framework (from files and dependencies).
3. The script generates standard configuration files that common assistants read automatically.

**Key benefits**:
- ✅ Works with existing AI tools (no gateway required)
- ✅ Offline-friendly after initial sync
- ✅ Version-controlled and auditable in Git
- ✅ Language-aware via auto-detection

**Alternative: Gateway Strategy** (advanced use cases)

For organizations needing request/response filtering, policy enforcement, or usage logging, use the gateway approach:
- [Gateway Strategy](examples/centralized-rules/gateway-strategy/README-GATEWAY.md)

**Complete Implementation**

- [Sync Strategy](examples/centralized-rules/sync-strategy/) - Simple Git-based sync (recommended)
- [Gateway Strategy](examples/centralized-rules/gateway-strategy/README-GATEWAY.md) - Central policy + logging + filters

**Anti-pattern: Scattered Configuration**

Copying AI rules into every repository without a central source causes drift, inconsistent enforcement, and manual update toil across teams.

---





# Anti-Patterns Reference

## Common AI Development Anti-Patterns

### Foundation Anti-Patterns
- **Rushing Into AI**: Starting AI adoption without proper assessment
- **Context Drift**: Inconsistent AI rules across team members
- **Unrestricted Access**: Allowing AI tools access to sensitive data
- **Ad-Hoc Development**: Skipping structured development lifecycle

### Development Anti-Patterns
- **Implementation-First AI**: Writing code before defining acceptance criteria
- **Test Generation Without Strategy**: Creating tests without coherent quality goals
- **Big Bang Generation**: Attempting complex features in single AI interaction
- **Uncoordinated Multi-Tool Usage**: Using multiple AI tools without orchestration
- **Black Box Systems**: Insufficient logging for AI debugging
- **Unclear Boundaries**: Ambiguous human-AI handoff points

### Operations Anti-Patterns
- **Fragmented Security**: Isolated security tools without unified framework
- **Alert Fatigue**: Overwhelming developers with low-priority findings
- **Static Deployment**: Fixed scripts without AI adaptation
- **Trusting AI Blue-Green Generation**: Accepting AI output without validation for deployment patterns
- **Reactive Maintenance**: Firefighting instead of proactive AI-assisted management
- **Blind Chaos Testing**: Random fault injection without understanding dependencies

---

# Implementation Guide

## Getting Started

### Phase 1: Foundation (Weeks 1-2)
1. **[Readiness Assessment](#readiness-assessment)** - Evaluate team and codebase readiness
2. **[Codified Rules](#codified-rules)** - Establish consistent AI coding standards
3. **[Security Sandbox](#security-sandbox)** - Implement secure AI tool isolation
4. **[Developer Lifecycle](#developer-lifecycle)** - Define structured development process
5. **[Issue Generation](#issue-generation)** - Generate structured work items from requirements

### Phase 2: Development (Weeks 3-4)
1. **[Spec-Driven Development](#spec-driven-development)** - Implement specification-first approach
2. **[Progressive Enhancement](#progressive-enhancement)** - Practice iterative development
3. **[Cross-Model Validation](#cross-model-validation)** - Stress-test high-stakes decisions across multiple frontier models
4. **[Atomic Decomposition](#atomic-decomposition)** - Break down complex features

### Phase 3: Operations (Weeks 5-6)
1. **[Policy Generation](#policy-generation)** - Codify compliance into executable policy files
2. **[Security Orchestration](#security-orchestration)** - Aggregate scanner findings into actionable summaries
3. **[Centralized Rules](#centralized-rules)** - Sync organization-wide AI standards from a central Git repo

**Note**: For teams practicing continuous delivery, implement security ([Security Sandbox](#security-sandbox), Security Orchestration, Policy Generation) from week 1 alongside foundation patterns. The phases represent learning dependencies, not deployment sequences.

## Success Metrics

### Foundation Metrics
- Team readiness score improvement
- Consistent AI rule adherence across projects
- Zero credential leaks in AI-generated code
- Reduced onboarding time for new developers

### Development Metrics
- Test coverage maintenance (>90% for AI-generated code)
- Reduced code review cycles
- Faster feature delivery with maintained quality
- Decreased debugging time for AI-generated issues

### Operations Metrics
- Automated policy compliance verification
- Reduced deployment failures
- Faster incident response with AI-generated runbooks
- Proactive technical debt management

## Contributing

Have a pattern that's working well for your team? Open an issue or PR to share your experience. The AI development landscape is evolving rapidly, and we're all learning together.

### Pattern Contribution Guidelines
1. Follow the established pattern template (Maturity, Description, Related Patterns, Examples, Anti-patterns)
2. Include practical, runnable examples
3. Specify clear success criteria and anti-patterns
4. Reference related patterns appropriately
5. Test patterns with multiple AI tools when applicable

## License

MIT License - See LICENSE file for details.
