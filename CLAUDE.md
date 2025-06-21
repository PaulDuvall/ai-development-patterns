# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the AI Development Patterns repository - a comprehensive collection of patterns for building software with AI assistance. The patterns are organized by implementation maturity (Beginner/Intermediate/Advanced) and development lifecycle phases (Foundation → Development → Operations).

## Repository Structure

```
├── README.md                    # Main pattern documentation (3000+ lines)
├── pattern-spec.md             # Pattern creation specification and formatting rules
├── examples/                   # Working implementations of patterns
│   └── parallelized-ai-agents/ # Complete Docker-based parallel agent example
├── docs/                       # Additional documentation and specs
│   ├── specs.md               # Specification-driven development patterns
│   └── examples/              # Pattern implementation examples (au1a.md, pm7a.md, etc.)
├── sandbox/                    # AI security isolation examples
├── specs/                      # Example specifications (OpenAPI, Gherkin, etc.)
├── policies/                   # Policy-as-code examples (Cedar, OPA)
├── tests/                      # Testing pattern examples
├── monitoring/                 # Observability and chaos engineering examples
├── ops/                        # Operations pattern implementations
├── pipelines/                  # CI/CD pattern examples
└── deployment/                 # Deployment automation examples
```

## Key Architectural Principles

### Pattern Architecture
- **Three-tier organization**: Foundation → Development → Operations patterns
- **Dependency-driven**: Patterns have explicit dependencies shown in the reference table
- **Maturity-based progression**: Beginner patterns enable Intermediate, which enable Advanced
- **Anti-pattern inclusion**: Every pattern includes what NOT to do with specific examples

### Pattern Reference System
- **Hyperlinked navigation**: Every pattern reference must link to its section using `#pattern-name-in-lowercase-with-hyphens`
- **Comprehensive reference table**: Lines 50-89 in README.md contain the master pattern index
- **Related patterns**: Each pattern explicitly lists dependencies and related patterns

### Documentation Standards
- **Specification compliance**: All patterns follow the structure defined in `pattern-spec.md`
- **Required sections**: Maturity level, description, related patterns, core implementation, anti-pattern
- **Code examples**: Realistic, runnable examples with actual commands and file paths
- **Source attribution**: External patterns include source URLs

## Working with Patterns

### Adding New Patterns
1. **Follow pattern-spec.md**: Strict adherence to the specification format is required
2. **Update reference table**: Add new pattern to the table at lines 50-89 with proper dependencies
3. **Add to correct section**: Foundation (lines 270+), Development (lines 1400+), or Operations (lines 2500+)
4. **Include anti-pattern**: Every pattern must show what NOT to do
5. **Link related patterns**: Use proper markdown hyperlinks to related patterns

### Pattern Dependencies
- **Foundation patterns** (lines 270-1400): Establish team readiness, security, and basic AI integration
- **Development patterns** (lines 1400-2500): Daily workflows for AI-assisted coding
- **Operations patterns** (lines 2500+): CI/CD, security, compliance, and production management

### Content Guidelines
- **Kanban workflow assumed**: No sprint-based or fixed iteration references
- **Container-first examples**: Security patterns emphasize containerization and isolation
- **Real-world focus**: Examples use realistic scenarios (e.g., TaskFlow SaaS application)
- **Tool-agnostic**: Patterns work across different AI providers and development tools

## Development Workflow

### Repository Maintenance
- **Git workflow**: Standard GitHub flow with main branch
- **Commit format**: Use conventional commits with Claude Code attribution
- **ACP operations**: Always Add → Commit → Push for complete operations

### Example Implementations
- **Working examples**: `examples/` contains fully functional pattern implementations
- **Docker-based**: Primary example uses Docker Compose for agent isolation
- **Real dependencies**: Examples include actual Dockerfiles, requirements.txt, shell scripts

### Quality Standards
- **Hyperlink integrity**: All internal pattern references must be valid hyperlinks
- **Code accuracy**: All code examples must be syntactically correct and runnable
- **Specification compliance**: Changes to pattern structure must update pattern-spec.md

## Special Considerations

### Security Patterns
- **Isolation-first**: AI Security Sandbox pattern emphasizes network isolation and secret management
- **Default-deny**: Container configurations use `network_mode: none` by default
- **Parallel safety**: Multiple agent patterns include conflict resolution and coordination

### Advanced Patterns
- **Multi-agent coordination**: Parallelized AI Coding Agents pattern includes shared memory and merge automation
- **Enterprise focus**: Operations patterns target compliance, security, and production concerns
- **Scalability considerations**: Patterns support both small teams and enterprise deployments

When modifying this repository, maintain the established pattern structure, ensure all hyperlinks work correctly, and follow the dependency relationships defined in the reference table.