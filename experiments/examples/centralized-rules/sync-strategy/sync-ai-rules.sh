#!/bin/bash
# sync-ai-rules.sh
# Synchronize centralized AI rules to local configuration files
# Supports: CLAUDE.md, AGENTS.md, .cursorrules

set -e

# Configuration
CONFIG_FILE=".ai/sync-config.json"
VERSION_FILE=".ai/.rules-version"
CACHE_DIR=".ai/.rules-cache"
DEFAULT_CENTRAL_REPO="git@github.com:yourorg/ai-rules-central.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flags
FORCE=false
CHECK_ONLY=false
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) FORCE=true; shift ;;
    --check-only) CHECK_ONLY=true; shift ;;
    --quiet) QUIET=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

log() {
  if [ "$QUIET" != "true" ]; then
    echo -e "${GREEN}[sync-ai-rules]${NC} $1"
  fi
}

warn() {
  echo -e "${YELLOW}[sync-ai-rules]${NC} $1" >&2
}

error() {
  echo -e "${RED}[sync-ai-rules]${NC} $1" >&2
  exit 1
}

# Load configuration
load_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    warn "No $CONFIG_FILE found, creating default..."
    mkdir -p .ai
    cat > "$CONFIG_FILE" << 'EOF'
{
  "centralRepo": "git@github.com:yourorg/ai-rules-central.git",
  "rules": {
    "base": ["universal-rules"],
    "languages": "auto-detect",
    "frameworks": "auto-detect"
  },
  "outputFormats": ["CLAUDE.md", "AGENTS.md", ".cursorrules"]
}
EOF
    log "Created default config at $CONFIG_FILE - please customize!"
  fi

  # Parse JSON config (requires jq for production, simple parsing for demo)
  if command -v jq >/dev/null 2>&1; then
    CENTRAL_REPO=$(jq -r '.centralRepo // empty' "$CONFIG_FILE")
    OUTPUT_FORMATS=$(jq -r '.outputFormats[]' "$CONFIG_FILE" 2>/dev/null || echo "CLAUDE.md")
  else
    # Fallback: simple grep-based parsing
    CENTRAL_REPO=$(grep -o '"centralRepo"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
    OUTPUT_FORMATS="CLAUDE.md AGENTS.md .cursorrules"
  fi

  CENTRAL_REPO=${CENTRAL_REPO:-$DEFAULT_CENTRAL_REPO}
}

# Clone or update central rules repository
sync_central_repo() {
  log "Syncing central rules repository..."

  if [ -d "$CACHE_DIR" ]; then
    if [ "$FORCE" = "true" ]; then
      log "Force mode: removing existing cache..."
      rm -rf "$CACHE_DIR"
    else
      log "Updating existing cache..."
      (cd "$CACHE_DIR" && git pull --quiet) || error "Failed to update cache"
      return 0
    fi
  fi

  log "Cloning $CENTRAL_REPO..."
  mkdir -p .ai
  git clone --depth 1 --quiet "$CENTRAL_REPO" "$CACHE_DIR" || error "Failed to clone central repo"
}

# Detect programming languages in the repository
detect_languages() {
  local languages=()

  # Python
  if ls *.py pyproject.toml requirements.txt setup.py 2>/dev/null | grep -q .; then
    languages+=("python")
  fi

  # TypeScript
  if ls tsconfig.json 2>/dev/null | grep -q . || \
     grep -q '"@types/' package.json 2>/dev/null; then
    languages+=("typescript")
  fi

  # JavaScript (without TypeScript)
  if [ ! -f tsconfig.json ] && ls package.json 2>/dev/null | grep -q .; then
    languages+=("javascript")
  fi

  # Go
  if ls go.mod go.sum 2>/dev/null | grep -q .; then
    languages+=("go")
  fi

  # Rust
  if ls Cargo.toml 2>/dev/null | grep -q .; then
    languages+=("rust")
  fi

  # Java
  if ls pom.xml build.gradle 2>/dev/null | grep -q .; then
    languages+=("java")
  fi

  # Ruby
  if ls Gemfile *.gemspec 2>/dev/null | grep -q .; then
    languages+=("ruby")
  fi

  echo "${languages[@]}"
}

