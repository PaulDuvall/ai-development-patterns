# Asynchronous Research - Complete Implementation Guide

This directory contains a complete implementation guide for the **Asynchronous Research** pattern based on Simon Willison's approach to using fire-and-forget coding agents for autonomous code investigations.

**Pattern Source**: Simon Willison, "[Code research projects with async coding agents](https://simonwillison.net/2025/Nov/6/async-code-research/)", November 6, 2025

## Overview

The Asynchronous Research pattern enables developers to conduct 2-3 autonomous code investigations per day with minimal human oversight. Fire research prompts at async coding agents, let them work autonomously for 10-30 minutes, then review results when complete.

**Key Insight**: *"The great thing about questions about code is that they can often be definitively answered by writing and executing code."* - Simon Willison

## Directory Structure

```
asynchronous-research/
├── README.md                          # This file
├── setup/
│   ├── create-research-repo.sh       # Script to initialize research repository
│   ├── claude-code-config.md         # Configure Claude Code for research
│   ├── gemini-jules-config.md        # Configure Gemini Jules for research
│   └── platform-comparison.md        # Compare async agent platforms (2025)
├── prompt-templates/
│   ├── performance-benchmark.md      # Template for benchmark research
│   ├── feasibility-study.md          # Template for "is this possible?"
│   ├── library-comparison.md         # Template for comparative analysis
│   └── integration-proof.md          # Template for "can A work with B?"
├── example-research-tasks/
│   ├── redis-notifications/          # Proof-of-concept example
│   ├── markdown-comparison/          # Simon's benchmark example
│   └── webassembly-compilation/      # Complex multi-step research
└── automation/
    ├── summarize-workflow.yml        # GitHub Action to auto-index research
    ├── AGENTS.md.template            # Template for agent guidance
    └── result-parser.py              # Extract findings from agent output
```

## Quick Start

### 1. Create Dedicated Research Repository

```bash
# Run the setup script
./setup/create-research-repo.sh my-research

# Or manually:
gh repo create my-research --private
cd my-research

# Initialize with README
cat > README.md << 'EOF'
# Research Repository

Autonomous code investigations using async coding agents.

## Pattern

This repository follows the Asynchronous Research pattern from
[AI Development Patterns](https://github.com/paulduvall/ai-development-patterns).

Each folder contains one research task with autonomous agent findings.
EOF

git add README.md
git commit -m "Initial commit"
git push -u origin main
```

### 2. Configure Your Async Agent Platform

Choose your platform and follow the configuration guide:

- **Claude Code (web)**: See [setup/claude-code-config.md](setup/claude-code-config.md)
- **Gemini Jules**: See [setup/gemini-jules-config.md](setup/gemini-jules-config.md)
- **Codex Cloud**: Similar to Claude Code configuration
- **GitHub Copilot**: Follow GitHub Enterprise setup

**Critical**: Enable unrestricted network access for your research repo. This is safe because there are no production secrets.

### 3. Choose a Research Question

Good research questions are:
- **Specific** and testable
- **Answerable** by writing and executing code
- **Focused** on a single investigation
- **Deliverable** with clear outputs (code, charts, reports)

**Examples from Simon:**
- "Could Redis Streams handle 10k concurrent notification subscribers?"
- "How do 7 Python Markdown libraries compare on performance?"
- "Can cmarkgfm C extension compile for Pyodide WebAssembly?"

### 4. Use a Prompt Template

Start with a template from `prompt-templates/` and customize:

**Performance Benchmark Template:**
```
Work in new folder: [folder-name]/

[Describe system to build and test]

Measure and report:
- [Metric 1]
- [Metric 2]
- [Metric 3]

Produce [deliverables: code, charts, report].
```

**Library Comparison Template:**
```
Work in new folder: [folder-name]/

Compare these libraries: [lib1, lib2, lib3]

For each library:
1. [Analysis task]
2. [Performance test]
3. [Feature comparison]

Output: README.md with charts, raw data as JSON.
```

See [prompt-templates/](prompt-templates/) for complete templates.

### 5. Fire and Forget

Submit your research prompt to your async agent platform:

1. **Submit prompt** (2-3 paragraphs with clear deliverables)
2. **Agent works autonomously** (10-30 minutes typically)
3. **Receive notification** when PR/commit is ready
4. **Skim results** for key insights
5. **Merge if useful**, discard if not

