#!/bin/bash
# lifecycle-workflow.sh - Complete 9-stage AI Development Lifecycle

set -e

# Configuration
FEATURE_NAME=""
TARGET_STAGE=""
CONTEXT=""
PROMPTS_DIR="stage-prompts"
OUTPUT_DIR="lifecycle-output"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --feature NAME    Feature name to implement"
    echo "  --stage NUM       Run specific stage (1-9)"
    echo "  --context TEXT    Additional context for AI"
    echo "  --help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --feature \"JWT Authentication\""
    echo "  $0 --stage 6 --context \"implement-oauth2\""
}

log_stage() {
    echo -e "${BLUE}=== Stage $1: $2 ===${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --feature)
            FEATURE_NAME="$2"
            shift 2
            ;;
        --stage)
            TARGET_STAGE="$2"
            shift 2
            ;;
        --context)
            CONTEXT="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Stage 1: Problem Definition
run_stage_1() {
    log_stage 1 "Problem Definition"
    
    cat > "$OUTPUT_DIR/01-problem-statement.md" << EOF
# Problem Definition: $FEATURE_NAME

## Problem Statement
We need to implement $FEATURE_NAME to address the following business needs:

## Success Criteria
- [ ] Functional requirements met
- [ ] Non-functional requirements satisfied (performance, security, usability)
- [ ] Integration tests passing
- [ ] Production deployment successful

## Constraints
- Timeline: [To be defined]
- Budget: [To be defined]
- Technical: [To be defined]
- Compliance: [To be defined]

## Stakeholders
- Product Owner: [Name]
- Technical Lead: [Name]
- QA Lead: [Name]

Generated: $(date)
EOF

    log_success "Problem statement documented"
}

# Stage 2: Technical Planning
run_stage_2() {
    log_stage 2 "Technical Planning"
    
    cat > "$OUTPUT_DIR/02-technical-plan.md" << EOF
# Technical Planning: $FEATURE_NAME

## Architecture Overview
[AI will generate architecture diagram and component breakdown]

## Technology Stack
- Backend: [To be determined by AI]
- Frontend: [To be determined by AI]
- Database: [To be determined by AI]
- Infrastructure: [To be determined by AI]

## Integration Points
- External APIs: [To be identified]
- Internal services: [To be identified]
- Third-party libraries: [To be identified]

## Security Considerations
- Authentication: [To be defined]
- Authorization: [To be defined]
- Data protection: [To be defined]

## Performance Requirements
- Response time: [To be defined]
- Throughput: [To be defined]
- Scalability: [To be defined]

Generated: $(date)
EOF

    log_success "Technical plan created"
}

# Stage 3: Requirements Analysis
run_stage_3() {
    log_stage 3 "Requirements Analysis"
    
    cat > "$OUTPUT_DIR/03-requirements.md" << EOF
# Requirements Analysis: $FEATURE_NAME

## Functional Requirements
[AI will generate detailed functional requirements]

## Non-Functional Requirements

### Performance
- Response time: < 200ms for API calls
- Throughput: Support 1000 concurrent users
- Availability: 99.9% uptime

### Security
- Data encryption at rest and in transit
- Secure authentication and authorization
- Input validation and sanitization

### Usability
- Intuitive user interface
- Mobile responsive design
- Accessibility compliance (WCAG 2.1)

### Scalability
- Horizontal scaling capability
- Load balancing support
- Database optimization

Generated: $(date)
EOF

    log_success "Requirements documented"
}

# Stage 4: Issue Generation
run_stage_4() {
    log_stage 4 "Issue Generation"
    
    cat > "$OUTPUT_DIR/04-kanban-issues.json" << EOF
{
  "feature": "$FEATURE_NAME",
  "epic": {
    "title": "Implement $FEATURE_NAME",
    "description": "Complete implementation of $FEATURE_NAME with all required functionality",
    "acceptance_criteria": [
      "All functional requirements implemented",
      "Security requirements satisfied",
      "Performance benchmarks met",
      "Integration tests passing"
    ]
  },
  "stories": [
    {
      "title": "Set up project structure",
      "description": "Initialize project with required dependencies and configuration",
      "estimate": "4 hours",
      "acceptance_criteria": [
        "Project structure created",
        "Dependencies installed",
        "Configuration files setup"
      ],
      "labels": ["setup", "backend"]
    },
    {
      "title": "Implement core functionality",
      "description": "Develop main feature logic and business rules",
      "estimate": "8 hours",
      "acceptance_criteria": [
        "Core logic implemented",
        "Unit tests written",
        "Code review completed"
      ],
      "labels": ["feature", "backend"]
    },
    {
      "title": "Add integration tests",
      "description": "Create comprehensive integration test suite",
      "estimate": "6 hours",
      "acceptance_criteria": [
        "Integration tests written",
        "Test coverage > 90%",
        "Tests passing in CI"
      ],
      "labels": ["testing", "qa"]
    }
  ]
}
EOF

    log_success "Kanban issues generated"
}