# Detect frameworks
detect_frameworks() {
  local frameworks=()

  # React
  if grep -q '"react"' package.json 2>/dev/null; then
    frameworks+=("react")
  fi

  # Vue
  if grep -q '"vue"' package.json 2>/dev/null; then
    frameworks+=("vue")
  fi

  # Next.js
  if grep -q '"next"' package.json 2>/dev/null; then
    frameworks+=("nextjs")
  fi

  # Django
  if ls manage.py 2>/dev/null | grep -q . || \
     grep -q '"django"' requirements.txt pyproject.toml 2>/dev/null; then
    frameworks+=("django")
  fi

  # FastAPI
  if grep -q '"fastapi"' requirements.txt pyproject.toml 2>/dev/null; then
    frameworks+=("fastapi")
  fi

  # Express
  if grep -q '"express"' package.json 2>/dev/null; then
    frameworks+=("express")
  fi

  # Flask
  if grep -q '"flask"' requirements.txt pyproject.toml 2>/dev/null; then
    frameworks+=("flask")
  fi

  echo "${frameworks[@]}"
}

# Build combined rules document
build_rules() {
  local output_file=$1
  local languages=($(detect_languages))
  local frameworks=($(detect_frameworks))

  log "Detected languages: ${languages[*]:-none}"
  log "Detected frameworks: ${frameworks[*]:-none}"

  # Start document
  {
    cat << 'HEADER'
# AI Development Rules
# Auto-generated from central rules - DO NOT EDIT MANUALLY
HEADER
    echo "# Last synced: $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo "# Rules version: $(cd "$CACHE_DIR" && git rev-parse --short HEAD)"
    echo "# Source: $CENTRAL_REPO"
    echo ""
  } > "$output_file"

  # Add base rules
  log "Adding base rules..."
  if [ -f "$CACHE_DIR/base/universal-rules.md" ]; then
    cat "$CACHE_DIR/base/universal-rules.md" >> "$output_file"
    echo -e "\n---\n" >> "$output_file"
  fi

  # Add language-specific rules
  for lang in "${languages[@]}"; do
    if [ -f "$CACHE_DIR/languages/$lang.md" ]; then
      log "Adding $lang rules..."
      cat "$CACHE_DIR/languages/$lang.md" >> "$output_file"
      echo -e "\n---\n" >> "$output_file"
    fi
  done

  # Add framework-specific rules
  for framework in "${frameworks[@]}"; do
    if [ -f "$CACHE_DIR/frameworks/$framework.md" ]; then
      log "Adding $framework rules..."
      cat "$CACHE_DIR/frameworks/$framework.md" >> "$output_file"
      echo -e "\n---\n" >> "$output_file"
    fi
  done

  # Add footer
  {
    echo ""
    echo "---"
    echo "To update these rules, run: ./sync-ai-rules.sh"
  } >> "$output_file"
}

# Check if rules are current
check_rules_current() {
  if [ ! -f "$VERSION_FILE" ]; then
    return 1  # No version file = outdated
  fi

  local current_version=$(cat "$VERSION_FILE")
  local latest_version=$(cd "$CACHE_DIR" && git rev-parse HEAD)

  if [ "$current_version" != "$latest_version" ]; then
    return 1  # Version mismatch = outdated
  fi

  return 0  # Current
}

# Main sync process
main() {
  log "Starting AI rules synchronization..."

  # Load configuration
  load_config

  # Sync central repository
  sync_central_repo

  # Check-only mode
  if [ "$CHECK_ONLY" = "true" ]; then
    if check_rules_current; then
      log "✅ Rules are current"
      exit 0
    else
      error "❌ Rules are outdated. Run: ./sync-ai-rules.sh"
    fi
  fi

  # Generate output files
  for format in $OUTPUT_FORMATS; do
    log "Generating $format..."
    build_rules "$format"
  done

  # Update version file
  (cd "$CACHE_DIR" && git rev-parse HEAD) > "$VERSION_FILE"

  log "✅ Sync complete! Generated: $OUTPUT_FORMATS"
  log "Rules are now ready for:"
  echo "  - Claude Code (reads CLAUDE.md)"
  echo "  - Cursor IDE (reads .cursorrules)"
  echo "  - Gemini/other tools (read AGENTS.md)"
}

main
