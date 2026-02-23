# AI Development Best Practices

A canonical, enumerated list of best practices derived from comprehensive analysis of AI-assisted development patterns and real-world implementations. Each practice is actionable and stated in 1-2 crisp sentences.

## Foundation & Team Readiness

1. **Assess Before Implementing**: Systematically evaluate team and codebase readiness using [Readiness Assessment](../README.md#readiness-assessment) before introducing AI development patterns.

2. **Establish Codified Rules**: Store AI coding standards, prompts, and preferences in versioned `.ai/` configuration directories using [Codified Rules](../README.md#codified-rules) rather than relying on ad-hoc prompting.

3. **Security by Design**: Run AI tools in isolated environments with no network access, no system privileges, and read-only source code access to prevent credential leaks using [Security Sandbox](../README.md#security-sandbox).

4. **Start Small, Scale Systematically**: Begin with simple AI-assisted tasks and progressively enhance complexity using [Progressive Enhancement](../README.md#progressive-enhancement) rather than attempting comprehensive solutions immediately.

## Workflow & Development Process

5. **Spec-Driven Development**: Write machine-readable specifications with explicit authority levels (system/platform/feature) and unique identifiers before AI implementation to ensure consistent, testable outcomes using [Spec-Driven Development](../README.md#spec-driven-development).

6. **Test-First AI Development**: Create automated tests from specifications before AI code generation, ensuring every specification has corresponding test coverage with measurable success criteria using [Testing Orchestration](../experiments/README.md#testing-orchestration).

7. **Progressive Enhancement Over Big-Bang**: Apply Lean and Kanban principles by building features through small, deployable iterations with daily feedback cycles rather than large-scale AI generation attempts using [Progressive Enhancement](../README.md#progressive-enhancement).

8. **Structured Development Lifecycle**: Follow a systematic 9-stage process from problem definition through deployment and monitoring for consistent AI-assisted development using [Developer Lifecycle](../README.md#developer-lifecycle).

9. **Size Tasks Appropriately**: Use 4-8 hour work items for standard development with [Issue Generation](../README.md#issue-generation) and 1-2 hour atomic tasks for parallel AI agent execution with [Atomic Decomposition](../README.md#atomic-decomposition).

10. **Generate Structured Work Items**: Break down features into specific, testable tasks with clear acceptance criteria using [Issue Generation](../README.md#issue-generation) to ensure continuous development flow.

## Quality & Testing

11. **Testing Orchestration**: Generate complete test suites (unit, integration, performance, security) automatically from specifications using [Testing Orchestration](../experiments/README.md#testing-orchestration).

12. **Maintain Test-to-Specification Traceability**: Link every specification element to automated tests with anchored references and coverage tracking using [Automated Traceability](../README.md#automated-traceability).

13. **Structured Observability**: Implement comprehensive logging with operation context, correlation IDs, and specific error details in standardized formats (JSON/structured) for AI analysis and debugging using [Observable Development](../README.md#observable-development).

14. **Transparent Error Handling**: Design error messages and system responses with sufficient context for AI diagnosis, including error codes, affected components, and suggested remediation steps using [Error Resolution](../README.md#error-resolution).

15. **Validate AI Output**: Always verify AI-generated code through automated testing and human review, especially for security and deployment configurations.

## Parallel & Multi-Agent Development

16. **Safe Agent Parallelization**: Use container isolation or Git worktrees to prevent AI agents from interfering with concurrent work on shared codebases using [Parallel Agents](../README.md#parallel-agents) (and enforce isolation with [Security Sandbox](../README.md#security-sandbox)).

17. **Implement Resource Locking**: Use file-based locking and atomic operations when multiple AI agents need to access shared resources or directories.

18. **Atomic Decomposition**: Break complex features into independently implementable tasks that can be completed in isolation without cross-dependencies using [Atomic Decomposition](../README.md#atomic-decomposition).

19. **Shared Memory for Coordination**: Enable AI agents to share discoveries and coordinate work while maintaining strict isolation boundaries for safety using [Context Persistence](../README.md#context-persistence).

20. **Conflict Detection and Resolution**: Implement automated systems to detect and resolve integration conflicts between parallel AI agent outputs.

## Knowledge & Context Management

21. **Capture High-Impact Knowledge**: Document successful patterns (>80% success rate) and failure modes (>30 minutes wasted) in structured, searchable formats with specific success metrics and context.

22. **Context Optimization**: Match AI tool selection to task complexity using [Context Optimization](../experiments/README.md#context-optimization) and defined criteria: simple models for queries <500 tokens, complex models for architecture decisions >2000 tokens.

23. **Image Spec**: Use diagrams, mockups, and flows as primary specifications for complex needs using [Image Spec](../README.md#image-spec), supplemented with structured text for precise details.

24. **Version Knowledge Assets**: Treat AI development knowledge as code with semantic versioning, peer review processes, and automated quality checks.

25. **AI Model Lifecycle Management**: Establish systematic processes for AI model versioning, performance monitoring, drift detection, and automated retraining triggers.

## Tool Design & Integration

26. **Smart Defaults with Extensibility**: Design AI development tools that work perfectly with no configuration while supporting advanced customization options.

27. **Self-Documenting Commands**: Include comprehensive built-in help with usage patterns, examples, and parameter explanations in every AI development tool using [Custom Commands](../README.md#custom-commands).

28. **Hooks-Based Governance**: Implement flexible hook systems for automated monitoring, logging, and policy enforcement at critical development workflow points using [Event Automation](../README.md#event-automation).

29. **Modular Command Architecture**: Organize AI tools into clear categories with well-defined scopes (project-specific vs. machine-wide) for flexible workflows.

30. **Use Specialized Subagents**: Use [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) to offload specialized tasks to isolated AI assistants with custom prompts, tools, and context for consistent, focused execution.

31. **Experimental Design Frameworks**: Treat experimental AI development features as sophisticated specifications that map future advanced workflows.

## Operations & Automation

32. **Policy Generation**: Transform compliance specifications into executable Cedar/OPA policy files using AI assistance for consistency and automation with [Policy Generation](../README.md#policy-generation).

33. **Security Orchestration**: Aggregate multiple security tools and use AI to summarize findings, reducing alert fatigue while maintaining rigor with [Security Orchestration](../README.md#security-orchestration).

34. **Baseline Management**: Use AI to analyze historical data and establish intelligent monitoring thresholds that minimize false positives using [Baseline Management](../README.md#baseline-management).

35. **Incident Automation**: Generate actionable playbooks from historical incident data and continuously improve operational procedures using [Incident Automation](../experiments/README.md#incident-automation).

36. **Infrastructure as Specifications**: Generate deployment configurations and infrastructure code from plain-English specifications using AI assistance.

37. **Operational Readiness Reviews (ORRs)**: Conduct systematic pre-deployment reviews using data-driven checklists derived from past incidents to prevent known operational risks across workloads.

## AI Ethics & Model Governance

38. **Bias Detection and Mitigation**: Implement automated bias testing in AI model outputs using diverse test datasets and continuous monitoring for fairness across demographic groups.

39. **AI Decision Transparency**: Ensure AI-generated decisions include explainable reasoning, confidence scores, and alternative options when impacting user experience or business logic.

40. **Model Performance Monitoring**: Establish automated monitoring for AI model accuracy, latency, and drift with defined thresholds for performance degradation alerts.

41. **Ethical AI Boundaries**: Define explicit constraints for AI tool usage including prohibited use cases, data privacy specifications, and human oversight specifications for critical decisions.

42. **AI Output Validation**: Implement multi-layered validation including automated testing, peer review, and domain expert verification for AI-generated code and configurations.

## AI-Enhanced Traditional Practices

43. **SOLID Principles for AI Code**: Apply Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion specifically to AI-generated code to ensure maintainable, extensible systems.

44. **Clean Architecture with AI Layers**: Structure AI applications using Clean Architecture principles with dedicated layers for AI model interfaces, business rules, and external AI service dependencies.

45. **Domain-Driven Design for AI Systems**: Use DDD bounded contexts to separate AI model domains, ensuring clear boundaries between different AI capabilities and business contexts.

46. **Well-Architected AI Systems**: Apply AWS Well-Architected Framework pillars (Operational Excellence, Security, Reliability, Performance, Cost Optimization, Sustainability) specifically to AI workloads and model deployments.

47. **Contract-First AI Integration**: Define clear contracts and interfaces for AI components using Design by Contract principles, ensuring predictable behavior and error handling.

48. **Lean AI Development**: Apply Lean principles to eliminate waste in AI model training, reduce unnecessary experimentation, and focus on value-delivering AI features.

49. **Continuous Integration for AI**: Implement CI pipelines that include AI model validation, performance regression testing, and automated deployment of AI components alongside traditional code.

50. **Chaos Engineering for AI Systems**: Apply chaos engineering principles to AI systems by introducing controlled failures in AI model responses, degraded model performance, and service dependencies.

## Version Control Security

51. **Signed Commits**: Configure Git to sign all commits and tags using SSH keys to verify author identity and prevent commit spoofing. Anyone can set `user.name` and `user.email` to impersonate another committer — signed commits prove authenticity and display a "Verified" badge on GitHub.

    **SSH signing setup (recommended):**
    ```bash
    git config --global gpg.format ssh
    git config --global user.signingkey ~/.ssh/id_ed25519
    git config --global commit.gpgsign true
    git config --global tag.gpgSign true
    ```

    **GitHub requirement:** Upload the same SSH public key as a **Signing Key** under *Settings > SSH and GPG keys* (this is a separate entry from the Authentication Key).

    **Enforcement:** Enable *"Require signed commits"* in GitHub branch protection rules for all protected branches.

    **Verification:**
    ```bash
    git log --show-signature -1
    git verify-commit HEAD
    ```

52. **Unicode and Trojan Source Scanning**: Add automated CI/CD checks that reject commits containing invisible Unicode control characters — bidirectional overrides (U+202A, U+202E, U+2066–U+2069), zero-width joiners/non-joiners, and homoglyph substitutions — which attackers use to make malicious code visually appear benign (CVE-2021-42574).

    **Example CI step (GitHub Actions):**
    ```yaml
    - name: Scan for Trojan Source characters
      run: |
        if grep -rPn '[\x{200B}\x{200C}\x{200D}\x{2060}\x{FEFF}\x{202A}-\x{202E}\x{2066}-\x{2069}]' \
          --include='*.py' --include='*.js' --include='*.ts' --include='*.go' \
          --include='*.java' --include='*.rb' --include='*.rs' .; then
          echo "ERROR: Suspicious Unicode control characters detected"
          exit 1
        fi
    ```

    **Additional measures:** Use language-specific linters (`bidichk` for Go, `pylint` Unicode checks for Python) and block confusable homoglyphs in identifiers (e.g., Cyrillic "а" vs Latin "a").

53. **Prompt Injection Prevention**: Defend AI-integrated applications against prompt injection by enforcing strict boundaries between system instructions and untrusted input, validating both inputs and outputs, and monitoring for anomalous behavior.

    **Core defenses:**
    - **System/user prompt separation** — never concatenate untrusted input directly into system prompts; use structured message roles and delimiters
    - **Input sanitization** — strip or escape control tokens, instruction-like prefixes ("Ignore previous instructions…"), and role-override attempts before passing user content to models
    - **Output validation** — parse AI responses through deterministic validators (schema checks, allowlists, regex) before acting on them; never execute raw model output as code or commands
    - **Least-privilege tool access** — limit which tools and APIs an AI agent can invoke; scope permissions to the minimum required for the task
    - **Rate limiting and anomaly detection** — monitor for unusual prompt lengths, repetitive override attempts, and sudden behavioral shifts that indicate injection attacks

## Anti-Patterns to Avoid

54. **No Assessment Rush**: Don't implement AI development patterns without first evaluating team readiness and codebase architecture quality.

55. **Avoid Ad-Hoc Development**: Don't jump directly to AI coding without structured lifecycle processes, proper planning, or testing strategy.

56. **No Implementation-First Development**: Don't generate code first then retrofit tests - always establish specifications and tests before implementation.

57. **Prevent Uncoordinated Parallelization**: Don't run multiple AI agents without proper isolation, conflict detection, or resolution mechanisms.

58. **No Black Box Systems**: Don't build systems with minimal observability that prevent AI from understanding behavior and diagnosing issues.

59. **Avoid One-Size-Fits-All Tools**: Don't use the most powerful (expensive) AI models for simple tasks that could be handled by lighter alternatives.

60. **No Manual Policy Translation**: Don't manually translate compliance specifications when AI can generate consistent, testable policy code.

61. **Prevent Manual Evidence Collection**: Don't manually gather compliance evidence when AI can continuously collect and organize audit trails automatically.

62. **Avoid Monolithic AI Architecture**: Don't build large, coupled AI systems that violate Single Responsibility Principle and are difficult to test and maintain.

63. **No AI Without Contracts**: Don't integrate AI components without clear interface contracts, error handling specifications, and fallback mechanisms.

## Implementation Priority Framework

### Phase 1: Foundation (Weeks 1-2)
- Practices 1-4: Assessment, rules, security, progressive start
- Practices 41-47: Ethical AI boundaries, SOLID principles, Clean Architecture, DDD, Well-Architected principles
- Focus on team readiness, safe AI tool integration, and solid architectural foundations

### Phase 2: Development (Weeks 3-4)
- Practices 5-15: Workflows, testing, quality assurance
- Practices 38-42: AI ethics, bias detection, transparency, model monitoring, output validation
- Practices 48-49: Lean AI development and continuous integration for AI
- Establish systematic development and quality practices with ethical considerations

### Phase 3: Advanced Capabilities (Weeks 5-8)
- Practices 16-25: Parallel development, knowledge management, AI model lifecycle
- Practice 50: Chaos engineering for AI systems
- Scale to sophisticated multi-agent and context-aware development with resilience testing

### Phase 4: Operations & Tooling (Continuous)
- Practices 26-37: Tool design, automation, operations
- Mature operational capabilities and custom tooling with full lifecycle support

### Continuous: Version Control Security
- Practices 51-53: Signed commits, Trojan Source scanning, prompt injection prevention

### Continuous: Anti-Pattern Vigilance
- Practices 54-63: Ongoing awareness and prevention
- Maintain discipline against common failure modes in both AI and traditional development

## Success Metrics

### Foundation Success
- Zero credential leaks through proper AI tool sandboxing
- Consistent AI rule adherence across team members and projects
- Reduced onboarding time for new developers

### Development Success  
- >90% test coverage maintained for AI-generated code
- Faster feature delivery with maintained quality standards
- Reduced debugging time through observable development

### Operations Success
- Automated policy compliance verification and reporting
- Reduced deployment failures through AI-generated automation
- Proactive technical debt management and resolution

### AI Ethics & Governance Success
- Zero bias incidents detected through automated monitoring
- 100% AI decision transparency for user-facing features
- AI model performance within defined SLA thresholds (accuracy, latency, drift)
- Documented ethical AI constraints with measurable compliance metrics

# Software Development Matrix

| **Category**              | **Approaches / Principles**                                                                 |
|----------------------------|---------------------------------------------------------------------------------------------|
| **Principles**             | SOLID • KISS • DRY • YAGNI • Separation of Concerns • Convention over Configuration • Fail Fast • Design by Contract |
| **Code Quality & Design**  | Clean Code • Refactoring • TDD • BDD • DDD • Design Patterns • Anti-Patterns Awareness      |
| **Architectures**          | Layered / n-tier • Clean Architecture / Onion • Hexagonal (Ports & Adapters) • Microservices • Event-Driven • CQRS • Event Sourcing • Serverless |
| **Cloud & Platform Frameworks** | AWS Well-Architected Framework • Azure Well-Architected Framework • Google Cloud Architecture Framework • Cloud Native Computing Foundation (CNCF) • Platform Engineering |
| **Methodologies & Practices** | Extreme Programming (XP) • Kanban • Lean • Trunk-Based Development • Steel Thread • Pair Programming • Mob Programming |
| **Operations & Delivery**  | 12-Factor App • Continuous Integration • Continuous Delivery • Continuous Deployment • Feature Toggles • Infrastructure as Code (IaC) • DevOps • DevSecOps • Site Reliability Engineering (SRE) |
| **Techniques**             | Code Reviews • Prototyping / Spikes • Progressive Delivery (Canary, Blue/Green) • Chaos Engineering • Metrics & Observability |

---

*This canonical list of 63 practices represents distilled wisdom from extensive AI development experience, emphasizing security, ethics, quality, and systematic approaches over ad-hoc AI usage. These practices provide a comprehensive MECE framework for teams to adopt AI-assisted development safely and effectively while maintaining high standards for code quality, system reliability, and ethical AI governance.*