# Stage 5: Specification Creation
run_stage_5() {
    log_stage 5 "Specification Creation"
    
    cat > "$OUTPUT_DIR/05-api-specification.yaml" << EOF
openapi: 3.0.0
info:
  title: $FEATURE_NAME API
  version: 1.0.0
  description: API specification for $FEATURE_NAME

paths:
  /api/feature:
    get:
      summary: Get feature status
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  data:
                    type: object
    post:
      summary: Create feature resource
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                config:
                  type: object
      responses:
        '201':
          description: Resource created
        '400':
          description: Bad request

components:
  schemas:
    Error:
      type: object
      properties:
        message:
          type: string
        code:
          type: string

# Generated: $(date)
EOF

    log_success "API specification created"
}

# Stage 6: Implementation
run_stage_6() {
    log_stage 6 "Implementation"
    
    mkdir -p "$OUTPUT_DIR/implementation"
    
    cat > "$OUTPUT_DIR/implementation/README.md" << EOF
# Implementation: $FEATURE_NAME

## Development Setup
\`\`\`bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Run development server
npm run dev
\`\`\`

## Implementation Guide

### Step 1: Core Logic
Implement the main feature functionality following the specifications.

### Step 2: API Endpoints
Create REST API endpoints as defined in the OpenAPI specification.

### Step 3: Database Layer
Set up database models and data access layer.

### Step 4: Business Logic
Implement business rules and validation logic.

### Step 5: Error Handling
Add comprehensive error handling and logging.

## Code Quality Standards
- Follow ESLint configuration
- Maintain test coverage > 90%
- Use TypeScript for type safety
- Document all public APIs

Generated: $(date)
EOF

    log_success "Implementation guide created"
}

# Stage 7: Testing
run_stage_7() {
    log_stage 7 "Testing"
    
    mkdir -p "$OUTPUT_DIR/testing"
    
    cat > "$OUTPUT_DIR/testing/test-plan.md" << EOF
# Test Plan: $FEATURE_NAME

## Test Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Achieve >95% code coverage

### Integration Tests
- Test API endpoints end-to-end
- Test database interactions
- Test external service integrations

### Performance Tests
- Load testing with expected traffic
- Stress testing for peak loads
- Memory and CPU profiling

### Security Tests
- Authentication/authorization testing
- Input validation testing
- SQL injection prevention
- XSS prevention

## Test Execution
\`\`\`bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run performance tests
npm run test:performance

# Run security tests
npm run test:security
\`\`\`

Generated: $(date)
EOF

    log_success "Test plan created"
}

# Stage 8: Deployment
run_stage_8() {
    log_stage 8 "Deployment"
    
    mkdir -p "$OUTPUT_DIR/deployment"
    
    cat > "$OUTPUT_DIR/deployment/deploy.sh" << 'EOF'
#!/bin/bash
# Deployment script for feature

set -e

echo "🚀 Starting deployment..."

# Build application
echo "📦 Building application..."
npm run build

# Run tests
echo "🧪 Running tests..."
npm test

# Security scan
echo "🔒 Running security scan..."
npm audit

# Deploy to staging
echo "🎭 Deploying to staging..."
npm run deploy:staging

# Run smoke tests
echo "💨 Running smoke tests..."
npm run test:smoke

# Deploy to production
echo "🌟 Deploying to production..."
npm run deploy:production

echo "✅ Deployment completed successfully!"
EOF

    chmod +x "$OUTPUT_DIR/deployment/deploy.sh"
    
    log_success "Deployment scripts created"
}

# Stage 9: Monitoring
run_stage_9() {
    log_stage 9 "Monitoring"
    
    mkdir -p "$OUTPUT_DIR/monitoring"
    
    cat > "$OUTPUT_DIR/monitoring/alerts.yaml" << EOF
# Monitoring and Alerting Configuration

alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    duration: 5m
    severity: critical
    channels: [slack, email]

  - name: slow_response_time
    condition: avg_response_time > 500ms
    duration: 10m
    severity: warning
    channels: [slack]

  - name: high_cpu_usage
    condition: cpu_usage > 80%
    duration: 15m
    severity: warning
    channels: [slack]

dashboards:
  - name: "$FEATURE_NAME Overview"
    panels:
      - requests_per_minute
      - error_rate
      - response_time_p95
      - active_users

# Generated: $(date)
EOF

    log_success "Monitoring configuration created"
}

# Main execution
main() {
    echo "🚀 AI Development Lifecycle Starting..."
    
    if [[ -z "$FEATURE_NAME" && -z "$TARGET_STAGE" ]]; then
        echo "Error: Must specify either --feature or --stage"
        usage
        exit 1
    fi
    
    if [[ -n "$TARGET_STAGE" ]]; then
        # Run specific stage
        case $TARGET_STAGE in
            1) run_stage_1 ;;
            2) run_stage_2 ;;
            3) run_stage_3 ;;
            4) run_stage_4 ;;
            5) run_stage_5 ;;
            6) run_stage_6 ;;
            7) run_stage_7 ;;
            8) run_stage_8 ;;
            9) run_stage_9 ;;
            *) 
                log_error "Invalid stage: $TARGET_STAGE (must be 1-9)"
                exit 1
                ;;
        esac
    else
        # Run all stages
        run_stage_1
        run_stage_2
        run_stage_3
        run_stage_4
        run_stage_5
        run_stage_6
        run_stage_7
        run_stage_8
        run_stage_9
    fi
    
    log_success "AI Development Lifecycle completed!"
    echo "📁 Outputs saved to: $OUTPUT_DIR"
}

main "$@"