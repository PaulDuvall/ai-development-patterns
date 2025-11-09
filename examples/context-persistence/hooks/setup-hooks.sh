#!/bin/bash
# Setup AI Context Persistence Hooks for Claude Code
#
# This script configures Claude Code hooks for automatic context management

set -euo pipefail

PROJECT_ROOT="${1:-.}"
cd "$PROJECT_ROOT"

echo "Setting up AI Context Persistence hooks..."
echo ""

# Create directory structure
echo "📁 Creating directories..."
mkdir -p .ai/{memory,knowledge/{patterns,failures},hooks,archive}
mkdir -p .claude

# Copy memory templates
echo "📝 Creating memory schema templates..."
if [[ -f "examples/ai-context-persistence/templates/TODO.md" ]]; then
    cp -n examples/ai-context-persistence/templates/*.{md,log,json} .ai/memory/ 2>/dev/null || true
else
    # Create minimal templates
    cat > .ai/memory/TODO.md << 'EOF'
# Task Tracking

## Current Tasks

- [ ] Task description
  - **Status**: pending
  - **Dependencies**: none

## Completed

- [x] Completed task (YYYY-MM-DD)
EOF

    cat > .ai/memory/DECISIONS.log << 'EOF'
[YYYY-MM-DD HH:MM] Decision title
Rationale: Why this decision was made
Alternatives: What else was considered
Impact: What this affects
EOF

    cat > .ai/memory/NOTES.md << 'EOF'
# Session Notes

## Previously On...

[Session recap will go here]

---

## Session YYYY-MM-DD

**Context**: What you're working on
**Discoveries**: Key findings
**Blockers**: Current roadblocks
**Next Actions**: What to do next
EOF

    cat > .ai/memory/scratchpad.md << 'EOF'
# Scratchpad - Working Memory

## Current Exploration

[Active investigation notes]

### Hypothesis
[What you think might be happening]

### Evidence
- [Observation 1]
- [Observation 2]

### Next Steps
- [What to try next]
EOF
fi

# Copy hook scripts
echo "🔧 Installing hook scripts..."
SCRIPT_DIR="$(dirname "$0")"
cp "$SCRIPT_DIR"/{session-resume,session-end,post-edit-reminder,pre-compact}.sh .ai/hooks/
chmod +x .ai/hooks/*.sh

# Copy settings.json
echo "⚙️  Configuring Claude Code hooks..."
if [[ -f ".claude/settings.json" ]]; then
    echo "⚠️  .claude/settings.json already exists"
    echo "   Backup created at .claude/settings.json.backup"
    cp .claude/settings.json .claude/settings.json.backup
fi

cp "$SCRIPT_DIR/settings.json" .claude/settings.json

# Copy scripts
echo "📜 Installing context management scripts..."
if [[ -d "$SCRIPT_DIR/../scripts" ]]; then
    mkdir -p .ai/scripts
    cp "$SCRIPT_DIR/../scripts"/{session-resume,context-compact,knowledge}.sh .ai/scripts/ 2>/dev/null || true
    chmod +x .ai/scripts/*.sh 2>/dev/null || true
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Directory structure:"
echo "   .ai/memory/          - Memory schemas (TODO, DECISIONS, NOTES, scratchpad)"
echo "   .ai/knowledge/       - Knowledge patterns and failures"
echo "   .ai/hooks/           - Claude Code hook scripts"
echo "   .ai/scripts/         - Context management scripts"
echo "   .claude/settings.json - Hook configuration"
echo ""
echo "🔒 Security: Hooks require approval"
echo ""
echo "Next steps:"
echo "1. Start Claude Code:    claude"
echo "2. Review hooks:         /hooks"
echo "3. Approve trusted hooks"
echo "4. Restart Claude Code to activate"
echo ""
echo "📚 Documentation:"
echo "   .ai/hooks/README.md - Hook documentation"
echo "   Run: ./scripts/session-resume.sh to load context"
echo ""
