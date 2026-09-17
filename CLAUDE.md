# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the AI Development Patterns repository - a comprehensive collection of patterns for building software with AI assistance. The patterns are organized by implementation maturity (Beginner/Intermediate/Advanced) and development lifecycle phases (Foundation → Development → Operations).

## Repository Structure

```
├── README.md                    # Main pattern documentation
├── pattern-spec.md              # Pattern creation specification and formatting rules
├── PATTERN_MIGRATION_GUIDE.md   # Naming/anchor migration reference (historical + mapping)
├── index.html                   # GitHub Pages landing page
├── docs/                        # Additional documentation
├── examples/                    # Working implementations of stable patterns
├── experiments/                 # Experimental patterns + examples
├── scripts/                     # Repo automation scripts (validation, updates)
├── tests/                       # Pytest-based validation suite
├── verification/                # Machine-verified pattern adoption evidence (see verification/README.md)
└── .github/                     # GitHub Actions workflows
```

## Key Architectural Principles

### Pattern Architecture
- **Three-tier organization**: Foundation → Development → Operations patterns
- **Dependency-driven**: Patterns have explicit dependencies shown in the reference table
- **Maturity-based progression**: Beginner patterns enable Intermediate, which enable Advanced
- **Anti-pattern inclusion**: Every pattern includes what NOT to do with specific examples

### Pattern Reference System
- **Hyperlinked navigation**: Every pattern reference must link to its section using `#pattern-name-in-lowercase-with-hyphens`
- **Comprehensive reference table**: See "Complete Pattern Reference" in `README.md`
- **Related patterns**: Each pattern explicitly lists dependencies and related patterns

### Documentation Standards
- **Specification compliance**: All patterns follow the structure defined in `pattern-spec.md`
- **Required sections**: Maturity level, description, related patterns, core implementation, anti-pattern
- **Code examples**: Realistic, runnable examples with actual commands and file paths
- **Source attribution**: External patterns include source URLs

## Working with Patterns

### Adding New Patterns
1. **Follow pattern-spec.md**: Strict adherence to the specification format is required
2. **Update reference table**: Add the pattern to the "Complete Pattern Reference" table with proper dependencies
3. **Add to correct section**: Add the full pattern under `README.md` headings: "Foundation Patterns", "Development Patterns", or "Operations Patterns"
4. **Include anti-pattern**: Every pattern must show what NOT to do
5. **Link related patterns**: Use proper markdown hyperlinks to related patterns

### Pattern Dependencies
- **Foundation patterns**: Establish team readiness, security, and basic AI integration
- **Development patterns**: Daily workflows for AI-assisted coding
- **Operations patterns**: CI/CD, security, compliance, and production management

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
- **Isolation-first**: Security Sandbox pattern emphasizes network isolation and secret management
- **Default-deny**: Container configurations use `network_mode: none` by default
- **Parallel safety**: Multiple agent patterns include conflict resolution and coordination

### Advanced Patterns
- **Multi-agent coordination**: Parallel Agents pattern includes shared memory and merge automation
- **Enterprise focus**: Operations patterns target compliance, security, and production concerns
- **Scalability considerations**: Patterns support both small teams and enterprise deployments

When modifying this repository, maintain the established pattern structure, ensure all hyperlinks work correctly, and follow the dependency relationships defined in the reference table.

## Task Tracking

Tasks live in `.tasks/backlog.jsonl` — an append-only JSONL file, one task per line, git-tracked. There is no daemon and no database: the file is the record and git is the history.

Do NOT use TodoWrite, TaskCreate, markdown TODO lists, or `bd`/beads — this repo migrated off beads on 2026-08-17.

**A task's state is its LAST line.** The file is append-only, so `grep '"status": *"open"'` also matches tasks that were later closed, over-reporting the open set. Always fold last-line-wins:

```bash
python3 -c "import json;last={};[last.__setitem__(t['id'],t) for t in map(json.loads,filter(str.strip,open('.tasks/backlog.jsonl')))];print('\n'.join(f\"{i}  {t['title'][:68]}\" for i,t in last.items() if t['status']=='open'))"
```

Close a task by APPENDING a new line with `status` set to `closed`; never edit or delete an existing line. Work discovered while doing another task gets its own line with `discovered_from` set to the parent id.

**Schema:** `{id, title, status, blocks[], depends_on[], spec_ref, created, priority, description, discovered_from?}` — `status` is `open` or `closed`; `priority` is 1 (most urgent) to 4; a task is ready when every id in `depends_on` is closed. Issue ids keep their original beads form so existing commit messages still resolve.

The full beads history is archived verbatim at `.tasks/beads-archive.jsonl`.
