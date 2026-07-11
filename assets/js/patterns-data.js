// AUTO-GENERATED FROM README.md - DO NOT EDIT BY HAND.
// Regenerate with: python3 scripts/generate-patterns-data.py
// README.md is the single source of record for all pattern content.
window.PATTERNS_DATA = {
  "repoUrl": "https://github.com/PaulDuvall/ai-development-patterns",
  "patternCount": 29,
  "categories": [
    {
      "id": "foundation",
      "name": "Foundation",
      "blurb": "Establish team readiness, security, and the basics of AI integration.",
      "accent": "#2d5a3f",
      "icon": "🟢",
      "count": 6
    },
    {
      "id": "development",
      "name": "Development",
      "blurb": "Daily workflows for AI-assisted coding, planning, and review.",
      "accent": "#b7950b",
      "icon": "🟡",
      "count": 17
    },
    {
      "id": "operations",
      "name": "Operations",
      "blurb": "CI/CD, security, compliance, and production management with AI.",
      "accent": "#c0392b",
      "icon": "🔴",
      "count": 6
    }
  ],
  "maturities": [
    "Beginner",
    "Intermediate",
    "Advanced"
  ],
  "lenses": [
    {
      "id": "harness-engineering-lens",
      "name": "Harness Engineering Lens",
      "shortDescription": "The Harness Engineering framing — Agent = Model + Harness — describes the controls built around a coding agent (separate from the model) to make its output trustworthy.",
      "bodyMarkdown": "The [Harness Engineering](https://martinfowler.com/articles/harness-engineering.html) framing — **`Agent = Model + Harness`** — describes the controls built *around* a coding agent (separate from the model) to make its output trustworthy. Harness Engineering isn't one of the patterns in this catalog; it's a *lens* over them — a way of grouping the patterns below and understanding *why* you'd use them together. Every control is one of two kinds and runs in one of two ways:\n\n- **Feedforward (guides)** steer the agent *before* it acts.\n- **Feedback (sensors)** observe *after* it acts so it can self-correct.\n- **Computational** controls are deterministic, fast, and reliable — linters, type checks, tests, fitness functions.\n- **Inferential** controls are semantic, slower, and probabilistic — AI review, LLM-as-judge.\n\nA healthy harness balances all four: feedforward-only agents never learn whether the rules worked; feedback-only agents repeat the same mistakes. The catalog maps onto the lens as follows.\n\n| Pattern | Direction | Execution | Regulates |\n|---------|-----------|-----------|-----------|\n| [Codified Rules](#codified-rules) / [Centralized Rules](#centralized-rules) | Feedforward | — | Conventions |\n| [Spec-Driven Development](#spec-driven-development) | Feedforward | — | Behaviour |\n| [Planned Implementation](#planned-implementation) | Feedforward | — | Approach |\n| [Custom Commands](#custom-commands) | Feedforward | — | Workflow |\n| [Agent Observability](#agent-observability) | Feedforward + Feedback | Computational + Inferential | Architecture fitness |\n| [Guided Refactoring](#guided-refactoring) | Feedback | Computational + Inferential | Maintainability |\n| [Adversarial Evaluator](#adversarial-evaluator) | Feedback | Inferential | Behaviour |\n| [Error Resolution](#error-resolution) | Feedback | Computational | Runtime |\n| [Agent Hooks](#agent-hooks) | Feedforward + Feedback | Computational | Workflow boundaries |\n| [Bounded Autonomy](#bounded-autonomy) | Feedforward + Feedback | Computational | Autonomous loops |\n\nTwo principles from the source are worth stating directly:\n\n- **Keep Quality Left** — run cheap, fast controls early (linters, basic review pre-commit) and reserve expensive ones (mutation testing, deep AI review) for later, so issues are caught where they cost least.\n- **Steer, don't automate** — when the agent repeats a mistake, improve the harness (the guides and sensors), not just the prompt. The human's job is to iterate on the harness.\n\n**Source**: Birgitta Böckeler, \"[Harness Engineering](https://martinfowler.com/articles/harness-engineering.html)\", martinfowler.com.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#harness-engineering-lens"
    },
    {
      "id": "loop-engineering-lens",
      "name": "Loop Engineering Lens",
      "shortDescription": "Most of this catalog treats a single AI task as the unit of work: write a prompt, get an output, review it. The Loop Engineering Lens zooms out.",
      "bodyMarkdown": "Most of this catalog treats a single AI task as the unit of work: write a prompt, get an output, review it. The **Loop Engineering Lens** zooms out. When you remove a human from the inner loop and let an agent iterate — read tool output, act, re-check, repeat — the *loop* becomes the thing you design, bound, and verify, not the task. Like the [Harness Engineering Lens](#harness-engineering-lens), this is a lens over the catalog, not a pattern to adopt. The two are complementary: Harness Engineering asks how *good* the controls around an agent are (the quality of its guides and sensors); Loop Engineering asks how much *autonomy* that control quality earns you, and how to bound the blast radius once no human inspects each iteration. Better verification reach buys more autonomy; weak verification caps it — no matter how capable the model.\n\nThree principles set the lens's dimensions:\n\n- **No executable done-check, no loop** — gate before you start. If \"done\" isn't a state a command can check (exit 0 or 1), and failure isn't cheaply reversible, run it interactively instead of looping.\n- **The test arbitrates, not the model** — one task per loop, deterministic verification, and the agent never certifies its own work. Producer ≠ grader: the thing that writes the code is never the thing that decides it's correct.\n- **Your verification reach sets the autonomy ceiling** — bound the loop with turn, spend, and stall/divergence limits; keep state in git; let humans own the upstream policy and the downstream merge.\n\n| Principle | What the loop must have | Catalog patterns that satisfy it |\n|-----------|-------------------------|----------------------------------|\n| No executable done-check, no loop | An observable goal, acceptance criteria written first, and cheap reversal | [Spec-Driven Development](#spec-driven-development), [Planned Implementation](#planned-implementation), [Agent Observability](#agent-observability); reversible failure via [Parallel Agents](#parallel-agents) worktrees |\n| The test arbitrates, not the model | Tight scope, an independent verifier, and checks wired to fire on every change | [Atomic Decomposition](#atomic-decomposition), [Adversarial Evaluator](#adversarial-evaluator), [Test Promotion](experiments/README.md#test-promotion), [Agent Hooks](#agent-hooks), [Autonomous Acceptance](experiments/README.md#autonomous-acceptance) |\n| Verification reach sets the autonomy ceiling | Hard bounds, state in git, and human-owned edges | [Bounded Autonomy](#bounded-autonomy), [Agent Memory](#agent-memory), [Long-Running Orchestration](experiments/README.md#long-running-orchestration), [Centralized Rules](#centralized-rules), [Handoff Protocols](experiments/README.md#handoff-protocols) |\n\nThe [Bounded Autonomy](#bounded-autonomy) pattern supplies the control layer that caps turns, spend, and time, detects stalls and divergence, and captures an in-loop diagnostic trail.\n\nTwo principles from the source are worth stating directly:\n\n- **The unit of work is the loop, not the task** — design, bound, and verify the loop as a whole. A single task is just one iteration of it; optimizing the task while leaving the loop unbounded is how runaway cost and silent drift happen.\n- **One writer per resource** — when loops fan out, canonicalize work-item keys *before* grouping so two agents never write the same file. Parallel loops corrupt state at the seams (collisions over a shared resource), not because any individual agent reasoned badly.\n\nThe detailed, tool-specific field checklist for gating, scoping, and bounding loops lives at [Loop Engineering Checklist](docs/loop-engineering-checklist.md).\n\n**Source**: Synthesis of the \"verification reach sets the autonomy ceiling\" idea with field practice for running autonomous coding loops; see the companion [Loop Engineering Checklist](docs/loop-engineering-checklist.md) for the operational form. Conceptually complementary to the [Harness Engineering Lens](#harness-engineering-lens) above, which addresses the quality of the controls this lens treats as the autonomy-setting constraint.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#loop-engineering-lens"
    },
    {
      "id": "lifecycle-lens",
      "name": "Lifecycle Lens",
      "shortDescription": "Most of this catalog reads like a menu: pick the patterns you need.",
      "bodyMarkdown": "Most of this catalog reads like a menu: pick the patterns you need. The **Lifecycle Lens** instead orders them along one feature's path from problem to production, so you can see which pattern does the work at each stage and where the handoffs happen. Like the [Harness Engineering Lens](#harness-engineering-lens) and [Loop Engineering Lens](#loop-engineering-lens), this is a lens over the catalog, not a pattern to adopt. The adoptable discipline — run the stages in order, don't skip ahead to code — lives in the [Developer Lifecycle](#developer-lifecycle) pattern; this lens is the map of which patterns carry each stage.\n\n| Stage | What it produces | Catalog patterns |\n|-------|------------------|------------------|\n| 1. Problem definition | A scoped problem statement and a readiness check | [Agent Readiness](#agent-readiness) |\n| 2-3. Plan & requirements | Architecture, tasks, and API specs | [Planned Implementation](#planned-implementation), [Issue Generation](#issue-generation) |\n| 4-5. Specifications & tests | Acceptance criteria written before any code | [Spec-Driven Development](#spec-driven-development) |\n| 6. Implementation | Working code in small, verifiable increments | [Atomic Decomposition](#atomic-decomposition), [Incremental Generation](#incremental-generation) |\n| 7. Testing & review | Test results, security scan, independent review | [Agent Observability](#agent-observability), [Adversarial Evaluator](#adversarial-evaluator) |\n| 8. Deployment | A shipped change | [Custom Commands](#custom-commands), [Agent Hooks](#agent-hooks) |\n| 9. Monitoring & correction | Runtime signals and human-approved fixes | [Agent Observability](#agent-observability), [Drift Remediation](#drift-remediation), [Error Resolution](#error-resolution) |\n\nRead top to bottom it is a feedforward chain: each stage's output is the next stage's input. The catalog's three categories ([Foundation](#foundation-patterns) -> [Development](#development-patterns) -> [Operations](#operations-patterns)) are the same arc at coarser grain; this lens is the per-feature zoom of it.\n\n**Source**: The nine-stage workflow from the [Developer Lifecycle](#developer-lifecycle) pattern, generalized into a mapping over the catalog. See [examples/developer-lifecycle/](examples/developer-lifecycle/) for a runnable end-to-end implementation.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#lifecycle-lens"
    }
  ],
  "dependencyDiagram": "graph TB\n    subgraph F[Foundation]\n        RDY[Agent Readiness] --> CR[Codified Rules] --> SS[Security Sandbox]\n        SS --> DL[Developer Lifecycle] --> TI[Tool Integration]\n        RDY --> IG[Issue Generation]\n    end\n\n    subgraph D[Development]\n        DL --> SD[Spec-Driven Development]\n        PI[Planned Implementation] --> INCR[Incremental Generation]\n        INCR --> AD[Atomic Decomposition] --> PA[Parallel Agents]\n        INCR --> AE[Adversarial Evaluator]\n        CR --> AM[Agent Memory] --> PD[Progressive Disclosure]\n        CR --> AH[Agent Hooks] --> CC[Custom Commands]\n        SD --> IS[Image Spec]\n        CR --> GR[Guided Refactoring]\n        DL --> AO[Agent Observability] --> ER[Error Resolution]\n        TI --> MR[Model Routing]\n        AM --> CRES[Code Research]\n        PA --> BA[Bounded Autonomy]\n    end\n\n    subgraph O[Operations]\n        SS --> PG[Policy Generation] --> EVA[Evidence Automation]\n        CR --> CZR[Centralized Rules]\n        AO --> DR[Drift Remediation]\n        GR --> DF[Debt Forecasting]\n        AO --> GC[Guided Chaos]\n    end\n\n    classDef foundation fill:#a8d5ba,stroke:#2d5a3f,stroke-width:2px,color:#1a3a25\n    classDef development fill:#f9e79f,stroke:#b7950b,stroke-width:2px,color:#7d6608\n    classDef operations fill:#f5b7b1,stroke:#c0392b,stroke-width:2px,color:#78281f\n    class RDY,CR,SS,DL,TI,IG foundation\n    class SD,PI,INCR,AD,PA,AE,AM,PD,AH,CC,IS,GR,AO,ER,MR,CRES,BA development\n    class PG,EVA,CZR,DR,DF,GC operations\n\n    click RDY \"https://github.com/PaulDuvall/ai-development-patterns#agent-readiness\"\n    click CR \"https://github.com/PaulDuvall/ai-development-patterns#codified-rules\"\n    click SS \"https://github.com/PaulDuvall/ai-development-patterns#security-sandbox\"\n    click DL \"https://github.com/PaulDuvall/ai-development-patterns#developer-lifecycle\"\n    click TI \"https://github.com/PaulDuvall/ai-development-patterns#tool-integration\"\n    click IG \"https://github.com/PaulDuvall/ai-development-patterns#issue-generation\"\n    click SD \"https://github.com/PaulDuvall/ai-development-patterns#spec-driven-development\"\n    click PI \"https://github.com/PaulDuvall/ai-development-patterns#planned-implementation\"\n    click INCR \"https://github.com/PaulDuvall/ai-development-patterns#incremental-generation\"\n    click AM \"https://github.com/PaulDuvall/ai-development-patterns#agent-memory\"\n    click AH \"https://github.com/PaulDuvall/ai-development-patterns#agent-hooks\"\n    click CC \"https://github.com/PaulDuvall/ai-development-patterns#custom-commands\"\n    click PD \"https://github.com/PaulDuvall/ai-development-patterns#progressive-disclosure\"\n    click AD \"https://github.com/PaulDuvall/ai-development-patterns#atomic-decomposition\"\n    click GR \"https://github.com/PaulDuvall/ai-development-patterns#guided-refactoring\"\n    click AO \"https://github.com/PaulDuvall/ai-development-patterns#agent-observability\"\n    click IS \"https://github.com/PaulDuvall/ai-development-patterns#image-spec\"\n    click AE \"https://github.com/PaulDuvall/ai-development-patterns#adversarial-evaluator\"\n    click PA \"https://github.com/PaulDuvall/ai-development-patterns#parallel-agents\"\n    click ER \"https://github.com/PaulDuvall/ai-development-patterns#error-resolution\"\n    click MR \"https://github.com/PaulDuvall/ai-development-patterns#model-routing\"\n    click CRES \"https://github.com/PaulDuvall/ai-development-patterns#code-research\"\n    click BA \"https://github.com/PaulDuvall/ai-development-patterns#bounded-autonomy\"\n    click PG \"https://github.com/PaulDuvall/ai-development-patterns#policy-generation\"\n    click EVA \"https://github.com/PaulDuvall/ai-development-patterns#evidence-automation\"\n    click CZR \"https://github.com/PaulDuvall/ai-development-patterns#centralized-rules\"\n    click DR \"https://github.com/PaulDuvall/ai-development-patterns#drift-remediation\"\n    click DF \"https://github.com/PaulDuvall/ai-development-patterns#debt-forecasting\"\n    click GC \"https://github.com/PaulDuvall/ai-development-patterns#guided-chaos\"",
  "siteDiagram": "graph LR\n  subgraph sg_foundation[\"Foundation\"]\n    direction TB\n    agent_readiness[\"Agent Readiness\"]\n    codified_rules[\"Codified Rules\"]\n    security_sandbox[\"Security Sandbox\"]\n    developer_lifecycle[\"Developer Lifecycle\"]\n    tool_integration[\"Tool Integration\"]\n    issue_generation[\"Issue Generation\"]\n  end\n  subgraph sg_development[\"Development\"]\n    direction TB\n    spec_driven_development[\"Spec-Driven Development\"]\n    planned_implementation[\"Planned Implementation\"]\n    incremental_generation[\"Incremental Generation\"]\n    agent_memory[\"Agent Memory\"]\n    agent_hooks[\"Agent Hooks\"]\n    custom_commands[\"Custom Commands\"]\n    progressive_disclosure[\"Progressive Disclosure\"]\n    atomic_decomposition[\"Atomic Decomposition\"]\n    guided_refactoring[\"Guided Refactoring\"]\n    agent_observability[\"Agent Observability\"]\n    image_spec[\"Image Spec\"]\n    adversarial_evaluator[\"Adversarial Evaluator\"]\n    parallel_agents[\"Parallel Agents\"]\n    error_resolution[\"Error Resolution\"]\n    model_routing[\"Model Routing\"]\n    code_research[\"Code Research\"]\n    bounded_autonomy[\"Bounded Autonomy\"]\n  end\n  subgraph sg_operations[\"Operations\"]\n    direction TB\n    policy_generation[\"Policy Generation\"]\n    evidence_automation[\"Evidence Automation\"]\n    centralized_rules[\"Centralized Rules\"]\n    drift_remediation[\"Drift Remediation\"]\n    debt_forecasting[\"Debt Forecasting\"]\n    guided_chaos[\"Guided Chaos\"]\n  end\n  agent_readiness --> codified_rules\n  codified_rules --> security_sandbox\n  codified_rules --> developer_lifecycle\n  security_sandbox --> developer_lifecycle\n  security_sandbox --> tool_integration\n  developer_lifecycle --> tool_integration\n  agent_readiness --> issue_generation\n  developer_lifecycle --> spec_driven_development\n  planned_implementation --> incremental_generation\n  codified_rules --> agent_memory\n  codified_rules --> agent_hooks\n  security_sandbox --> agent_hooks\n  agent_hooks --> custom_commands\n  spec_driven_development --> custom_commands\n  codified_rules --> progressive_disclosure\n  agent_memory --> progressive_disclosure\n  incremental_generation --> atomic_decomposition\n  codified_rules --> guided_refactoring\n  developer_lifecycle --> agent_observability\n  spec_driven_development --> image_spec\n  incremental_generation --> image_spec\n  incremental_generation --> adversarial_evaluator\n  atomic_decomposition --> parallel_agents\n  developer_lifecycle --> error_resolution\n  agent_observability --> error_resolution\n  tool_integration --> model_routing\n  agent_memory --> code_research\n  tool_integration --> code_research\n  parallel_agents --> bounded_autonomy\n  agent_observability --> bounded_autonomy\n  security_sandbox --> policy_generation\n  policy_generation --> evidence_automation\n  agent_observability --> evidence_automation\n  codified_rules --> centralized_rules\n  progressive_disclosure --> centralized_rules\n  agent_observability --> drift_remediation\n  bounded_autonomy --> drift_remediation\n  guided_refactoring --> debt_forecasting\n  tool_integration --> debt_forecasting\n  agent_observability --> guided_chaos\n  bounded_autonomy --> guided_chaos\n  classDef foundation fill:#e4f0e8,stroke:#2d5a3f,stroke-width:1.5px,color:#1a3a25,rx:4,ry:4;\n  classDef development fill:#f7efcf,stroke:#b7950b,stroke-width:1.5px,color:#5c4a00,rx:4,ry:4;\n  classDef operations fill:#f7e2df,stroke:#c0392b,stroke-width:1.5px,color:#78281f,rx:4,ry:4;\n  class agent_readiness,codified_rules,security_sandbox,developer_lifecycle,tool_integration,issue_generation foundation;\n  class spec_driven_development,planned_implementation,incremental_generation,agent_memory,agent_hooks,custom_commands,progressive_disclosure,atomic_decomposition,guided_refactoring,agent_observability,image_spec,adversarial_evaluator,parallel_agents,error_resolution,model_routing,code_research,bounded_autonomy development;\n  class policy_generation,evidence_automation,centralized_rules,drift_remediation,debt_forecasting,guided_chaos operations;\n  click agent_readiness openPatternFromDiagram \"Open Agent Readiness\"\n  click codified_rules openPatternFromDiagram \"Open Codified Rules\"\n  click security_sandbox openPatternFromDiagram \"Open Security Sandbox\"\n  click developer_lifecycle openPatternFromDiagram \"Open Developer Lifecycle\"\n  click tool_integration openPatternFromDiagram \"Open Tool Integration\"\n  click issue_generation openPatternFromDiagram \"Open Issue Generation\"\n  click spec_driven_development openPatternFromDiagram \"Open Spec-Driven Development\"\n  click planned_implementation openPatternFromDiagram \"Open Planned Implementation\"\n  click incremental_generation openPatternFromDiagram \"Open Incremental Generation\"\n  click agent_memory openPatternFromDiagram \"Open Agent Memory\"\n  click agent_hooks openPatternFromDiagram \"Open Agent Hooks\"\n  click custom_commands openPatternFromDiagram \"Open Custom Commands\"\n  click progressive_disclosure openPatternFromDiagram \"Open Progressive Disclosure\"\n  click atomic_decomposition openPatternFromDiagram \"Open Atomic Decomposition\"\n  click guided_refactoring openPatternFromDiagram \"Open Guided Refactoring\"\n  click agent_observability openPatternFromDiagram \"Open Agent Observability\"\n  click image_spec openPatternFromDiagram \"Open Image Spec\"\n  click adversarial_evaluator openPatternFromDiagram \"Open Adversarial Evaluator\"\n  click parallel_agents openPatternFromDiagram \"Open Parallel Agents\"\n  click error_resolution openPatternFromDiagram \"Open Error Resolution\"\n  click model_routing openPatternFromDiagram \"Open Model Routing\"\n  click code_research openPatternFromDiagram \"Open Code Research\"\n  click bounded_autonomy openPatternFromDiagram \"Open Bounded Autonomy\"\n  click policy_generation openPatternFromDiagram \"Open Policy Generation\"\n  click evidence_automation openPatternFromDiagram \"Open Evidence Automation\"\n  click centralized_rules openPatternFromDiagram \"Open Centralized Rules\"\n  click drift_remediation openPatternFromDiagram \"Open Drift Remediation\"\n  click debt_forecasting openPatternFromDiagram \"Open Debt Forecasting\"\n  click guided_chaos openPatternFromDiagram \"Open Guided Chaos\"",
  "patterns": [
    {
      "id": "agent-readiness",
      "name": "Agent Readiness",
      "maturity": "Beginner",
      "type": "Foundation",
      "category": "foundation",
      "shortDescription": "Evaluate codebase and team readiness for AI integration",
      "dependencies": [],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Issue Generation",
          "id": "issue-generation"
        }
      ],
      "bodyMarkdown": "**Description**: Systematic evaluation of codebase and team readiness for AI-assisted development before implementing AI patterns.\n\n\n**Source**: Factory.ai, \"[Agent Readiness](https://factory.ai/product/agent-readiness)\"; Kodus, \"[agent-readiness](https://github.com/kodustech/agent-readiness)\"; Guillaume Moigneu, \"[Making coding agents reliable](https://developer.upsun.com/posts/ai/making-coding-agents-reliable)\", February 17, 2026\n\nIndustry tooling commonly calls this practice *agent readiness* (Factory.ai, Kodus) or an *AI readiness assessment* (Microsoft).\n\n> 📋 **Quick start**: Use the free [AI Development Readiness Scorecard](https://www.redactedventures.com/scorecard) to score your team against this framework in about 10 minutes and get a tailored pattern adoption sequence.\n\n**Assessment Framework**\n\n```mermaid\ngraph TD\n    A[Codebase Assessment] --> B[Team Assessment]\n    B --> C[Infrastructure Assessment]\n    C --> D[Readiness Score]\n    D --> E[Implementation Plan]\n```\n\n**Codebase Readiness Checklist**\n```markdown\n## Code Quality Prerequisites\n□ Consistent code formatting and style guide\n□ Comprehensive test coverage (>80% for critical paths)\n□ Clear separation of concerns and modular architecture\n□ Documented APIs and interfaces\n□ Version-controlled configuration and secrets management\n\n## Documentation Standards\n□ README with setup and development instructions\n□ API documentation (OpenAPI/Swagger)\n□ Architecture decision records (ADRs)\n□ Coding standards and conventions documented\n□ Deployment and operational procedures\n```\n\n**Anti-pattern: Premature Adoption**\nStarting AI adoption without proper assessment leads to inconsistent practices, security vulnerabilities, and team frustration.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#agent-readiness"
    },
    {
      "id": "codified-rules",
      "name": "Codified Rules",
      "maturity": "Beginner",
      "type": "Foundation",
      "category": "foundation",
      "shortDescription": "Version and maintain AI coding standards as explicit configuration files",
      "dependencies": [
        {
          "name": "Agent Readiness",
          "id": "agent-readiness"
        }
      ],
      "related": [
        {
          "name": "Agent Readiness",
          "id": "agent-readiness"
        },
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        },
        {
          "name": "Progressive Disclosure",
          "id": "progressive-disclosure"
        },
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        },
        {
          "name": "Custom Commands",
          "id": "custom-commands"
        },
        {
          "name": "Centralized Rules",
          "id": "centralized-rules"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Version and maintain AI coding standards as explicit configuration files that persist across sessions and team members.\n\n\n**Source**: \"[AGENTS.md](https://agents.md/)\" open format specification (OpenAI, Google Jules, Cursor, Factory); Cursor, \"[Rules](https://cursor.com/docs/rules)\" documentation\n\nIndustry tooling implements this pattern as `AGENTS.md` (open format stewarded under the Linux Foundation), *Rules* (Cursor), `CLAUDE.md` memory (Anthropic Claude Code), and *repository custom instructions* (GitHub Copilot).\n\n**Standardized Project Structure**\n```bash\nproject/\n├── .ai/                          # AI configuration directory\n│   ├── rules/                    # Modular rule sets\n│   │   ├── security.md          # Security standards\n│   │   ├── testing.md           # Testing requirements\n│   │   ├── style.md             # Code style guide\n│   │   └── architecture.md      # Architectural patterns\n│   ├── prompts/                 # Reusable prompt templates\n│   │   ├── implementation.md    # Implementation prompts\n│   │   ├── review.md            # Code review prompts\n│   │   └── testing.md           # Test generation prompts\n│   └── knowledge/               # Captured patterns and gotchas\n│       ├── successful.md        # Proven successful patterns\n│       └── failures.md          # Known failure patterns\n├── .cursorrules                 # Cursor IDE configuration\n├── CLAUDE.md                    # Claude Code session context\n└── .windsurf/                   # Windsurf configuration\n    └── rules.md\n```\n\n**Complete Example**: See [examples/codified-rules/](examples/codified-rules/) for:\n- Comprehensive development workflow rules and standards\n- Pipeline automation and CI/CD rules\n- Code quality standards and enforcement guidelines\n- Claude Code configuration for rules-as-code implementation\n\n**Anti-pattern: Broken Context**\nEach developer maintains their own prompts and preferences, leading to inconsistent code across the team.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#codified-rules"
    },
    {
      "id": "security-sandbox",
      "name": "Security Sandbox",
      "maturity": "Beginner",
      "type": "Foundation",
      "category": "foundation",
      "shortDescription": "Run AI tools in isolated environments without access to secrets or sensitive data",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        }
      ],
      "related": [
        {
          "name": "Security & Compliance Patterns",
          "id": "security--compliance-patterns"
        },
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        }
      ],
      "bodyMarkdown": "**Description**: Run AI tools in isolated environments without access to secrets or sensitive data to prevent credential leaks and maintain security compliance.\n\n\n**Source**: Anthropic, \"[sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime)\"; Anthropic, \"[Sandboxing](https://code.claude.com/docs/en/sandboxing)\" (Claude Code documentation)\n\n**Core Security Implementation**\n\n**Claude Code Users**: Use the `/sandbox` command to instantly create isolated environments without manual Docker configuration:\n```bash\n/sandbox\n# Creates a secure, isolated environment with:\n# - No access to credentials or sensitive files\n# - Restricted network access\n# - Controlled file system permissions\n```\n\n**Docker-Based Implementation**: For custom isolation or multi-agent scenarios:\n```yaml\n# Basic AI isolation with complete network isolation\nservices:\n  ai-development:\n    network_mode: none                    # Zero network access\n    cap_drop: [ALL]                       # No system privileges\n    volumes:\n      - ./src:/workspace/src:ro           # Read-only source code\n      # DO NOT mount ~/.aws, .env, secrets/, etc.\n```\n\n**Complete Example**: See [examples/security-sandbox/](examples/security-sandbox/) for:\n- Complete Docker isolation configurations for single and multi-agent setups\n- Resource locking and emergency shutdown procedures\n- Security monitoring and violation detection\n- Multi-agent coordination with conflict resolution\n\n**Production Implementations**\n\nModern AI development platforms provide enterprise-grade implementations of these security controls:\n\n**Cloud-Based Sandboxes**:\n- **[Claude Code for the web](https://www.claude.ai/code)**: Sandboxed AI coding with isolated execution environments\n- **[Google Jules](https://jules.google/)**: Google's AI coding assistant with secure development environments\n- **[OpenAI Codex](https://chatgpt.com/codex)**: Cloud-based AI coding with secure execution environments\n- **[Google Vertex AI Agent Engine Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution)**: Managed secure runtimes for AI agent code execution\n- **[GitHub Codespaces](https://docs.github.com/en/codespaces/overview)**: Isolated cloud development VMs with configurable security policies\n- **[E2B](https://e2b.dev)**: Specialized AI agent sandboxes with microVM isolation\n\n**Cloud & Self-Hosted Options**:\n- **[Daytona](https://www.daytona.io)**: microVM-based isolation for development environments (available as cloud service or self-hosted)\n- **[Coder](https://coder.com)**: Cloud development environments with enterprise security controls (available as cloud service or self-hosted)\n\n**Anti-pattern: Unrestricted Access**\nAllowing AI tools full system access risks credential leaks, data breaches, and security compliance violations.\n\n**Anti-pattern: Conflicting Workspaces**\nAllowing multiple parallel agents to write to the same directories creates race conditions, file conflicts, and unpredictable behavior that can corrupt the development environment.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#security-sandbox"
    },
    {
      "id": "developer-lifecycle",
      "name": "Developer Lifecycle",
      "maturity": "Intermediate",
      "type": "Workflow",
      "category": "foundation",
      "shortDescription": "Take one feature from problem to production through a staged, plan-first discipline",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        }
      ],
      "related": [
        {
          "name": "Lifecycle Lens",
          "id": "lifecycle-lens"
        },
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        },
        {
          "name": "Planned Implementation",
          "id": "planned-implementation"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Atomic Decomposition",
          "id": "atomic-decomposition"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        }
      ],
      "bodyMarkdown": "**Description**: A staged, plan-first discipline for taking a single feature from problem to production with AI assistance.\n\n\n**Source**: GitHub, \"[Spec Kit](https://github.com/github/spec-kit)\"; AWS DevOps & Developer Productivity Blog, \"[AI-Driven Development Life Cycle: Reimagining Software Engineering](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)\", July 31, 2025\n\nThis pattern is the per-feature discipline: plan before you generate, and stop retrying a failing approach after a few tries instead of looping on it. For how each stage maps onto the rest of the catalog, see the [Lifecycle Lens](#lifecycle-lens).\n\n**Workflow Interaction Sequence**\n\n```mermaid\nsequenceDiagram\n    participant D as Developer\n    participant AI as AI Assistant\n    participant S as System/CI\n    participant T as Tests\n    participant M as Monitoring\n    \n    Note over D,M: Stage 1-3: Problem → Plan → Requirements\n    D->>AI: Problem Definition (e.g., JWT Authentication)\n    AI->>D: Technical Architecture Plan\n    D->>AI: Requirements Clarification\n    AI->>D: API Specs + Kanban Tasks + Security Requirements\n    \n    Note over D,M: Stage 4-5: Issues → Specifications\n    D->>AI: Generate Executable Tests\n    AI->>T: Gherkin Scenarios + API Tests + Security Tests\n    T->>D: Test Suite Ready (Performance Criteria: <200ms)\n    \n    Note over D,M: Stage 6: Implementation\n    D->>AI: Implement Following Specifications\n    AI->>S: Code + Tests + Error Handling + Logging\n    S->>D: Implementation Results\n    \n    Note over D,M: Stage 7-9: Testing → Deployment → Monitoring\n    D->>S: Run All Tests\n    S->>D: Test Results + Security Scan + Performance Benchmark\n    alt Tests Pass\n        S->>S: Deploy to Production\n        S->>M: Setup Monitoring Alerts\n        M->>D: Deployment Complete + Monitoring Active\n    else Tests Fail\n        S->>D: Failure Report\n        D->>AI: Fix Issues\n        AI->>S: Updated Implementation\n    end\n    \n    Note over D,M: Continuous Monitoring\n    M->>D: Performance Alerts + Security Events\n```\n\n**Complete Implementation**: See [examples/developer-lifecycle/](examples/developer-lifecycle/) for full 9-stage workflow scripts, detailed prompts for each stage, enhanced implementation techniques ([Five-Try Rule](https://www.linkedin.com/posts/jessicakerr_the-implementation-is-a-test-of-the-design-activity-7367649800193761281-LzCu/), markdown iteration, function decomposition), and integration with CI/CD pipelines.\n\n**Anti-pattern: Unplanned Development**\nJumping straight to coding with AI without proper planning, requirements, or testing strategy. Also avoid continuing with the same AI approach after 3-4 failures without decomposing the problem or changing strategy.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#developer-lifecycle"
    },
    {
      "id": "tool-integration",
      "name": "Tool Integration",
      "maturity": "Intermediate",
      "type": "Foundation",
      "category": "foundation",
      "shortDescription": "Connect AI systems to external data, APIs, and tools",
      "dependencies": [
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        },
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        }
      ],
      "related": [
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        },
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        }
      ],
      "bodyMarkdown": "**Description**: Connect AI systems to external data sources, APIs, and tools for enhanced capabilities beyond prompt-only interactions.\n\n\n**Source**: Anthropic, \"[Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)\", November 25, 2024; Model Context Protocol, \"[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)\" reference servers\n\nThe industry implements this pattern as *tool use* (Anthropic), *function calling* (OpenAI), and the *Model Context Protocol (MCP)*.\n\n**Core Concept**\n\nModern AI development requires more than chat-based interactions. AI systems become significantly more capable when connected to real-world data sources and tools. This pattern demonstrates the architectural shift from isolated prompt-only AI to tool-augmented AI systems.\n\n**Implementation Overview**\n\n```python\n# Core tool-augmented AI system with security controls\nclass ToolAugmentedAI:\n    def __init__(self, config_path: str = \".ai/tools.json\"):\n        self.available_tools = {\n            \"database_query\": self._query_database,     # Read-only SQL queries\n            \"file_operations\": self._file_operations,   # Controlled file access\n            \"api_requests\": self._api_requests,         # Allowlisted HTTP requests\n            \"system_info\": self._system_info            # Safe system information\n        }\n    \n    def execute_with_tools(self, ai_request: str, tool_calls: list) -> dict:\n        \"\"\"Execute AI request with secure tool access\"\"\"\n        # Process tool calls with security validation\n        # Return structured results with error handling\n```\n\n**Tool Categories & Security**\n\n- **Database Access**: Read-only queries with operation whitelisting (`SELECT`, `WITH` only)\n- **File Operations**: Path-restricted read/write within configured directories\n- **API Integration**: HTTP requests limited to allowlisted domains with timeouts\n- **System Information**: Safe environment data without sensitive details\n\n**Configuration Example**\n```json\n{\n  \"allowed_apis\": [\"api.github.com\", \"api.openweathermap.org\"],\n  \"file_access_paths\": [\"./data/\", \"./logs/\", \"./generated/\"],\n  \"max_query_results\": 100,\n  \"security\": {\n    \"read_only_database\": true,\n    \"api_rate_limits\": true,\n    \"file_size_limits\": \"10MB\"\n  }\n}\n```\n\n**Model Context Protocol (MCP) Integration**\n\nThis pattern can be implemented using [Anthropic's Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) for standardized tool integration across AI systems:\n\n```json\n{\n  \"mcp_servers\": {\n    \"filesystem\": {\n      \"command\": \"npx\",\n      \"args\": [\"@modelcontextprotocol/server-filesystem\", \"./data\"]\n    },\n    \"sqlite\": {\n      \"command\": \"npx\",\n      \"args\": [\"@modelcontextprotocol/server-sqlite\", \"app_data.db\"]\n    }\n  }\n}\n```\n\n**What [Tool Integration](#tool-integration) Enables**\n\n- **Real-time data access**: AI queries current database state, not training data\n- **File system interaction**: Read logs, write generated code, manage project files\n- **API integration**: Fetch live data from external services and APIs\n- **System awareness**: Access to current environment state and configuration\n- **Enhanced context**: AI decisions based on actual system state, not assumptions\n\n**Complete Implementation**\n\nSee [examples/tool-integration/](examples/tool-integration/) for:\n- Full Python implementation with security controls\n- Configuration examples and MCP integration\n- Usage patterns and deployment guidelines\n- Integration with [Security Sandbox](#security-sandbox)\n\n**Anti-pattern: Disconnected Prompting**\nAttempting to solve complex data analysis, system integration, or real-time problems using only natural language prompts without providing AI access to actual data sources, APIs, or system tools. This leads to hallucinated responses, outdated information, and inability to interact with real systems.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#tool-integration"
    },
    {
      "id": "issue-generation",
      "name": "Issue Generation",
      "maturity": "Intermediate",
      "type": "Foundation",
      "category": "foundation",
      "shortDescription": "Generate flow-sized work items with acceptance criteria and dependencies",
      "dependencies": [
        {
          "name": "Agent Readiness",
          "id": "agent-readiness"
        }
      ],
      "related": [
        {
          "name": "Agent Readiness",
          "id": "agent-readiness"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        }
      ],
      "bodyMarkdown": "**Description**: Generate small, deployable work items (<1 hour with AI assistance) from requirements using AI to ensure continuous delivery with clear acceptance criteria and dependency tracking.\n\n**Methodology Note**: This pattern aligns well with Kanban principles (continuous flow, small batches) but works with any development methodology including Scrum, Scrumban, or ad-hoc workflows.\n\n\n**Source**: GitHub Docs, \"[Using GitHub Copilot to create issues](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-to-create-issues)\"; Eyal Toledano, \"[Task Master](https://github.com/eyaltoledano/claude-task-master)\"\n\n**[Issue Generation](#issue-generation) Framework**\n\n```mermaid\ngraph TD\n    A[Requirements Document] --> B[AI Feature Analysis]\n    B --> C[Work Item Splitting]\n    C --> D{<1 hour?}\n    D -->|No| E[Split Further]\n    E --> C\n    D -->|Yes| F[Story Generation]\n    F --> G[Acceptance Criteria]\n    G --> H[Cycle Time Target]\n    H --> I[Dependency Mapping]\n    I --> J[Work Item Creation]\n```\n\n**Core Principles**\n\n- **Small Batch Sizing**: Each work item sized to complete in under an hour with AI assistance, enabling continuous delivery and rapid feedback\n- **AI-Assisted Decomposition**: Use AI to break down requirements into implementable tasks\n- **Traceability Integration**: Connect issues to implementation files and CI workflows\n- **Dependency Mapping**: Establish clear relationships between work items and epics\n- **Acceptance-Driven**: Each task includes specific, testable acceptance criteria\n\n**Work Item Attributes**\n\nGenerated issues must include:\n- **Title**: Specific, actionable description of the work\n- **Cycle Time Target**: Estimated completion time (<1 hour with AI assistance)\n- **Acceptance Criteria**: Testable conditions for completion\n- **File Scope**: Which files will be added, updated, or removed\n- **CI Requirements**: Test coverage, pipeline steps, quality gates\n- **Dependencies**: Blocking and enabling relationships with other issues\n\n**Epic Relationship Management**\n\n- **Bidirectional Linking**: Parent-child references maintained automatically\n- **Progress Tracking**: Epic completion calculated from subissue status\n- **Dependency Validation**: Automated checking for circular dependencies\n- **Status Propagation**: Subissue changes update epic progress\n\n**Implementation Examples**: See [examples/issue-generation/](examples/issue-generation/) for detailed AI prompts, epic breakdown workflows, CI integration patterns, and traceability implementations. For AI-first workflows, see [Beads guide](examples/issue-generation/beads-guide.md) - a git-native issue tracker with CLI access and persistent agent memory.\n\n> \"Small, frequent deliveries expose issues early and keep teams aligned.\"\n> – Agile Alliance\n\n**Kanban Context**: This pattern embodies Kanban principles of continuous flow and small batch sizes. If using Kanban: \"If a task takes more than one day, split it.\" (Kanban Guide, Lean Kanban University). However, the pattern works equally well with Scrum sprints, continuous delivery, or any methodology that values incremental progress.\n\n**Anti-pattern: Under-Specified Issues**\nCreating generic tasks without specific acceptance criteria, proper sizing, or clear dependencies leads to scope creep and estimation errors.\n\n**Anti-pattern: Broken Integration**\nCreating issues without CI workflow integration, file tracking, or traceability requirements leads to disconnected development cycles and poor visibility into implementation progress.\n\n**Anti-pattern Examples:**\n```markdown\n❌ \"Fix the login page\"\n❌ \"Make the dashboard better\"\n❌ \"Add some tests\"\n❌ \"AUTH-002: Implement password validation\" (no file tracking or CI requirements)\n\n✅ \"Add OAuth 2.0 token validation endpoint (<1 hour with AI)\"\n✅ \"Implement dashboard metric WebSocket connection (45 minutes)\"\n✅ \"Write unit tests for user service login method (30 minutes)\"\n✅ \"AUTH-002: Password validation service with CI integration\"\n   - Files: src/auth/validators.py, tests/test_validators.py\n   - Coverage: 95%, unit + integration tests\n   - CI: lint, test, security-scan must pass\n   - AI-assisted: Use AI for implementation and test generation\n```",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#issue-generation"
    },
    {
      "id": "spec-driven-development",
      "name": "Spec-Driven Development",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Guide code generation with executable specifications and acceptance criteria",
      "dependencies": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        }
      ],
      "related": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        },
        {
          "name": "Custom Commands",
          "id": "custom-commands"
        },
        {
          "name": "Image Spec",
          "id": "image-spec"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Use executable specifications to guide AI code generation with clear acceptance criteria before implementation.\n\n**Core Principle: Precision Enables Productivity**\n\nSpecDriven AI combines three key elements:\n- **Machine-readable specifications** with unique identifiers and authority levels\n- **Rigorous Test-Driven Development** with coverage tracking and automated validation\n- **AI-powered implementation** with persistent context through structured specifications\n\n**Key Innovation: Authority Level System**\n\nSpecifications use authority levels to resolve conflicts and establish precedence:\n- **`authority=system`**: Core business logic and security requirements (highest precedence)\n- **`authority=platform`**: Infrastructure and technical architecture decisions  \n- **`authority=feature`**: User interface and experience requirements (lowest precedence)\n\nWhen requirements conflict, higher authority levels take precedence, enabling clear decision-making for AI implementation.\n\n\n**Source**: GitHub, \"[Spec Kit](https://github.com/github/spec-kit)\"; Birgitta Böckeler, \"[Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)\", October 15, 2025\n\n**SpecDriven AI Workflow**\n\n```mermaid\ngraph TD\n    A[Machine-Readable Specifications<br/>with Authority Levels] --> B[Coverage Tracking<br/>& Validation]\n    B --> C[AI Implementation<br/>with Ephemeral Prompts]\n    C --> D[Automated Testing<br/>& Compliance Check]\n    D --> E{Specs Pass?}\n    E -->|No| F[Refine Prompts<br/>Not Specs]\n    F --> C\n    E -->|Yes| G[Coverage Report<br/>& Deployment]\n    G --> H[Specification Persistence<br/>for Regression]\n    \n    style A fill:#e1f5e1\n    style B fill:#e1f5e1\n    style H fill:#e1f5e1\n    style C fill:#ffe6e6\n    style F fill:#ffe6e6\n```\n\n**Core Implementation**\n\n**Machine-Readable Specification with Authority Levels**\n```markdown\n# IAM Policy Generator Specification {#iam_policy_gen}\n\n## CLI Requirements {#cli_requirements authority=system}\nThe system MUST provide a command-line interface that:\n- Accepts policy type via `--policy-type` flag\n- Validates input parameters against AWS IAM constraints\n- Generates syntactically correct IAM policy JSON [^test_iam_syntax]\n- Returns exit code 0 for success, 1 for validation errors\n\n## Input Validation {#input_validation authority=platform}  \nThe system MUST:\n- Reject invalid AWS service names with clear error messages\n- Validate resource ARN format before policy generation\n- Implement rate limiting for API calls [^test_rate_limit]\n\n[^test_iam_syntax]: tests/test_iam_policy_syntax.py\n[^test_rate_limit]: tests/test_rate_limiting.py\n```\n\n**Automated Coverage Tracking**\n```bash\n# Run specification compliance validation\npytest --cov=src --cov-report=html --spec-coverage\npython spec_validator.py --check-coverage --authority-conflicts\n\n# Output shows specification coverage\n# Specification Coverage Report:\n# ✅ cli_requirements: 100% (3/3 tests linked)\n# ✅ input_validation: 85% (6/7 tests linked) \n# ⚠️  Missing test: [^test_malformed_arn] in line 23\n```\n\n**Tooling Integration**\n\n```bash\n# Pre-commit hook validates specification compliance\n# .pre-commit-config.yaml\nrepos:\n  - repo: local\n    hooks:\n      - id: spec-coverage\n        name: Specification Coverage Check\n        entry: python spec_validator.py --check-coverage\n        language: python\n        pass_filenames: false\n\n# Git workflow with specification traceability  \ngit commit -m \"feat: implement rate limiting [spec:rl2c]\n  \nImplements rate limiting requirement from input_validation\nsection. Closes specification anchor #failed_auth.\n\nCoverage: 94% (31/33 spec requirements covered)\"\n```\n\n**Key Benefits**\n- **Authority-based conflict resolution** prevents requirement ambiguity\n- **Automated coverage tracking** ensures no specifications are missed\n- **AI tool independence** through persistent, machine-readable requirements\n- **Precise traceability** from specification anchors to test implementations\n- **Living documentation** that evolves with the system\n\n**Automated Traceability**\n\nSpecification anchors (`{#cli_requirements}`) and test footnotes (`[^test_iam_syntax]`) are the link layer that ties requirements to tests to code to docs. Maintain those links automatically on every change instead of in a spreadsheet:\n\n```bash\n# After each commit, validate anchor coverage and flag drift\ngit diff --name-only HEAD~1 | while read file; do\n    ai \"For $file: confirm referenced spec anchors still exist, propose new\n        anchor links for any uncovered behavior, and emit an impact list of\n        which downstream tests and docs need updating.\"\ndone\n```\n\nWhen a spec section moves or a test is renamed, the same loop surfaces the broken link before it ships. The result is a living traceability graph that stays accurate without manual upkeep — the alternative (traceability in a spreadsheet) is stale within a week.\n\n**Anti-pattern: Broken Traceability**\nMaintaining requirement-to-test links in spreadsheets or manual documentation that becomes stale and inaccurate within days of being written.\n\n**Complete Implementation**\n\nSee [examples/spec-driven-development/](examples/spec-driven-development/) for:\n- Complete IAM Policy Generator implementation\n- spec_validator.py tool for automated compliance checking\n- Pre-commit hooks and Git workflow integration\n- Full specification examples with authority levels\n- Coverage tracking and reporting tools\n\n**Anti-pattern: Spec-Ignored**\nWriting code with AI first, then trying to retrofit tests, resulting in tests that mirror implementation rather than specify behavior.\n\n**Anti-pattern: Over-Prompting**\nSaving collections of prompts as if they were specifications. Prompts are implementation details; specifications are behavioral contracts.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#spec-driven-development"
    },
    {
      "id": "planned-implementation",
      "name": "Planned Implementation",
      "maturity": "Beginner",
      "type": "Development",
      "category": "development",
      "shortDescription": "Interview, constrain, and plan before writing code",
      "dependencies": [],
      "related": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        },
        {
          "name": "Adversarial Evaluator",
          "id": "adversarial-evaluator"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Interview, constrain, and plan before writing code so AI implementation matches actual requirements instead of confident-sounding assumptions.\n\n\n**Source**: Cursor, \"[Plan Mode](https://cursor.com/docs/agent/plan-mode)\" documentation; Anthropic, \"[Claude Code best practices](https://code.claude.com/docs/en/best-practices)\"\n\nIndustry tooling commonly implements the planning half of this pattern as *plan mode* (Cursor, Claude Code).\n\n**Core Principle: Think Before You Code**\n\nThe costliest bugs come from building the wrong thing, not building it wrong. This pattern front-loads three activities before any code is written:\n\n1. **Interview** — have AI ask structured questions to surface tacit knowledge, hidden constraints, and decisions that would otherwise emerge mid-implementation.\n2. **Constrain** — translate the interview answers into explicit boundaries the AI must respect (line counts, dependencies, performance budgets, prohibited approaches).\n3. **Plan** — generate an explicit step-by-step implementation plan, review it, and iterate before any code is generated.\n\n**Planning Workflow**\n\n```mermaid\ngraph TD\n    A[Idea or Request] --> B[AI Interviews You<br/>Clarifying Questions]\n    B --> C{Gaps Remain?}\n    C -->|Yes| B\n    C -->|No| D[Define Explicit Constraints<br/>Line count, deps, perf budget]\n    D --> E[Generate Initial Plan]\n    E --> F[Review & Refine Plan]\n    F --> G{Plan Approved?}\n    G -->|No| E\n    G -->|Yes| H[Execute Implementation]\n    H --> I[Validate Against Plan]\n    I --> J{Meets Plan?}\n    J -->|No| H\n    J -->|Yes| K[Complete]\n\n    style B fill:#e1f5e1\n    style D fill:#e1f5e1\n    style F fill:#e1f5e1\n    style H fill:#ffe6e6\n    style K fill:#e1f5e1\n```\n\n**Interview Phase**\n\nBefore writing any plan, have AI act as an interviewer:\n\n```bash\nai \"I want to build a notification system for our app.\n\nBefore writing any code or plan, interview me:\n1. Ask clarifying questions about requirements I haven't stated\n2. Identify constraints I should decide on upfront\n3. Surface assumptions that could cause rework later\n4. Group your questions by category (scope, technical, users, edge cases)\n\nAsk one category at a time. Wait for my answers before continuing.\"\n```\n\nTypical interview output groups questions by category — scope (\"Which channels? In-app, email, SMS?\"), technical (\"Expected volume — 10/day vs 10,000/hour changes architecture\"), users (\"Can users configure preferences?\"), edge cases (\"What happens when delivery fails?\"). After answers are collected, ask AI to consolidate them into a requirements summary, an explicit non-goals list, and remaining open questions — that document becomes the input to the planning phase.\n\n**Constraint Phase**\n\nTranslate the interview answers into the boundaries the AI must respect. Constraints prevent over-engineering more reliably than instructions to \"keep it simple\":\n\n```\nBad:  \"Create user service\"\nGood: \"Create user service: <100 lines, 3 methods max, only bcrypt dependency\"\n\nBad:  \"Add caching\"\nGood: \"Add caching using Map, max 1000 entries, LRU eviction\"\n\nBad:  \"Improve performance\"\nGood: \"Reduce p99 latency to <50ms without new dependencies\"\n```\n\nCarry these constraints into every subsequent prompt — they're the steering, not the suggestion.\n\n**Core Implementation**\n\n**1. Plan Generation Phase**\n```bash\n# Example planning prompt structure\nCONTEXT: \"Building user authentication for SaaS application\"\nREQUIREMENTS: \"JWT tokens, password reset, rate limiting\"\nCONSTRAINTS: \"Must integrate with existing user table, 2-hour time limit\"\n\nREQUEST: \"Generate step-by-step implementation plan with:\n- Database changes needed\n- API endpoints to create/modify\n- Security considerations\n- Testing approach\n- Rollback strategy\"\n```\n\n**2. Plan Review and Iteration**\n```markdown\n# Generated Plan Review Checklist\n\n### Technical Approach\n- [ ] Database schema changes are backwards compatible\n- [ ] API design follows existing conventions\n- [ ] Security measures address OWASP top 10\n- [ ] Performance impact is minimal\n\n### Implementation Strategy\n- [ ] Tasks are broken into deployable increments\n- [ ] Dependencies are clearly identified\n- [ ] Rollback plan is feasible\n- [ ] Testing strategy covers edge cases\n\n### Resource Requirements\n- [ ] Time estimate is realistic\n- [ ] Required permissions are available\n- [ ] External dependencies are identified\n```\n\n**3. Execution with Plan Validation**\n```bash\n# During implementation, validate against plan\necho \"✓ Step 1: Created user_sessions table (matches plan)\"\necho \"✓ Step 2: Added JWT service (matches plan)\"\necho \"⚠ Step 3: Rate limiting - using Redis instead of in-memory (plan deviation documented)\"\n```\n\n**Tool-Agnostic Planning Approach**\n\n**Planning Session Structure**\n```markdown\n## 1. Problem Definition (2-3 sentences)\nClear statement of what needs to be built and why\n\n## 2. Constraints & Requirements\n- Technical constraints (existing systems, performance, security)\n- Business requirements (timeline, user experience, compliance)\n- Resource constraints (team size, expertise, budget)\n\n## 3. Implementation Options\n- Option A: [Brief description, pros/cons, time estimate]\n- Option B: [Brief description, pros/cons, time estimate]\n- Recommended: [Choice with justification]\n\n## 4. Detailed Plan\n- [ ] Step 1: [Concrete action with acceptance criteria]\n- [ ] Step 2: [Concrete action with acceptance criteria]\n- [ ] Step 3: [Concrete action with acceptance criteria]\n\n## 5. Validation Strategy\nHow to verify each step works and overall solution meets requirements\n```\n\n\n**When to Use Plan-First Development**\n\n- **Complex Features**: Multi-step implementations requiring coordination\n- **Unknown Domains**: Working in unfamiliar technologies or business areas\n- **Team Collaboration**: When multiple developers need to understand the approach\n- **High-Stakes Changes**: Security, performance, or business-critical modifications\n- **Learning Contexts**: When using AI to explore new implementation approaches\n\n**Complete Implementation**\n\nSee [examples/planned-implementation/](examples/planned-implementation/) for:\n- Tool-specific planning examples (Claude Code, Cursor)\n- Planning templates and checklists\n- Markdown iteration techniques and stakeholder review cycles\n- Integration with existing development workflows\n- Plan validation and iteration strategies\n\n**Anti-pattern: Blind Generation**\nJumping straight from a vague idea to code generation without interviewing for requirements or setting constraints. AI fills the gaps with assumptions — often reasonable-sounding but wrong for your context — and you discover requirements through failed implementations instead of conversation.\n\n**Anti-pattern: Unconstrained Generation**\nSkipping the constraint phase. Telling AI to \"make it good\" or \"add features\" without explicit boundaries produces over-engineered solutions that are hard to review.\n\n**Anti-pattern: Over-Constrained**\nStacking so many constraints (\"exactly 50 lines, 2 methods, no dependencies, 100% test coverage, sub-10ms response time\") that AI can't find a coherent solution. Constraints are budgets, not handcuffs — pick the ones that matter for this task.\n\n**Anti-pattern: Over-Analysis**\nSpending excessive time refining plans without moving to implementation, missing opportunities for rapid feedback and iterative improvement.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#planned-implementation"
    },
    {
      "id": "incremental-generation",
      "name": "Incremental Generation",
      "maturity": "Beginner",
      "type": "Development",
      "category": "development",
      "shortDescription": "Build complex features through small, deployable iterations",
      "dependencies": [
        {
          "name": "Planned Implementation",
          "id": "planned-implementation"
        }
      ],
      "related": [
        {
          "name": "Planned Implementation",
          "id": "planned-implementation"
        },
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Image Spec",
          "id": "image-spec"
        },
        {
          "name": "Adversarial Evaluator",
          "id": "adversarial-evaluator"
        }
      ],
      "bodyMarkdown": "**Description**: Build complex features through small, deployable iterations rather than big-bang generation.\n\n\n**Source**: GitHub Docs, \"[Prompt engineering for GitHub Copilot Chat](https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering)\"; Harper Reed, \"[My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/)\", February 16, 2025\n\nIndustry sources describe this mechanism as small tasks, bite-sized steps, or incremental\ndevelopment. This catalog uses *incremental generation* to avoid collision with the established\nweb-design meaning of *progressive enhancement*.\n\n**Examples**\nBuilding authentication incrementally:\n```bash\n# Day 1: Minimal login\n\"Create POST /login that returns 200 for admin/admin, 401 otherwise\"\n→ Deploy\n\n# Day 2: Real password check\n\"Modify login to check passwords against users table. Keep existing API.\"\n→ Deploy\n\n# Day 3: Add security\n\"Add bcrypt hashing to login. Support both hashed and plain passwords temporarily.\"\n→ Deploy\n\n# Day 4: Modern tokens\n\"Replace session with JWT. Keep session endpoint for backward compatibility.\"\n→ Deploy\n```\n\n**Developer Review Required**: Each iteration requires developer review and testing of AI-generated code before deployment.\n\n**When to Use [Incremental Generation](#incremental-generation)**\n\n- **MVP Development**: When you need to get to market quickly with minimal features\n- **Uncertain Requirements**: When requirements are likely to change based on user feedback  \n- **Risk Mitigation**: When you want to reduce the risk of large, complex implementations\n- **Continuous Delivery**: When you have automated deployment and want rapid iterations\n- **Learning Projects**: When the team is learning new technologies or domains\n\n**Anti-pattern: Monolithic Generation**\nAsking AI to \"create a complete user management system\" results in 5000 lines of coupled, untested code that takes days to review and debug.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#incremental-generation"
    },
    {
      "id": "agent-memory",
      "name": "Agent Memory",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Preserve useful context and decisions across sessions",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        }
      ],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Progressive Disclosure",
          "id": "progressive-disclosure"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Parallel Agents",
          "id": "parallel-agents"
        }
      ],
      "bodyMarkdown": "**Description**: Manage AI context as a finite resource through structured memory schemas, prompt pattern capture, and session continuity protocols for efficient multi-session development.\n\n\n**Source**: Anthropic, \"[Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)\" (Claude API documentation); Packer et al., \"[MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)\", October 12, 2023\n\nIndustry tooling commonly calls this practice *memory*, *agent memory*, a *memory bank*, or a\n*memory tool*.\n\n**Core Principles**\n\nAI context is a finite resource with diminishing returns. Effective context engineering requires:\n- **Minimal High-Signal Tokens**: Find the smallest set of information that maximizes outcomes\n- **Just-in-Time Retrieval**: Load context dynamically rather than pre-loading everything\n- **[Progressive Disclosure](#progressive-disclosure)**: Explore and discover information as needed, not upfront\n\n**Structured Memory Schemas**\n\nPersist information outside the context window using standardized memory formats:\n\n```markdown\n# TODO.md - Task tracking across sessions\n- [ ] Implement JWT middleware (blocked: key rotation design)\n- [x] Add bcrypt password hashing (2024-01-15)\n- [ ] Rate limiting (next: research token bucket vs sliding window)\n\n# DECISIONS.log - Architectural decisions with timestamp\n2024-01-15 10:30: Use RS256 for JWT (not HS256)\nRationale: Asymmetric keys enable better key rotation\nAlternatives: HS256 (simpler but less flexible)\nImpact: auth-service, api-gateway\n\n# NOTES.md - Session continuity and discoveries\nSession 2024-01-15:\n  Context: Implementing authentication system\n  Discoveries: bcrypt has performance issues >100 req/s\n  Blockers: Need to decide on refresh token storage\n  Next: Benchmark argon2 as bcrypt alternative\n\n# scratchpad.md - Working memory (cleared after task)\nExploring JWT refresh token flow...\n- httpOnly cookies prevent XSS\n- Need CSRF protection for cookie-based auth\n```\n\n**Prompt Pattern Library**\n\nCapture successful prompts and failures with success rates for reuse:\n\n```bash\n# Initialize knowledge structure\n./knowledge-capture.sh --init\n\n# Capture successful pattern\n./knowledge-capture.sh --success \\\n  --domain \"auth\" \\\n  --pattern \"JWT Auth\" \\\n  --prompt \"JWT with RS256, 15min access, httpOnly cookie\" \\\n  --success-rate \"95%\"\n\n# Document failure to avoid repeating\n./knowledge-capture.sh --failure \\\n  --domain \"auth\" \\\n  --bad-prompt \"Make auth secure\" \\\n  --problem \"Too vague → AI over-engineers\" \\\n  --solution \"Specify exact JWT requirements\"\n```\n\n**Context Window Management**\n\n**Compaction Strategy** - When context approaches limits:\n1. Distill critical decisions to `DECISIONS.log`\n2. Summarize key discoveries in `NOTES.md`\n3. Update `TODO.md` with current state and blockers\n4. Create \"Previously on...\" recap for session continuity\n\n**Session Continuity Protocol** - Resume work across sessions:\n1. Read `NOTES.md` for previous session context\n2. Review `TODO.md` for current tasks and blockers\n3. Check `DECISIONS.log` for recent architectural choices\n4. Scan `scratchpad.md` for active explorations\n\n```bash\n# Compact context when nearing limits\n./context-compact.sh --summarize\n\n# Resume from previous session\n./session-resume.sh  # Displays TODO + recent decisions + notes recap\n```\n\n**Complete Implementation**: See [examples/agent-memory/](examples/agent-memory/) for:\n- Memory schema templates (TODO.md, DECISIONS.log, NOTES.md, scratchpad.md)\n- Context compaction and session resume automation scripts\n- Prompt pattern capture and maintenance tools\n- Working examples of memory schemas in use\n\n**Anti-pattern: Over-Documentation**\n\nCreating extensive knowledge bases that become maintenance burdens instead of accelerating development through selective, actionable knowledge capture.\n\n**Why it's problematic:**\n- Knowledge bases become outdated and misleading\n- Developers spend more time documenting than developing\n- Overly detailed entries are ignored in favor of quick experimentation\n- Knowledge becomes siloed and not easily discoverable\n\n**Instead, focus on:**\n- Capture only high-impact patterns (>80% success rate)\n- Document failures that wasted significant time (>30 minutes)\n- Keep entries concise and immediately actionable\n- Review and prune knowledge quarterly\n\n**Anti-pattern: Bloated Context**\n\nLoading entire codebases, documentation, or conversation history into context rather than using structured memory and just-in-time retrieval.\n\n**Why it's problematic:**\n- Wastes tokens on low-signal information\n- Degrades AI performance due to information overload\n- Slows interaction latency and increases costs\n- Misses the forest for the trees\n\n**Instead:**\n- Use lightweight identifiers (file paths, links) rather than full content\n- Load context progressively as needed\n- Externalize detailed information to memory schemas\n- Prefer 3-5 high-quality examples over exhaustive documentation",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#agent-memory"
    },
    {
      "id": "agent-hooks",
      "name": "Agent Hooks",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Run commands and policy checks at assistant lifecycle hooks",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        }
      ],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        },
        {
          "name": "Custom Commands",
          "id": "custom-commands"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        }
      ],
      "bodyMarkdown": "**Description**: Attach commands and policy checks to assistant lifecycle hooks so validation and workflow controls run automatically.\n\n\nIndustry implementations call these controls *hooks*, *lifecycle hooks*, *agent hooks*, or event plugins. The compatibility anchor above preserves inbound links to the former catalog entry.\n\n**Core Concept**\n\nAttach shell commands to AI assistant lifecycle events. Commands receive context via environment variables (file paths, tool names, user prompts) and return exit codes to allow/block/warn.\n\n**Event Flow Example**\n\n```mermaid\nsequenceDiagram\n    participant Dev as Developer\n    participant AI as AI Assistant\n    participant Pre as PreToolUse Hook\n    participant Post as PostToolUse Hook\n\n    Dev->>AI: Edit .env file\n    AI->>Pre: Run security-hook.sh\n    Pre->>Pre: Check if file is sensitive\n    Pre-->>AI: Exit 2 (BLOCK)\n    AI->>Dev: ❌ Blocked: Cannot edit sensitive file\n\n    Dev->>AI: Edit src/api.js\n    AI->>Pre: Run security-hook.sh\n    Pre->>Pre: Check if file is sensitive\n    Pre-->>AI: Exit 0 (Allow)\n    AI->>AI: Execute file edit\n    AI->>Post: Run security-hook.sh\n    Post->>Post: Scan for secrets with gitleaks\n    alt Secret Found\n        Post-->>AI: Exit 1 (Warning)\n        AI->>Dev: ⚠️ Secret detected! Review before committing\n    else No Secret\n        Post-->>AI: Exit 0 (Success)\n        AI->>Dev: ✅ Edit complete\n    end\n```\n\n**Simple Security Example**\n\nPrevent editing sensitive files and scan for secrets:\n\n```bash\n#!/bin/bash\n# security-hook.sh\n\nFILE=\"$TOOL_INPUT_FILE_PATH\"\n\n# Block .env and credentials files\nif echo \"$FILE\" | grep -E \"(\\\\.env|secrets\\\\.json|credentials)\" > /dev/null; then\n  echo \"❌ Blocked: Cannot edit sensitive file\"\n  exit 2\nfi\n\n# Scan for hardcoded secrets (requires gitleaks)\nif command -v gitleaks > /dev/null; then\n  if gitleaks detect --no-git --source=\"$FILE\" 2>&1 | grep -q \"leaks found\"; then\n    echo \"⚠️ Secret detected! Review before committing.\"\n    exit 1\n  fi\nfi\n\nexit 0\n```\n\n**Configuration Example (Claude Code)**\n\n```json\n{\n  \"hooks\": {\n    \"PreToolUse\": [{\n      \"matcher\": \"Edit\",\n      \"hooks\": [{\"type\": \"command\", \"command\": \"./security-hook.sh\"}]\n    }],\n    \"PostToolUse\": [{\n      \"matcher\": \"Edit\",\n      \"hooks\": [{\"type\": \"command\", \"command\": \"./security-hook.sh\"}]\n    }]\n  }\n}\n```\n\n**Common Use Cases**\n- Auto-format code after edits (`prettier`, `black`, `gofmt`)\n- Block sensitive file modifications\n- Log AI interactions for compliance\n- Run linters before commits\n\n**Security Warning**\n\nEvent commands run with full system access. Always review scripts before enabling. Test in isolated environments first.\n\n**Complete Implementation**\n\nSee [examples/agent-hooks/](examples/agent-hooks/) for a working implementation with security scanning and hooks.\n\n**Anti-pattern: Unchecked Events**\n\nRunning automation from untrusted sources without review exposes your system to malicious code execution and credential theft. Always audit event scripts before installation.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#agent-hooks"
    },
    {
      "id": "custom-commands",
      "name": "Custom Commands",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Encode repeatable domain workflows in assistant commands",
      "dependencies": [
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        }
      ],
      "related": [
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Progressive Disclosure",
          "id": "progressive-disclosure"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Discover and use built-in command vocabularies, then extend them with custom commands that encode domain expertise and sophisticated workflows.\n\n\n**Core Concept**\n\nAI coding tools provide built-in commands for common operations and support custom commands (markdown files with AI instructions) for project-specific workflows. Commands are manual/on-demand (invoked like `/refactor`), while events fire automatically (see [Agent Hooks](#agent-hooks)).\n\n**Command Discovery**\n\nDiscover built-in commands first:\n\n```bash\n# Claude Code\n/help /model /clear /review\n\n# Cursor IDE\nCmd+K /edit /chat\n\n# Gemini CLI\n/stats /memory /tools /clear\n```\n\n| Use Built-in Commands | Create [Custom Commands](#custom-commands) |\n|-----------------------|------------------------|\n| Generic operations (clear, help, model) | Domain expertise (refactoring, security analysis) |\n| Tool features (review, edit) | Project workflows (deploy, implement-spec) |\n| Universal commands | Team standards and conventions |\n\n**Example: Refactoring Assistant**\n\nEncode Martin Fowler's refactoring catalog for systematic code improvement:\n\n```markdown\n---\ndescription: Interactive refactoring assistant based on Martin Fowler's refactoring catalog\nargument-hint: Optional flags (--smell, --duplicates, --suggest)\n---\n\n# Refactoring Assistant\n\nYou are helping a developer improve code maintainability by identifying code smells and recommending specific refactoring techniques from Martin Fowler's catalog.\n\n# Usage\n/refactor              # Full analysis\n/refactor --smell      # Code smells only\n\n# Implementation\n\n### 1. Code Smell Detection\n- Long methods (>20 lines), duplicate code, complex conditionals\n- For each: location (file:line), severity, specific refactoring, effort estimate\n\n### 2. Bloater Detection\n- Excessive parameters (>4), data clumps, primitive obsession\n\n### 3. Refactoring Strategy\n1. Name the code smell\n2. Recommend technique from Fowler's catalog\n3. Show before/after example\n4. Estimate maintainability improvement\n\nGenerate step-by-step refactoring plan prioritized by impact.\n```\n\n**More Examples**\n\nAdditional command examples with detailed implementations:\n\n- **[Implement-Spec](examples/custom-commands/implement-spec-example.md)** - Spec-driven implementation with TDD and traceability\n- **[Security Review](examples/custom-commands/security-review-example.md)** - Multi-layer security analysis (secrets, vulnerabilities, config)\n- **[Safe-Refactor](examples/custom-commands/safe-refactor-example.md)** - Safe refactoring with automated testing and rollback\n- **[Test Runner](examples/custom-commands/test-example.md)** - Smart test selection with coverage and health monitoring\n\n**Tool Support**\n\n```bash\n# Claude Code: .claude/commands/*.md\nmkdir -p .claude/commands\ncp examples/custom-commands/commands/*.md .claude/commands/\n\n# Cursor IDE: .cursorrules\ncat examples/custom-commands/commands/refactor.md >> .cursorrules\n\n# Generic: .ai/commands/ (tool-agnostic)\nmkdir -p .ai/commands\ncp examples/custom-commands/commands/*.md .ai/commands/\n```\n\n**Complete Implementation**\n\nSee [examples/custom-commands/](examples/custom-commands/) for ready-to-use commands, configuration files, and setup guide.\n\n**Anti-pattern: Redundant Commands**\n\nCreating `/clear` when the tool already provides it. Always discover built-in commands first.\n\n**Anti-pattern: Shallow Commands**\n\n```markdown\n# Bad: Just wraps shell command\nRun: npm run deploy:staging\n\n# Good: Encodes expertise\n1. Verify staging environment health\n2. Check for active incidents\n3. Review recent commits for risk\n4. Run deployment with rollback plan\n```\n\n**Anti-pattern: Hardcoded Context**\n\n```markdown\n# Bad: Hardcoded values\nDeploy to prod-db-instance-1.us-east-1.rds.amazonaws.com\n\n# Good: Parameterized\nDeploy to database: $1 (default: $STAGING_DB)\n```",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#custom-commands"
    },
    {
      "id": "progressive-disclosure",
      "name": "Progressive Disclosure",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Load only the task-specific rules needed for the current work",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        }
      ],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        },
        {
          "name": "Custom Commands",
          "id": "custom-commands"
        },
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        },
        {
          "name": "Centralized Rules",
          "id": "centralized-rules"
        },
        {
          "name": "Model Routing",
          "id": "model-routing"
        }
      ],
      "bodyMarkdown": "**Description**: Load AI assistant rules incrementally based on task context rather than bundling all instructions upfront, preventing context bloat and improving instruction-following consistency.\n\n\n**Core Problem**\n\nAI coding assistants already consume part of their context window with built-in system instructions. When a project loads a single, monolithic rules file (hundreds of lines) for every task, instruction-following accuracy drops and irrelevant guidance crowds out what the model needs right now.\n\n**Implementation Strategy: Three-Tier Rule Architecture**\n\nKeep a small universal rules file, and load specialized rules only when the task touches the relevant area:\n\n```\n.ai/\n├── CLAUDE.md                    # Universal rules only (<60 lines)\n├── rules/                       # Specialized rules loaded on-demand\n│   ├── security/                # secrets, auth, dependencies\n│   ├── development/             # api-design, database, testing\n│   ├── operations/              # deployment, monitoring, cicd\n│   └── architecture/            # patterns, performance\n└── prompts/                     # Reusable task templates\n```\n\n**Main Rules File = Router**\n\nThe main file should explicitly tell the assistant what to load based on context:\n\n```markdown\n# AI Development Rules\n\n# Universal Principles (Always Apply)\n- Follow existing patterns in the codebase\n- Never commit secrets or credentials\n- Run tests after code changes\n\n# Progressive Disclosure (Context Loading)\n- **Security work** (auth/, .env, credentials): Read `.ai/rules/security/`\n- **API development** (api/, routes/): Read `.ai/rules/development/api-design.md`\n- **Database changes** (migrations/, models/): Read `.ai/rules/development/database.md`\n- **Testing** (tests/, specs/): Read `.ai/rules/development/testing.md`\n- **CI/CD** (.github/workflows/): Read `.ai/rules/operations/cicd.md`\n```\n\n**Automatic Loading with Hooks**\n\nCombine with [Agent Hooks](#agent-hooks) to auto-load the right rules before tool use:\n\n```bash\n#!/bin/bash\n# .ai/hooks/auto-load-context.sh\n\nFILE_PATH=\"$TOOL_INPUT_FILE_PATH\"\nLOADED_RULES=\"\"\n\nif echo \"$FILE_PATH\" | grep -Eq \"(\\\\.env|credentials|secrets|auth/)\"; then\n  LOADED_RULES=\"$LOADED_RULES .ai/rules/security/\"\nfi\n\nif echo \"$FILE_PATH\" | grep -Eq \"(api/|routes/|controllers/)\"; then\n  LOADED_RULES=\"$LOADED_RULES .ai/rules/development/api-design.md\"\nfi\n\nif echo \"$FILE_PATH\" | grep -Eq \"(tests?/|spec/|\\\\.test\\\\.|\\\\.spec\\\\.)\"; then\n  LOADED_RULES=\"$LOADED_RULES .ai/rules/development/testing.md\"\nfi\n\nif [ -n \"$LOADED_RULES\" ]; then\n  echo \"AI: Before proceeding, read these files: $LOADED_RULES\"\nfi\n```\n\n**Complete Implementation**\n\nSee [examples/progressive-disclosure/](examples/progressive-disclosure/) for templates and a ready-to-adapt rules router + directory layout.\n\n**Anti-pattern: Bloated Configuration**\n\nLoading a single, massive rules file for every task wastes context and reduces instruction-following accuracy—especially for small edits that need only a handful of universal rules.\n\n**Anti-pattern: Missing Guidance**\n\nCreating specialized rule files but never documenting when/how to load them forces humans to remember the routing and prevents consistent, automated context loading.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#progressive-disclosure"
    },
    {
      "id": "atomic-decomposition",
      "name": "Atomic Decomposition",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Split complex work into independently implementable agent tasks",
      "dependencies": [
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        }
      ],
      "related": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        },
        {
          "name": "Issue Generation",
          "id": "issue-generation"
        },
        {
          "name": "Parallel Agents",
          "id": "parallel-agents"
        }
      ],
      "bodyMarkdown": "**Description**: Break complex features into atomic, independently implementable tasks for parallel AI agent execution.\n\n\n**Atomic Task Criteria**\n\n```mermaid\ngraph TD\n    A[Feature Requirement] --> B[Task Analysis]\n    B --> C{Atomic Task Check}\n    C -->|✓ Independent| D[Can run in parallel]\n    C -->|✓ <2 hours| E[Rapid feedback cycle]\n    C -->|✓ Clear I/O| F[Testable interface]\n    C -->|✓ No shared state| G[Conflict-free]\n    C -->|✗ Fails check| H[Split Further]\n    H --> B\n    \n    D --> I[Ready for Agent]\n    E --> I\n    F --> I\n    G --> I\n```\n\n**Core Decomposition Process**\n\n```bash\n# Feature: User Authentication System\n# Bad: Monolithic task\n❌ \"Implement complete user authentication with JWT, password hashing, rate limiting, and email verification\"\n\n# Good: Atomic breakdown with AI validation\nai_decompose \"Break down user authentication into atomic tasks:\n\nTask 1: Password validation service (1.5h)\n- Input: plain text password, validation rules\n- Output: validation result object\n- Dependencies: None (pure function)\n\nTask 2: JWT token generation service (1h)  \n- Input: user ID, role, expiration config\n- Output: signed JWT token\n- Dependencies: None (crypto operations only)\n\nTask 3: Rate limiting middleware (2h)\n- Input: request metadata, rate limit config\n- Output: allow/deny decision\n- Dependencies: None (stateless logic)\n\nTask 4: Login endpoint integration (1h)\n- Input: credentials, services from tasks 1-3\n- Output: HTTP response with token/error\n- Dependencies: Tasks 1-3 (integration only)\"\n\n# Validate atomicity\nai_task_validator \"Check each task for:\n1. <2 hour completion time\n2. No shared mutable state\n3. Clear input/output contracts\n4. Testable in isolation\n5. No circular dependencies\"\n```\n\n\n**Agent Assignment & Coordination**\n\n```yaml\n# .ai/task-assignment.yml\nauthentication_feature:\n  parallel_tasks:\n    - id: \"auth-001\" # Password validation\n      agent: \"backend-specialist-1\"\n      estimated_hours: 1.5\n      dependencies: []\n      \n    - id: \"auth-002\" # JWT generation\n      agent: \"security-specialist\"\n      estimated_hours: 1\n      dependencies: []\n      \n    - id: \"auth-003\" # Rate limiting\n      agent: \"backend-specialist-2\"\n      estimated_hours: 2\n      dependencies: []\n      \n  integration_tasks:\n    - id: \"auth-004\" # Login endpoint\n      agent: \"integration-specialist\"\n      estimated_hours: 1\n      dependencies: [\"auth-001\", \"auth-002\", \"auth-003\"]\n```\n\n**Task Contract Validation**\n\n```python\n# Ensure tasks meet atomic criteria\nclass TaskContract:\n    def validate_atomic(self) -> bool:\n        return all([\n            len(self.side_effects) == 0,    # No side effects\n            self.estimated_hours <= 2,      # Rapid completion\n            self.has_clear_io_contract()    # Testable interface\n        ])\n\n# Example validation\ntask = TaskContract(\"auth-001\")\ntask.inputs = {\"password\": str, \"rules\": PasswordRules}  \ntask.outputs = {\"is_valid\": bool, \"errors\": List[str]}\nassert task.validate_atomic()  # ✓ Passes atomic criteria\n```\n\n**Complete Implementation**: See [examples/atomic-decomposition/](examples/atomic-decomposition/) for:\n- Contract validation system with automated checking\n- Function-level decomposition techniques and trigger indicators\n- Task dependency resolution and scheduling\n- Parallel execution coordination and monitoring\n- Agent assignment and resource management\n\n**When to Use [Atomic Decomposition](#atomic-decomposition)**\n- **Parallel Agent Implementation**: Multiple AI agents working simultaneously\n- **Complex Feature Development**: Large features benefiting from parallel work\n- **Time-Critical Projects**: Speed through parallelization essential\n- **Risk Mitigation**: Reduce blast radius of individual task failures\n\n**Anti-pattern: False Atomicity**\nCreating tasks that appear independent but secretly share state, require specific execution order, or have hidden dependencies on other concurrent work.\n\n**Anti-pattern: Over-Decomposition**  \nBreaking tasks so small that coordination overhead exceeds the benefits of parallelization, leading to more complexity than value.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#atomic-decomposition"
    },
    {
      "id": "guided-refactoring",
      "name": "Guided Refactoring",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Improve code against measurable quality rules while preserving behavior",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        }
      ],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Agent Hooks",
          "id": "agent-hooks"
        },
        {
          "name": "Debt Forecasting",
          "id": "debt-forecasting"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Systematic code improvement using AI to detect and resolve code smells with measurable quality metrics, following established refactoring rules and maintaining test coverage throughout the process.\n\n\n**Code Smell Detection Framework**\n\n```mermaid\ngraph TD\n    A[Code Analysis] --> B[Smell Detection]\n    B --> C[Refactoring Strategy]\n    C --> D[AI Implementation]\n    D --> E[Test Validation]\n    E --> F[Quality Metrics]\n    F --> G{Improvement?}\n    G -->|Yes| H[Commit Changes]\n    G -->|No| I[Revert & Retry]\n    H --> J[Update Knowledge Base]\n    I --> C\n```\n\n**Core Workflow**\n\n```bash\n# 1. Define refactoring rules\ncat > .ai/rules/refactoring.md << 'EOF'\n## Long Method Smell\n- Max lines: 20 (excluding docstrings)\n- Max cyclomatic complexity: 10\n- Detection: flake8 C901, pylint R0915\n\n## Large Class Smell  \n- Max class lines: 250, Max methods: 20\n- Detection: pylint R0902, R0904\nEOF\n\n# 2. Detect code smells with AI\nflake8 --select=C901 src/ > smells.txt\npylint src/ --disable=all --enable=R0915,R0902,R0904 >> smells.txt\n\nai \"Analyze smells.txt using .ai/rules/refactoring.md:\n1. Prioritize by impact and complexity\n2. Suggest specific refactoring strategy for each smell\n3. Generate implementation plan with risk assessment\"\n\n# 3. Apply refactoring with test preservation\npytest --cov=src tests/  # Baseline coverage\n\nai \"Refactor process_user_data() method (35 lines, exceeds threshold):\n- Apply Extract Method pattern for validation, database, notifications\n- Maintain test coverage >90% and API contract\n- Create atomic commits for each extracted method\"\n\n# 4. Validate and track improvements\npytest --cov=src tests/\nflake8 src/ && pylint src/\n\nai \"Generate refactoring impact report:\nBefore: complexity=12, length=35 lines, coverage=85%\nAfter: complexity=4+2+2, length=8+6+7 lines, coverage=92%\nDocument lessons learned in .ai/knowledge/refactoring.md\"\n```\n\n**Common Refactoring Patterns**\n\n- **Extract Method**: Break down long methods (>20 lines)\n- **Extract Class**: Split large classes (>250 lines, >20 methods)  \n- **Replace Primitive**: Convert strings/dicts to value objects\n- **Consolidate Duplicates**: Merge similar code patterns\n\n**Complete Implementation**: See [examples/guided-refactoring/](examples/guided-refactoring/) for:\n- Automated refactoring pipeline with CI integration\n- Quality metrics tracking and reporting\n- Risk assessment guidelines and rollback procedures\n- Knowledge base templates for refactoring outcomes\n\n**Anti-pattern: Scattered Refactoring**\nMaking widespread changes without systematic analysis leads to introduced bugs and degraded code quality.\n\n**Anti-pattern: Premature Refactoring**\nRefactoring code for hypothetical future requirements rather than addressing current code smells and quality issues.\n\n----",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#guided-refactoring"
    },
    {
      "id": "agent-observability",
      "name": "Agent Observability",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Capture traces, tool events, evaluations, and runtime context for diagnosis and improvement",
      "dependencies": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        }
      ],
      "related": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Error Resolution",
          "id": "error-resolution"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        }
      ],
      "bodyMarkdown": "**Description**: Capture structured traces, model and tool events, handoffs, evaluations, cost, latency, and failure context so agent behavior can be diagnosed and improved.\n\n\nIndustry sources use *agent observability*, *AI observability*, and *tracing*. The compatibility anchor above preserves inbound links to the former catalog entry.\n\n**Agent Run Trace**\n\nTreat an agent invocation as a correlated trace rather than an unstructured transcript:\n\n```mermaid\ngraph LR\n    R[Agent run span] --> M[Model call]\n    R --> T[Tool call]\n    T --> E[Error + artifact ref]\n    R --> H[Agent handoff]\n    H --> V[Independent evaluation]\n    R --> S[Cost, tokens, latency, outcome]\n```\n\nEvery event carries a `trace_id`, unique `span_id`, `parent_span_id`, `run_id`, and `session_id`. Event-specific fields make the control flow reviewable:\n\n| Event | Required diagnostic fields |\n|-------|----------------------------|\n| Agent run | producer, repository, base/final commit, goal, status, duration |\n| Model call | model, input/output tokens, cost, latency, status, prompt/response artifact refs |\n| Tool call | tool name, input/output refs, exit code, latency, status |\n| Handoff | source actor, target actor, reason, artifact ref |\n| Evaluation | evaluator and producer identities, verdict, score, check ref |\n| Error | failed parent span, error type/message, immutable evidence ref |\n\n```json\n{\n  \"trace_id\": \"trace_4c2d...\",\n  \"span_id\": \"span_a8e1...\",\n  \"parent_span_id\": \"span_root...\",\n  \"run_id\": \"run_f391...\",\n  \"session_id\": \"session_42\",\n  \"event_type\": \"tool.call\",\n  \"tool_name\": \"pytest\",\n  \"status\": \"error\",\n  \"duration_ms\": 430,\n  \"exit_code\": 1,\n  \"attributes\": {\n    \"input_ref\": \"tests/test_retry.py\",\n    \"output_ref\": \"artifacts/pytest.txt\"\n  }\n}\n```\n\n**Collect, Validate, and Budget**\n\nInstrument the agent runner or orchestrator, outside the model process. The recorder redacts before writing and stores references instead of raw prompts, responses, tool payloads, source files, or environment values:\n\n```python\n# Run from examples/agent-observability/.\nfrom agent_tracing import TraceRecorder\nfrom trace_fitness import validate_trace\nfrom trace_metrics import budget_alerts, summarize_trace\n\ntrace = TraceRecorder(session_id=\"session_42\", output_path=\"artifacts/trace.jsonl\")\nroot = trace.start_run(\n    goal=\"Fix retry behavior\",\n    producer=\"implementation-agent\",\n    repository=\"acme/payments\",\n    base_commit=\"9a17d2c\",\n)\ntrace.model_call(\n    parent_span_id=root,\n    model=\"reasoning-model\",\n    input_tokens=1200,\n    output_tokens=280,\n    cost_usd=0.018,\n    duration_ms=610,\n    request_ref=\"sha256:request\",\n    response_ref=\"sha256:response\",\n)\ntrace.tool_call(\n    parent_span_id=root,\n    tool_name=\"pytest\",\n    duration_ms=430,\n    status=\"ok\",\n    input_ref=\"tests/test_retry.py\",\n    output_ref=\"artifacts/pytest.txt\",\n    exit_code=0,\n)\ntrace.handoff(\n    parent_span_id=root,\n    from_actor=\"implementation-agent\",\n    to_actor=\"verification-agent\",\n    reason=\"independent review\",\n    artifact_ref=\"git:head:b82c119\",\n)\ntrace.evaluation(\n    parent_span_id=root,\n    evaluator=\"verification-agent\",\n    producer=\"implementation-agent\",\n    verdict=\"pass\",\n    score=0.95,\n    check_ref=\"artifacts/verification.json\",\n)\ntrace.finish_run(\n    status=\"ok\",\n    head_commit=\"b82c119\",\n    duration_ms=1600,\n    summary_ref=\"artifacts/run-summary.json\",\n)\n\nassert validate_trace(trace.events) == []\nsummary = summarize_trace(trace.events)\nassert not budget_alerts(\n    summary, max_cost_usd=0.10, max_duration_ms=5000, max_output_tokens=1000\n)\n```\n\nDeterministic checks validate schema, span relationships, redaction, required cost/latency fields, and evaluator independence. A fresh reviewer may assess whether the valid trace is semantically useful, but must not reconstruct missing telemetry or share the producer identity.\n\n**Privacy and Retention**\n\n- Redact credentials, authorization headers, cookies, tokens, and sensitive tool arguments before persistence.\n- Prefer commit SHAs, content hashes, and access-controlled artifact references to raw content.\n- Apply explicit retention and access policies to traces; observability is not permission to archive every prompt.\n- Preserve missing fields as gaps. Never ask a model to invent an event that was not captured.\n\n**Failure Diagnosis**\n\nBuild a redacted bundle containing the ordered model/tool/error/evaluation timeline, failed span IDs, cost and latency summary, and immutable artifact references. Pass that evidence into human-gated [Error Resolution](#error-resolution), where a proposed application or repository fix is reviewed and deterministically validated.\n\n**Complete Implementation**: See [examples/agent-observability/](examples/agent-observability/) for a provider-neutral trace recorder, metrics, redaction, schema fitness checks, independent quality interface, diagnostic-bundle builder, and executable tests.\n\n**Anti-pattern: Opaque Agent Runs**\n\nA transcript without trace/span relationships, model and tool metadata, costs, handoffs, evaluation identity, and source-linked failures cannot show what acted, what it touched, why it stopped, or whether the producer certified itself.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#agent-observability"
    },
    {
      "id": "image-spec",
      "name": "Image Spec",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Translate screenshots and design mockups into UI code with visual feedback",
      "dependencies": [
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        }
      ],
      "related": [
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        },
        {
          "name": "Model Routing",
          "id": "model-routing"
        }
      ],
      "bodyMarkdown": "**Description**: Use screenshots and design mockups as visual specifications that coding agents translate into UI code and refine through visual feedback.\n\n\nIndustry implementations commonly call this practice *design-to-code* or *screenshot-to-code*. The pattern is deliberately scoped to UI visuals; architecture diagrams and data-flow diagrams remain useful supporting context, but the adoption evidence does not establish them as primary executable specifications.\n\n**Core Implementation**\n\nUse a single screenshot or mockup as the source of truth for layout and visual intent, then supplement it with minimal behavioral and technology constraints:\n\n```bash\n# 1. Prepare one focused visual specification\n# - checkout-mock.png (layout, states, and key interactions)\n\n# 2. Attach the mockup and provide a minimal build request\ncat > build-request.txt << 'EOF'\nImplement the attached checkout mockup as a responsive React component.\nMatch its layout, spacing, colors, and empty/error states.\nUse the existing design tokens and component library.\nDo not invent backend behavior; stub the submit handler.\nEOF\n\n# 3. Iterate with visual feedback\n# - Screenshot the running output\n# - Annotate with required changes\n# - Re-attach and request the next iteration\n```\n\n**Complete Implementation**\n\nSee [examples/image-spec/](examples/image-spec/) for prompt templates and a repeatable screenshot-to-code iteration loop.\n\n**Anti-pattern: Overwhelming Visuals**\n\nUploading many screenshots at once without a named target state overwhelms context and creates contradictory UI requirements. Start with one screen and one state, implement it, then add the next visual increment.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#image-spec"
    },
    {
      "id": "adversarial-evaluator",
      "name": "Adversarial Evaluator",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Separate generation from independent adversarial evaluation",
      "dependencies": [
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        }
      ],
      "related": [
        {
          "name": "Planned Implementation",
          "id": "planned-implementation"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        },
        {
          "name": "Spec-Driven Development",
          "id": "spec-driven-development"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Separate the agent that generates work from an independent agent that judges it — ideally a different model — so adversarial pressure and cross-model divergence, not a model grading its own output, become the eval signal for high-stakes decisions.\n\n\n**Core Principle: Separate the Producer from the Judge**\n\nBorrowed from GANs (Generative Adversarial Networks): two networks compete — one generates, one judges — and that adversarial tension forces quality up. The same dynamic applies to multi-agent systems. A model asked to grade its own output shares its own blind spots; the confident reasoning that produced a flawed answer also produces a confident review of it. The fix is to separate the generator from the evaluator completely, and to make the evaluator as *independent* as the stakes require.\n\nIndependence is a spectrum, not a switch:\n\n| Independence level | How | Strength |\n|---|---|---|\n| Same model, different prompt/role | \"Now critique the above as a skeptical reviewer\" | Weak — shared training priors, correlated blind spots |\n| Different model as judge | Claude generates, GPT-5 or Gemini judges | Strong — independent training data and failure modes |\n| Different identity + signing key | Judge owned by a separate party, attestation signed | Strongest — see [Autonomous Acceptance](experiments/README.md#autonomous-acceptance) |\n\nThe pattern has two topologies. Pick the one that matches the decision: an **adversarial judge** when you have one candidate and need to know whether it holds up, or **cross-model divergence** when there is no single right answer and you want to surface the space of reasonable ones.\n\n**Topology 1: Adversarial Judge (generate → attack)**\n\nSequential and asymmetric. One agent produces; a second, independent agent is told to *find fault* — not to summarize, not to agree, but to refute. Surviving that pressure is the quality signal.\n\n```mermaid\ngraph LR\n    G[Generator Agent<br/>Claude] -->|candidate| J[Judge Agent<br/>different model]\n    J -->|attack + grade| V{Survives?}\n    V -->|Yes| A[Accept]\n    V -->|No| R[Return with findings]\n    R --> G\n    style G fill:#a8d5ba,stroke:#2d5a3f,color:#1a3a25\n    style J fill:#f9e79f,stroke:#b7950b,color:#7d6608\n```\n\n```bash\n# adversarial-judge.sh — generate with one model, attack with another\nGENERATOR=\"claude-opus-4-8\"\nJUDGE=\"gpt-5\"\n\nllm -m \"$GENERATOR\" < task.md > candidate.md\n\nllm -m \"$JUDGE\" <<EOF\nYou are an adversarial reviewer. Your goal is to REFUTE the work below, not\nto praise it. Find every correctness bug, security hole, unhandled edge case,\nand unstated assumption. If you cannot break it, say so explicitly.\n\nTASK: $(cat task.md)\nCANDIDATE: $(cat candidate.md)\nEOF\n```\n\nThe judge must run on a *different* model than the generator. A Claude-generated answer reviewed by Claude inherits Claude's blind spots; the same answer attacked by GPT-5 or Gemini meets a different set of priors. That diversity of training data is what makes the adversary's findings real rather than confirmatory.\n\n**Topology 2: Cross-Model Divergence (fan out → compare)**\n\nParallel and symmetric. Instead of one judge attacking one output, run the *same* task across several frontier models at once and treat their disagreement as the signal. No model is cast as the judge — the divergence between independent peers is the verdict.\n\n```mermaid\ngraph TD\n    A[High-Stakes Prompt] --> B[Fan Out to N Models]\n    B --> C1[Claude Opus]\n    B --> C2[GPT-5]\n    B --> C3[Gemini]\n    C1 --> D[Side-by-Side Outputs]\n    C2 --> D\n    C3 --> D\n    D --> E{Convergent?}\n    E -->|Yes| F[Stronger Prior<br/>Proceed With Confidence]\n    E -->|No| G[Investigate the Divergence<br/>Disagreement IS the Finding]\n    G --> H[Choose, Synthesize, or Re-Prompt]\n\n    style D fill:#a8d5ba,stroke:#2d5a3f,color:#1a3a25\n    style G fill:#f9e79f,stroke:#b7950b,color:#7d6608\n    style F fill:#f5b7b1,stroke:#c0392b,color:#78281f\n```\n\n```bash\n#!/usr/bin/env bash\n# fan-out.sh — run the same prompt across multiple models\nPROMPT_FILE=\"$1\"\nmkdir -p .cross-model/$(date +%Y%m%d-%H%M%S)\nRUN_DIR=$(ls -td .cross-model/* | head -1)\n\nfor model in \\\n  \"claude-opus-4-8\" \\\n  \"gpt-5\" \\\n  \"gemini-2.5-pro\"; do\n    echo \"→ $model\"\n    llm -m \"$model\" < \"$PROMPT_FILE\" > \"$RUN_DIR/${model}.md\"\ndone\n\n# Diff the outputs to surface divergence quickly\ndiff -u \"$RUN_DIR/claude-opus-4-8.md\" \"$RUN_DIR/gpt-5.md\"     > \"$RUN_DIR/claude-vs-gpt.diff\"  || true\ndiff -u \"$RUN_DIR/gpt-5.md\"           \"$RUN_DIR/gemini-2.5-pro.md\" > \"$RUN_DIR/gpt-vs-gemini.diff\" || true\n\necho \"Outputs in $RUN_DIR — review the .diff files first.\"\n```\n\nReading the divergence:\n\n| Outcome | What it means | Action |\n|---|---|---|\n| All models agree | Stronger prior than any single model alone | Proceed |\n| 2 agree, 1 disagrees | The minority report may be catching something the majority missed | Read the dissent carefully before discarding |\n| All three disagree | The prompt is underspecified, the task is genuinely ambiguous, or you're at the frontier of model capability | Re-prompt with sharper constraints, or treat as a human-judgment call |\n\n**The disagreement IS the signal.** Don't reduce three rich outputs to a vote count — investigate *why* the models split. That investigation is the value the pattern delivers, not the \"winning\" answer.\n\n**When to Use**\n\nIndependent evaluation costs more than a single pass — an extra model call per judgment, or N parallel calls — so don't apply it to every prompt. Reach for it when:\n\n- **Irreversible decisions**: schema migrations, public API contracts, security model changes\n- **High-stakes reviews**: pre-merge architecture review, threat modeling, incident post-mortems\n- **Eval-style spot-checks**: validating a single canonical prompt that drives downstream automation\n- **Onboarding a new model**: comparing a candidate model's output against your trusted baseline before adopting it\n\nFor routine prompts, the single-model degenerate form (below) is sufficient and cheaper.\n\n**Single-Model Degenerate Form**\n\nWhen the cost of a second model isn't justified, ask one model to generate and then critique its own work, or to produce multiple options in a single call:\n\n```\n\"Generate 3 different authentication approaches. For each: performance profile,\nsecurity trade-offs, implementation complexity, and when to choose it.\nThen recommend one based on a typical SaaS startup's constraints.\"\n```\n\nThis is cheaper but provides weaker signal — the critique shares the generator's training biases. Modern IDE assistants offer this natively as \"alternative completions.\" It's the budget-friendly cousin of the full pattern, not a substitute for genuine independence on high-stakes calls.\n\n**Anti-pattern: Self-Grading**\n\nLetting the model that produced the work also certify it — a satisfaction score, a \"looks good to me,\" a self-review — and treating that as independent verification. The reviewer shares every blind spot of the author because it *is* the author: the confident reasoning that generated a subtly wrong answer generates an equally confident approval of it. Taken to its institutional extreme — a self-signed acceptance score gating a merge — this becomes the [Autonomous Acceptance](experiments/README.md#autonomous-acceptance) anti-pattern, where the rubber stamp simply moves from a human to a number.\n\n**Anti-pattern: Single-Model Bias**\n\nCommitting irreversible decisions on a single model's output without ever checking whether another frontier model would have made the same call. The decision feels well-reasoned because the model's prose is confident — but confidence is not correctness, and one model's blind spots become the project's blind spots.\n\n**Anti-pattern: Voting Theater**\n\nRunning three models and treating majority rule as truth. Frontier models are trained on overlapping data and exhibit correlated errors; 2-of-3 agreement on a wrong answer is common when the wrong answer is the most plausible-sounding one. Use the votes as a *prompt for investigation*, never as a verdict.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#adversarial-evaluator"
    },
    {
      "id": "parallel-agents",
      "name": "Parallel Agents",
      "maturity": "Advanced",
      "type": "Development",
      "category": "development",
      "shortDescription": "Run agents concurrently on isolated tasks or environments",
      "dependencies": [
        {
          "name": "Atomic Decomposition",
          "id": "atomic-decomposition"
        }
      ],
      "related": [
        {
          "name": "Atomic Decomposition",
          "id": "atomic-decomposition"
        },
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        }
      ],
      "bodyMarkdown": "**Description**: Run multiple AI agents concurrently on isolated tasks or environments to maximize development speed and exploration.\n\n\n**Agent Coordination Lifecycle**\n\n```mermaid\nsequenceDiagram\n    participant M as Manager\n    participant A1 as Auth Agent\n    participant A2 as API Agent  \n    participant A3 as Test Agent\n    participant SM as Shared Memory\n    participant CS as Conflict Scanner\n    \n    M->>A1: Start (OAuth2 Task)\n    M->>A2: Start (REST API Task)\n    M->>A3: Start (Test Suite Task)\n    \n    par Parallel Development\n        A1->>A1: Implement OAuth2 Flow\n        A1->>SM: Record Learning\n    and\n        A2->>A2: Implement REST Endpoints\n        A2->>SM: Record API Patterns\n    and\n        A3->>A3: Generate Integration Tests\n        A3->>SM: Record Test Patterns\n    end\n    \n    SM->>CS: Trigger Conflict Analysis\n    CS->>M: Report Conflicts/All Clear\n    M->>M: Merge Components & Cleanup\n```\n\n**Core Implementation Approaches**\n\n```yaml\n# Container-based isolation\n# docker-compose.parallel-agents.yml\nservices:\n  agent-auth:\n    image: ai-dev-environment:latest\n    volumes:\n      - ./feature-auth:/workspace:rw\n      - shared-memory:/shared:ro\n    environment:\n      - AGENT_ID=auth-feature\n      - TASK_ID=implement-oauth2\n    networks:\n      - agent-network\n\n  agent-api:\n    image: ai-dev-environment:latest\n    volumes:\n      - ./feature-api:/workspace:rw\n      - shared-memory:/shared:ro\n    environment:\n      - AGENT_ID=api-feature\n      - TASK_ID=implement-rest-endpoints\n\nvolumes:\n  shared-memory:\n    driver: local\nnetworks:\n  agent-network:\n    driver: bridge\n    internal: true\n```\n\n**Git Worktree Parallelization**\n\n```bash\n# Create isolated branches for parallel work\ngit worktree add -b agent/auth ../agent-auth\ngit worktree add -b agent/api ../agent-api\ngit worktree add -b agent/tests ../agent-tests\n\n# Launch agents in parallel\nparallel --jobs 3 << EOF\ncd ../agent-auth && ai-agent implement-oauth2\ncd ../agent-api && ai-agent implement-rest-endpoints\ncd ../agent-tests && ai-agent generate-integration-tests\nEOF\n\n# Automated conflict detection and merge\nfor branch in $(git branch -r | grep 'agent/'); do\n  git checkout -b temp-merge main\n  if git merge --no-commit --no-ff $branch; then\n    echo \"✓ No conflicts in $branch\"\n    git merge --abort\n  else\n    echo \"⚠ Conflicts detected - using AI resolution\"\n    ai-agent resolve-conflicts --branch $branch\n  fi\n  git checkout main && git branch -D temp-merge\ndone\n\n# Cleanup\ngit worktree remove ../agent-auth\ngit worktree remove ../agent-api\ngit worktree remove ../agent-tests\n```\n\n**Shared Memory & Coordination**\n\n```python\nimport fcntl\n\n# Agent coordination with shared knowledge\nclass AgentMemory:\n    def record_learning(self, agent_id, key, value):\n        \"\"\"Thread-safe learning capture with file locking\"\"\"\n        with fcntl.flock(self.lock_file, fcntl.LOCK_EX):\n            self.memory[agent_id][key] = value\n        \n    def get_shared_knowledge(self):\n        \"\"\"Consolidated knowledge from all agents\"\"\"\n        return self.consolidated_memory\n\n# Task definition\ntasks = {\n    \"auth-service\": {\n        \"agent_count\": 1,\n        \"isolation\": \"container\", \n        \"dependencies\": [],\n        \"instructions\": \"Implement OAuth2 with JWT tokens\"\n    },\n    \"api-endpoints\": {\n        \"agent_count\": 2,\n        \"isolation\": \"worktree\",\n        \"dependencies\": [\"auth-service\"],\n        \"instructions\": \"REST endpoints: user mgmt + CRUD\"\n    }\n}\n```\n\n**Complete Implementation**: See [examples/parallel-agents/](examples/parallel-agents/) for:\n- Full Docker isolation and coordination setup\n- Git worktree management and conflict resolution\n- Shared memory system with file locking\n- Emergency shutdown and safety monitoring\n- Task distribution and dependency management\n\n**When to Use [Parallel Agents](#parallel-agents)**\n- **Complex features** requiring multiple specialized implementations\n- **Time-critical projects** where speed trumps coordination overhead\n- **Exploration phases** testing multiple approaches simultaneously\n- **Large teams** with strong DevOps and coordination processes\n\n**Source**: [AI Native Dev - How to Parallelize AI Coding Agents](https://ainativedev.io/news/how-to-parallelize-ai-coding-agents)\n\n**Anti-pattern: Uncoordinated Agents**\nRunning multiple agents without isolation, shared memory, or conflict resolution leads to race conditions, lost work, and system instability.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#parallel-agents"
    },
    {
      "id": "error-resolution",
      "name": "Error Resolution",
      "maturity": "Intermediate",
      "type": "Development",
      "category": "development",
      "shortDescription": "Diagnose failures and apply proposed fixes only after human review and deterministic validation",
      "dependencies": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        }
      ],
      "related": [
        {
          "name": "Developer Lifecycle",
          "id": "developer-lifecycle"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        },
        {
          "name": "Harness Engineering Lens",
          "id": "harness-engineering-lens"
        }
      ],
      "bodyMarkdown": "**Description**: Collect failure context, reproduce and diagnose the cause with AI, then apply a proposed fix only after human review and deterministic validation.\n\n\nThe human approval node is part of the pattern, not an optional safeguard. Diagnosis and proposal generation may be automated; applying the patch remains human-gated and the deterministic checks arbitrate success.\n\n**[Error Resolution](#error-resolution) Workflow**\n\n```mermaid\ngraph TD\n    A[Error Occurs] --> B[Collect Error Context]\n    B --> C[Enrich with Git History]\n    C --> D[AI Diagnosis]\n    D --> E[Generate Fix Proposals]\n    E --> F{Human Review}\n    F -->|Approved| G[Apply Fix]\n    F -->|Rejected| H[Refine Context]\n    G --> I[Run Tests]\n    I --> J{Tests Pass?}\n    J -->|Yes| K[Commit Fix]\n    J -->|No| L[Rollback]\n    H --> D\n    L --> D\n\n    style B fill:#e1f5e1\n    style D fill:#ffe6e6\n    style G fill:#ffe6e6\n    style K fill:#e1f5e1\n```\n\n**Core Implementation**\n\n**Step 1: Collect Error Context**\n\n```bash\n# Create comprehensive error context file\ncat > .error-context.md << EOF\n# Error Analysis\n\n**Error Output:**\n[Complete error message, stack trace, and exit codes]\n\n**Recent Changes:**\n$(git log --oneline -5)\n\n**Affected Files:**\n$(git diff --name-only HEAD~1)\n\n**File Contents:**\n$(cat path/to/affected/file.ext)\n\n**Environment:**\n- OS: $(uname -s)\n- Shell: $SHELL\n- Working Directory: $(pwd)\nEOF\n```\n\n**Application Failure Context**\n\nInstrument application operations for diagnosis, but keep that telemetry distinct from the agent-run trace described by [Agent Observability](#agent-observability). A useful failure artifact records the operation, correlation ID, exact error type/message, safe reproduction inputs, source commit, and immutable log or trace references:\n\n```json\n{\n  \"operation\": \"process_payment\",\n  \"correlation_id\": \"req_42\",\n  \"agent_trace_id\": \"trace_4c2d...\",\n  \"error_type\": \"PaymentError\",\n  \"error_message\": \"provider timeout\",\n  \"safe_inputs\": {\"order_id\": \"order_42\"},\n  \"source_commit\": \"9a17d2c\",\n  \"evidence_refs\": [\"logs/payment-order_42.jsonl\", \"traces/request-order_42.json\"]\n}\n```\n\nRedact credentials and sensitive payloads before persistence. Use correlation IDs to join application logs and request traces, and use `agent_trace_id` only when an agent-run trace contributed to the diagnosis. Neither artifact authorizes applying a fix; the human review node below remains mandatory.\n\n**Step 2: AI-Powered Diagnosis**\n\n```bash\n# Send structured context to AI for analysis\nai \"Analyze this error and provide actionable fixes:\n\nCONTEXT:\n$(cat .error-context.md)\n\nREQUIRED OUTPUT:\n1. Root cause analysis\n2. Specific fix commands (copy-pasteable)\n3. Prevention strategy (pre-commit hooks, tests, etc.)\n\nFormat fixes as executable bash commands.\"\n```\n\n**Step 3: Validate and Apply Fixes**\n\n```bash\n# Create checkpoint before applying fixes\ngit stash push -m \"Pre-fix checkpoint\"\n\n# Review AI suggestions\ncat ai-suggestions.md\n\n# Apply fixes with validation\nbash fix-commands.sh\n\n# Verify with tests\n./run-tests.sh\n\n# Commit if successful, rollback if not\nif [ $? -eq 0 ]; then\n    git add .\n    git commit -m \"fix: [description based on AI analysis]\"\n    git stash drop\nelse\n    git stash pop\n    echo \"Fix failed validation, rolled back\"\nfi\n```\n\n**Practical Workflow Example**\n\n```bash\n# 1. Capture error from any source (CI, terminal, logs)\nERROR_LOG=\"path/to/error.log\"\n\n# 2. Enrich with context\ncat > error-analysis.md << EOF\n**Error:**\n$(cat $ERROR_LOG)\n\n**Recent Commits:**\n$(git log --oneline -3)\n\n**Changed Files:**\n$(git diff --name-only HEAD~1)\n\n**File Contents:**\n$(for file in $(git diff --name-only HEAD~1); do\n    echo \"**$file:**\"\n    cat $file\ndone)\nEOF\n\n# 3. AI diagnosis\nai \"Diagnose and fix:\n$(cat error-analysis.md)\n\nProvide:\n1. Root cause\n2. Exact fix commands\n3. How to prevent recurrence\"\n\n# 4. Apply and validate\n# [Review AI output]\n# [Execute suggested fixes]\n# [Run tests]\n# [Commit]\n```\n\n**When to Use [Error Resolution](#error-resolution)**\n\n- **CI/CD Failures**: Diagnose build, test, or deployment failures\n- **Local Development Errors**: Debug unexpected errors during development\n- **Configuration Issues**: Resolve environment or configuration problems\n- **Dependency Conflicts**: Analyze and resolve version conflicts\n- **Integration Failures**: Debug issues with external services or APIs\n\n**Complete Implementation**: See [examples/error-resolution/](examples/error-resolution/) for:\n- Reusable templates for error context collection and AI prompts\n- A redacted, source-linked application failure-context recorder\n- Optional correlation from application failures to separate agent-run traces\n- Executable redaction and persistence checks\n\n**Anti-pattern: Blind Diagnosis**\n\nSending only the error message to AI without surrounding context.\n\n```bash\n# ❌ Bad: No context\nai \"Fix error: Process completed with exit code 1\"\n```\n\n**Why it's problematic**: AI cannot diagnose the issue without seeing:\n- What command failed\n- Recent changes that might have caused it\n- File contents or configuration\n- System environment\n\n**Instead, provide full context:**\n\n```bash\n# ✅ Good: Comprehensive context\nai \"Fix this error:\n\nError: Process completed with exit code 1\n\nCommand that failed: terraform fmt -check -recursive\nFiles affected: main.tf, outputs.tf\n\nRecent change:\n$(git log -1 --oneline)\n\nFile content:\n$(cat terraform/main.tf)\n\nEnvironment: Terraform v1.6.0\"\n```\n\n**Anti-pattern: Brittle Fixes**\n\nApplying AI-suggested fixes without validation or rollback strategy.\n\n```bash\n# ❌ Bad: Apply without review or rollback\nai \"Fix this error\" | bash\n```\n\n**Why it's problematic**:\n- AI suggestions may introduce new bugs\n- May break existing functionality\n- Could make security or data loss mistakes\n- No rollback strategy if fix fails\n\n**Instead, validate fixes before applying:**\n\n```bash\n# ✅ Good: Validate before applying with rollback\ngit stash push -m \"Pre-fix checkpoint\"\n\n# Generate fix\nai \"Fix this error\" > proposed-fix.sh\n\n# Review the proposed changes\ncat proposed-fix.sh\n\n# Apply fix\nbash proposed-fix.sh\n\n# Verify changes\ngit diff\n\n# Run tests to validate\n./run-tests.sh\n\n# Commit or rollback\nif [ $? -eq 0 ]; then\n    git add .\n    git commit -m \"fix: [description]\"\n    git stash drop\nelse\n    git stash pop\n    echo \"Fix failed validation, rolled back\"\nfi\n```",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#error-resolution"
    },
    {
      "id": "model-routing",
      "name": "Model Routing",
      "maturity": "Advanced",
      "type": "Development",
      "category": "development",
      "shortDescription": "Match task requirements to model capability, context, latency, and cost",
      "dependencies": [
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        }
      ],
      "related": [
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        },
        {
          "name": "Incremental Generation",
          "id": "incremental-generation"
        },
        {
          "name": "Adversarial Evaluator",
          "id": "adversarial-evaluator"
        }
      ],
      "bodyMarkdown": "**Description**: Route each task to a model whose capability, context, latency, and cost profile matches the work.\n\n\nThe compatibility anchor above preserves inbound links to the former catalog entry. The revised name describes the decision being automated: choose a model route from explicit task requirements instead of filling the largest available context window.\n\n**Routing Policy**\n\nKeep model identifiers in configuration and route on durable capabilities:\n\n```yaml\n# .ai/model-routing.yml\nroutes:\n  - when: {risk: low, context_tokens: \"<8000\", modality: text}\n    profile: fast-low-cost\n  - when: {risk: medium, context_tokens: \"<64000\", requires_tools: true}\n    profile: balanced-agent\n  - when: {risk: high, requires_independent_judge: true}\n    profile: strongest-reasoner\n\nprofiles:\n  fast-low-cost: {model_env: FAST_MODEL, max_turns: 4}\n  balanced-agent: {model_env: AGENT_MODEL, max_turns: 20}\n  strongest-reasoner: {model_env: REVIEW_MODEL, max_turns: 8}\n```\n\nRecord the route and rationale with the task so a reviewer can reproduce the choice. Route high-risk output through an independent [Adversarial Evaluator](#adversarial-evaluator); model routing chooses a producer, not its own judge.\n\n**Anti-pattern: Maximal Routing**\n\nSending every task to the largest, most expensive model increases cost and latency without improving routine edits. Route by measured requirements and fall back only when deterministic checks show the cheaper profile cannot complete the task.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#model-routing"
    },
    {
      "id": "code-research",
      "name": "Code Research",
      "maturity": "Intermediate",
      "type": "Workflow",
      "category": "development",
      "shortDescription": "Answer technical questions with isolated executable experiments",
      "dependencies": [
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        }
      ],
      "related": [
        {
          "name": "Parallel Agents",
          "id": "parallel-agents"
        },
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        },
        {
          "name": "Adversarial Evaluator",
          "id": "adversarial-evaluator"
        }
      ],
      "bodyMarkdown": "**Description**: Answer technical questions with isolated agent-run experiments that produce executable, reviewable evidence.\n\n\n**Source**: Simon Willison, \"[Code research projects with async coding agents](https://simonwillison.net/2025/Nov/6/async-code-research/),\" November 6, 2025\n\nThe compatibility anchor above preserves inbound links to the former catalog entry. Asynchrony is an execution option; executable evidence is the defining mechanism.\n\n**Research Contract**\n\nPut each question in a disposable repository or worktree, require a runnable proof, and keep production secrets out of the environment:\n\n```markdown\n# research-question.md\nQuestion: Can Redis Streams sustain 10,000 concurrent notification subscribers?\n\nDeliverables:\n1. Minimal reproducible benchmark\n2. Pinned dependencies and exact run command\n3. Raw measurements plus machine/environment metadata\n4. Conclusion that names limits and failed approaches\n\nDone check: ./run-benchmark.sh && ./verify-results.sh\n```\n\nRun independent investigations in parallel when useful, then have a fresh reviewer execute the artifacts rather than accepting the research agent's narrative. A result that cannot be rerun is a hypothesis, not evidence.\n\n**Complete Example**: See [examples/code-research/](examples/code-research/) for repository setup, research prompt templates, result parsing, and executable investigation examples.\n\n**Anti-pattern: Narrative Research**\n\nAccepting a confident prose answer without runnable artifacts preserves the model's hallucinations. Require code, pinned inputs, raw results, and a deterministic reproduction command.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#code-research"
    },
    {
      "id": "bounded-autonomy",
      "name": "Bounded Autonomy",
      "maturity": "Advanced",
      "type": "Workflow",
      "category": "development",
      "shortDescription": "Bound agent loops by turns, spend, time, stalls, and verification reach",
      "dependencies": [
        {
          "name": "Parallel Agents",
          "id": "parallel-agents"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        }
      ],
      "related": [
        {
          "name": "Parallel Agents",
          "id": "parallel-agents"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Agent Memory",
          "id": "agent-memory"
        }
      ],
      "bodyMarkdown": "**Description**: Cap autonomous loops by turns, spend, and wall-clock time, detect stalls and divergence, and emit a machine-readable evidence trail.\n\n\nAutonomy must not exceed verification reach. Set limits before the loop starts, keep each writer in an isolated worktree, and let deterministic checks—not the agent—decide whether the goal converged.\n\n**Bounded Loop Contract**\n\n```yaml\n# bounded-loop.yml\ncaps:\n  max_turns: 40\n  max_budget_usd: 5.00\n  max_wall_secs: 3600\nstop_conditions:\n  stall_window: 3\n  done_check: make verify\n  recoverable_exit_codes: [2, 124]\nstate:\n  per_agent_worktree: true\n  commit_on_phase_boundary: true\nevidence:\n  run_summary: run-summary.json\n  failure_trail: logs/\nedges:\n  human_escape_hatch: true\n  downstream_merge: ci_gate_then_human\n```\n\nThe wrapper enforces caps outside the model process. It aborts on the first exhausted cap, repeated no-progress turn, unrecoverable error, or divergence signal; it never raises its own budget. Humans own the upstream allow/deny policy and downstream merge.\n\n**Complete Example**: See [examples/bounded-autonomy/](examples/bounded-autonomy/) for a runnable loop wrapper, done check, stop hook, and settings template.\n\n**Anti-pattern: Unbounded Autonomy**\n\nA loop without turn, spend, time, and stall limits can consume resources while drifting from its goal. Allowing the same agent to write, declare completion, and merge also removes the independent control needed to contain that drift.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#bounded-autonomy"
    },
    {
      "id": "policy-generation",
      "name": "Policy Generation",
      "maturity": "Advanced",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Generate validated Cedar, Rego, OPA, or Gatekeeper policy-as-code",
      "dependencies": [
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        }
      ],
      "related": [
        {
          "name": "Security Sandbox",
          "id": "security-sandbox"
        },
        {
          "name": "Evidence Automation",
          "id": "evidence-automation"
        },
        {
          "name": "Centralized Rules",
          "id": "centralized-rules"
        }
      ],
      "bodyMarkdown": "**Description**: Convert natural-language policy intent or runtime context into validated policy-as-code such as Cedar, Rego, OPA, and Gatekeeper.\n\n\nGenerate policy and its validation inputs together. Treat model output as a candidate artifact until the policy engine parses it and positive, negative, and boundary tests pass.\n\n```bash\nai \"Convert this requirement into Cedar policy plus allow/deny boundary tests:\nOnly production deployers may update production services.\" > candidate-policy.txt\n\n# Extract the reviewed policy, then let Cedar arbitrate validity.\ncedar validate --schema schema.cedarschema production.cedar\ncedar authorize --policies production.cedar --entities entities.json --request request.json\n```\n\nIndustry implementations also describe the mechanism as *NL2Cedar*, an *OPA AI assistant*, or a dynamic policy generator. The canonical name stays vendor-neutral and the output stays policy-as-code.\n\n**Complete Implementation**: See [examples/policy-generation/](examples/policy-generation/) for Cedar and Rego templates, compliance mapping, generation scripts, and validation examples.\n\n**Anti-pattern: Untested Policies**\n\nDeploying generated policy without parser validation and adversarial allow/deny tests can silently grant access or block legitimate operations. A plausible policy explanation is not executable proof.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#policy-generation"
    },
    {
      "id": "evidence-automation",
      "name": "Evidence Automation",
      "maturity": "Advanced",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Continuously collect dated, audit-ready control evidence",
      "dependencies": [
        {
          "name": "Policy Generation",
          "id": "policy-generation"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        }
      ],
      "related": [
        {
          "name": "Policy Generation",
          "id": "policy-generation"
        },
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Centralized Rules",
          "id": "centralized-rules"
        }
      ],
      "bodyMarkdown": "**Description**: Continuously collect control evidence from logs and configuration changes into dated, audit-ready records.\n\n\nDefine each control's deterministic collector, immutable source, evaluation command, and retention policy before asking AI to summarize it. The model may classify and explain evidence; it must not invent missing artifacts or author its own compliance verdict.\n\n```yaml\n# controls/evidence.yml\ncontrols:\n  - id: access-review\n    source: s3://audit-evidence/iam/\n    collector: ./collect-iam-changes.sh\n    verify: ./verify-iam-evidence.py\n    cadence: daily\n    required_fields: [commit, captured_at, actor, change, source_hash]\n```\n\nRun collectors on a schedule, hash normalized artifacts, and record explicit gaps. Generate the audit matrix from those records so every claim traces to a dated source and a reproducible check.\n\n**Anti-pattern: Synthetic Evidence**\n\nAsking a model to write an audit narrative when source records are missing creates assurance theater. Missing evidence must remain a visible failure or gap, never a model-filled placeholder.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#evidence-automation"
    },
    {
      "id": "centralized-rules",
      "name": "Centralized Rules",
      "maturity": "Advanced",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Synchronize organization-wide AI instructions from a central source",
      "dependencies": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Progressive Disclosure",
          "id": "progressive-disclosure"
        }
      ],
      "related": [
        {
          "name": "Codified Rules",
          "id": "codified-rules"
        },
        {
          "name": "Progressive Disclosure",
          "id": "progressive-disclosure"
        },
        {
          "name": "Evidence Automation",
          "id": "evidence-automation"
        }
      ],
      "bodyMarkdown": "**Description**: Enforce organization-wide AI instructions from a central source that synchronizes standard assistant configuration files.\n\n\nUse one versioned rules repository as the source of truth and generate tool-specific compatibility files from it:\n\n```text\nCentral Rules Repository\n  ├── base/universal-rules.md\n  ├── languages/python.md\n  └── frameworks/react.md\n           ↓ sync-ai-rules.sh\nProject Repository\n  ├── AGENTS.md\n  ├── CLAUDE.md\n  └── .cursorrules\n```\n\nValidate generated files in CI and record the source rules revision in each output. Products may call these *AI rules*, *AI instructions*, or an `AGENTS.md` source of truth; central synchronization is the stable mechanism.\n\n**Complete Implementation**: See the [sync strategy](examples/centralized-rules/sync-strategy/) for a Git-based implementation and the [gateway strategy](examples/centralized-rules/gateway-strategy/README-GATEWAY.md) for centralized filtering and logging.\n\n**Anti-pattern: Scattered Configuration**\n\nCopying assistant instructions independently into every repository causes silent drift and inconsistent enforcement. Generate compatibility files from one reviewed source and fail validation when local copies diverge.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#centralized-rules"
    },
    {
      "id": "drift-remediation",
      "name": "Drift Remediation",
      "maturity": "Advanced",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Detect declared-state drift and generate reviewable corrective patches",
      "dependencies": [
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        }
      ],
      "related": [
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Error Resolution",
          "id": "error-resolution"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        }
      ],
      "bodyMarkdown": "**Description**: Detect infrastructure drift against declared state and generate reviewable corrective patches with explicit approval gates.\n\n\nKeep detection deterministic and remediation reviewable. Capture the declared state, observed state, provider plan, and risk classification before generating a candidate correction:\n\n```bash\nterraform plan -detailed-exitcode -out=drift.tfplan || rc=$?\n[ \"${rc:-0}\" -eq 2 ] || exit \"${rc:-0}\"\nterraform show -json drift.tfplan > drift.json\n\nai \"Propose the smallest Terraform patch for drift.json.\nDo not apply it. Identify destructive changes and required approvals.\" > remediation.md\n\nterraform plan -out=candidate.tfplan  # deterministic re-check after review\n```\n\nOnly a human-approved pipeline applies the resulting plan. The agent that proposes a patch cannot approve or apply it.\n\n**Complete Implementation**: See [examples/drift-remediation/](examples/drift-remediation/) for drift detection, risk classification, corrective plans, and approval controls.\n\n**Anti-pattern: Blind Reconciliation**\n\nAutomatically applying a generated correction can destroy intentionally changed resources or propagate a compromised desired state. Preserve the diff, classify destructive actions, and require approval before apply.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#drift-remediation"
    },
    {
      "id": "debt-forecasting",
      "name": "Debt Forecasting",
      "maturity": "Intermediate",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Forecast maintenance burden from code and repository trends",
      "dependencies": [
        {
          "name": "Guided Refactoring",
          "id": "guided-refactoring"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        }
      ],
      "related": [
        {
          "name": "Guided Refactoring",
          "id": "guided-refactoring"
        },
        {
          "name": "Tool Integration",
          "id": "tool-integration"
        },
        {
          "name": "Model Routing",
          "id": "model-routing"
        }
      ],
      "bodyMarkdown": "**Description**: Forecast maintenance burden from code, dependency, coverage, and documentation trends so teams can prioritize technical debt.\n\n\nCombine deterministic trend data with an AI-assisted explanation instead of asking a model to guess debt from a snapshot:\n\n```bash\npython -m radon cc src --json > metrics/complexity.json\npython -m pytest --cov=src --cov-report=json:metrics/coverage.json\ngit log --since='90 days ago' --numstat > metrics/churn.txt\n\nai \"Rank maintenance risks using the attached complexity, coverage, churn,\ndependency, and documentation-drift trends. Cite the metric behind every rank.\" \\\n  > debt-forecast.md\n```\n\nReview forecast accuracy against later incidents and maintenance work, then adjust weights rather than treating model rankings as objective measurements.\n\n**Complete Implementation**: See [examples/debt-forecasting/](examples/debt-forecasting/) for a technical-debt analysis and prioritized maintenance report.\n\n**Anti-pattern: Reactive Debt**\n\nWaiting for debt to cause outages or block delivery loses the lead time a trend forecast provides. A one-time subjective code review is also not a forecast; retain comparable measurements over time.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#debt-forecasting"
    },
    {
      "id": "guided-chaos",
      "name": "Guided Chaos",
      "maturity": "Advanced",
      "type": "Operations",
      "category": "operations",
      "shortDescription": "Generate hypothesis-driven chaos experiments with explicit safety controls",
      "dependencies": [
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        }
      ],
      "related": [
        {
          "name": "Agent Observability",
          "id": "agent-observability"
        },
        {
          "name": "Bounded Autonomy",
          "id": "bounded-autonomy"
        },
        {
          "name": "Error Resolution",
          "id": "error-resolution"
        }
      ],
      "bodyMarkdown": "**Description**: Generate hypothesis-driven chaos experiments from architecture and dependency evidence with explicit blast-radius and recovery controls.\n\n\nThe compatibility anchor above preserves inbound links to the former catalog entry. The name emphasizes that AI proposes a bounded experiment; it does not receive open-ended authority to inject faults.\n\n```yaml\n# chaos-experiment.yml\nhypothesis: Checkout remains available when one payment worker is terminated.\nsteady_state_check: ./checks/checkout-slo.sh\nfault: terminate_one_payment_worker\nblast_radius: {environment: staging, max_instances: 1}\nabort_when: {error_rate_percent: 2, latency_p95_ms: 800}\nrecovery: ./recovery/restore-payment-worker.sh\napproval_required: true\n```\n\nExecute the steady-state check before and after injection, stream telemetry through [Agent Observability](#agent-observability), and abort deterministically when a guardrail trips. See the [chaos scenario examples](examples/guided-chaos/) for hypothesis and recovery templates.\n\n**Anti-pattern: Random Chaos**\n\nInjecting faults without a falsifiable hypothesis, bounded target, abort condition, and tested recovery path creates an outage rather than an experiment.",
      "githubUrl": "https://github.com/PaulDuvall/ai-development-patterns#guided-chaos"
    }
  ]
};