**Simon's workflow**: "I'm firing off 2-3 code research projects a day right now. My own time commitment is minimal."

### 6. Review Results

When the agent completes:

**Do:**
- Skim the report for key insights
- Verify the research question was answered
- Check if findings are actionable
- Look for unexpected discoveries

**Don't:**
- Audit code line-by-line (it's exploratory)
- Expect production-quality code
- Get blocked on minor issues
- Worry about "slop" (AI-generated content is expected)

### 7. Build on Previous Research

Research tasks can reference each other:

```bash
# Research 1: Prove Node.js can run Pyodide
# Result: node-pyodide/

# Research 2: Build on finding
# Prompt: "Building on the node-pyodide example, compile cmarkgfm
# C extension for Pyodide and prove it works in Node.js"
# Result: cmarkgfm-in-pyodide/
```

Create `AGENTS.md` in your repo with guidance for future runs:
```markdown
# Agent Guidance

## Research Standards
- Create one folder per research task
- Include README.md with findings
- Generate charts for performance data
- Provide runnable code examples

## Tech Stack Preferences
- Python: Use pytest for tests
- JavaScript: Use Node.js 20+
- Charts: Use matplotlib or chart.js
```

## Example Research Tasks

### Performance Benchmark: Redis Notifications

**Research Question**: "Can Redis Streams handle 10k concurrent notification subscribers?"

**Prompt** (see [example-research-tasks/redis-notifications/prompt.md](example-research-tasks/redis-notifications/prompt.md)):
```
Work in new folder: redis-notifications/

Build Redis Streams notification system.
Simulate 10,000 users receiving 100 notifications/second.
Run for 1 hour and measure:
- Memory usage over time
- P95 latency for delivery
- Behavior under network partition
- Recovery after Redis restart

Produce Python code, charts, detailed markdown report.
```

**Expected Deliverables**:
- `publisher.py` - Notification publishing script
- `subscriber.py` - Subscriber simulation
- `benchmark.py` - Performance measurement
- `results/` - Charts and raw data
- `README.md` - Findings and analysis

### Library Comparison: Python Markdown

**Research Question**: "How do Python Markdown libraries compare on performance?"

**Prompt** (see [example-research-tasks/markdown-comparison/prompt.md](example-research-tasks/markdown-comparison/prompt.md)):

Simon's actual prompt:
```
Create a performance benchmark and feature comparison report on PyPI cmarkgfm
compared to other popular Python markdown libraries—check all of them out from
github and read the source to get an idea for features, then design and run a
benchmark including generating some charts, then create a report in a new
python-markdown-comparison folder. Make sure the performance chart images are
directly displayed in the README.md in the folder.
```

**Results from Simon's research**:
- Agent found 7 libraries automatically
- cmarkgfm was 10-52x faster (C implementation)
- Generated comparison charts
- Feature matrix from source analysis

### Feasibility Study: WebAssembly Compilation

**Research Question**: "Can cmarkgfm (C extension) run in Pyodide WebAssembly?"

**Prompt** (see [example-research-tasks/webassembly-compilation/prompt.md](example-research-tasks/webassembly-compilation/prompt.md)):
```
Figure out how to get the cmarkgfm markdown library for Python working
in pyodide. This will be hard because it uses C so you will need to
compile it to pyodide compatible webassembly somehow.

Write a report on your results plus code to a new cmarkgfm-in-pyodide
directory. Test it using pytest to exercise a node.js test script that
calls pyodide.
```

**Simon's approach when stuck**:
> "Complete this project, actually run emscripten, I do not care how long it takes"

**Result**: 88.4KB `.whl` file with working C extension in WebAssembly.

## Platform Comparison (November 2025)

| Platform | Free Tier | Network Access | Setup Time | Best For |
|----------|-----------|----------------|------------|----------|
| **Claude Code (web)** | $250 credits ($20/month users, until Nov 18) | Configurable | 5 min | Complex research, multi-file |
| **Gemini Jules** | Free tier | Default unrestricted | 2 min | Quick POCs, exploration |
| **Codex Cloud** | Pay-as-you-go | Configurable | 10 min | Enterprise workflows |
| **GitHub Copilot Agent** | Enterprise | Configurable | 15 min | GitHub integration |

See [setup/platform-comparison.md](setup/platform-comparison.md) for detailed comparison.

## Success Metrics

**From Simon's 2 weeks of practice (Nov 2025)**:

- **13 projects** in 2 weeks (~1/day average)
- **2-3 tasks/day** at peak productivity
- **Minutes per task** of human time (prompt + review)
- **10-30 minutes** typical agent execution
- **Frequent useful results** informing decisions

## Integration with Development Workflow

### Before Choice Generation

Research validates which options are technically feasible:

```bash
# Question: Should we use Redis or RabbitMQ for notifications?

# Research Task 1: Redis proof-of-concept
# Research Task 2: RabbitMQ proof-of-concept

# Compare results → Make informed choice
```

### Before Planned Implementation

Research provides real data for planning:

```bash
# Question: How long will Markdown rendering optimization take?

# Research: Benchmark current vs. alternatives
# Result: cmarkgfm is 10-52x faster
# Planning: 2-day task to integrate cmarkgfm
```

### With Context Persistence

Archive research for future sessions:

```bash
# Add to .claude/context.md or similar:
## Research Findings

### Markdown Performance (2025-11)
cmarkgfm is 10-52x faster than alternatives. Use for production.
See: research-repo/python-markdown-comparison/
```

### With Parallel Agents

Run multiple research questions simultaneously:

```bash
# Fire 3 research tasks in parallel:
# 1. Redis vs RabbitMQ benchmarks
# 2. Authentication library comparison
# 3. Deployment strategy feasibility

# Review all results together → Make integrated decision
```

## Automation

### Auto-Generate Research Index

Install GitHub Action to automatically update README with summaries:

```bash
# Copy workflow
cp automation/summarize-workflow.yml .github/workflows/

# Install dependencies for LLM summarization
# Uses: cog, llm, llm-github-models (see Simon's approach)
```

See [automation/summarize-workflow.yml](automation/summarize-workflow.yml) for complete implementation.

### Result Parser

Extract structured findings from agent output:

```bash
# Parse agent results for key metrics
python automation/result-parser.py research-folder/

# Output: JSON with performance data, conclusions, warnings
```

## Anti-Patterns

### ❌ Blind Investigation

**Problem**: Vague prompts without clear goals.

```bash
# Bad
"Investigate Redis and try some stuff"

# Good
"Build Redis Streams POC. Measure: memory, P95 latency, partition behavior."
```

### ❌ Uncontained Slop

**Problem**: Publishing AI research directly to main docs without review.

**Solution**: Keep research in dedicated repo, mark as `noindex`.

### ❌ Secret Leakage

**Problem**: Running unrestricted agents on repos with production secrets.

**Solution**: Only use unrestricted access on dedicated, secret-free research repos.

### ❌ Proving Impossibility

**Problem**: Expecting agents to prove something can't be done.

**Simon's caveat**: "They can't prove something is impossible—just because the coding agent couldn't find a way doesn't mean it can't be done."

**Use for**: Proving feasibility, not impossibility.

## Troubleshooting

### Agent Gets Stuck

**Simon's approach**: Provide persistence prompts:
```
"Complete this project, actually run emscripten, I do not care how long it takes"
```

### Results Aren't Useful

**Check**:
- Was the research question specific enough?
- Did you provide clear deliverables?
- Is the agent exploring the right approach?

**Solution**: Refine prompt with more constraints.

### Agent Exceeds Context

**Solution**: Break into smaller research tasks:
```bash
# Instead of: "Benchmark all Python libraries"
# Do: "Benchmark top 3 Python Markdown libraries"
# Then: "Benchmark next 4 Python Markdown libraries"
```

### Network Access Issues

**Check**:
- Is network access enabled in agent settings?
- Are you running in the correct repository?
- Is the repository truly secret-free?

## References

- **Simon Willison's Article**: https://simonwillison.net/2025/Nov/6/async-code-research/
- **Simon's Research Repo**: https://github.com/simonw/research
- **AI Development Patterns**: [Main README](../../../README.md)
- **Related Patterns**:
  - [Parallel Agents](../../../README.md#parallel-agents)
  - [Context Persistence](../../../README.md#context-persistence)
  - [Choice Generation](../../../README.md#choice-generation)

## License

This example implementation is part of the AI Development Patterns project. The pattern itself is based on Simon Willison's public article and research repository.
