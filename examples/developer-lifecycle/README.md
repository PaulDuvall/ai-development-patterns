# AI Developer Lifecycle Example

This directory contains a working bash script that implements the 9-stage AI Developer Lifecycle, enhanced implementation techniques including the Five-Try Rule and systematic retry strategies, and a comprehensive workflow example showing how to apply these techniques in practice.

## Current Structure

```
ai-development-lifecycle/
├── README.md                  # This file
├── lifecycle-workflow.sh      # ✅ Complete 9-stage workflow automation script
└── examples/                  # Empty directory for future examples
```

## Complete Implementation Structure

A full implementation would include:

```
ai-development-lifecycle/
├── README.md                          # This file
├── lifecycle-workflow.sh              # ✅ Complete 9-stage workflow automation script
├── comprehensive-workflow-example.md  # ✅ Complete 7-step implementation example
├── enhanced-implementation-techniques.md # ✅ Five-Try Rule, systematic retry, integration strategies
├── stage-prompts/                     # Detailed prompts for each stage
│   ├── 01-problem-definition.md
│   ├── 02-technical-planning.md
│   ├── 03-requirements-analysis.md
│   ├── 04-issue-generation.md
│   ├── 05-specification-creation.md
│   ├── 06-implementation.md
│   ├── 07-testing.md
│   ├── 08-deployment.md
│   └── 09-monitoring.md
├── examples/                          # Example implementations
│   ├── jwt-authentication/            # Complete JWT auth example
│   └── api-endpoints/                 # REST API example
└── ci-integration/                    # CI/CD pipeline integration
    ├── github-actions.yml
    ├── gitlab-ci.yml
    └── azure-pipelines.yml
```

## The 9-Stage Lifecycle

1. **Problem Definition** → Clear problem statement and success criteria
2. **Technical Planning** → Architecture decisions and technical approach  
3. **Requirements Analysis** → Detailed functional and non-functional requirements
4. **Issue Generation** → Kanban-ready work items with acceptance criteria
5. **Specification Creation** → Executable specifications and API contracts
6. **Implementation** → AI-assisted coding following specifications
7. **Testing** → Comprehensive test suite execution and validation
8. **Deployment** → Automated deployment with rollback capabilities
9. **Monitoring** → Production monitoring and alerting setup

## Prerequisites

- Bash shell (macOS, Linux, or WSL on Windows)
- Basic command line knowledge
- AI assistant access (Claude, ChatGPT, etc.) for implementing generated templates

## Quick Start

1. **Make the script executable:**
   ```bash
   chmod +x lifecycle-workflow.sh
   ```

2. **Run complete lifecycle for a feature:**
   ```bash
   ./lifecycle-workflow.sh --feature "JWT Authentication"
   ```

3. **Run specific stage:**
   ```bash
   ./lifecycle-workflow.sh --stage 6 --context "implement-jwt-auth"
   ```

4. **View help:**
   ```bash
   ./lifecycle-workflow.sh --help
   ```

## What the Script Generates

The `lifecycle-workflow.sh` script creates a `lifecycle-output/` directory with:

- **Stage 1**: `01-problem-statement.md` - Problem definition template
- **Stage 2**: `02-technical-plan.md` - Architecture and technology decisions
- **Stage 3**: `03-requirements.md` - Functional and non-functional requirements
- **Stage 4**: `04-kanban-issues.json` - Ready-to-import GitHub/JIRA issues
- **Stage 5**: `05-api-specification.yaml` - OpenAPI specification template
- **Stage 6**: `implementation/README.md` - Implementation guide and setup instructions
- **Stage 7**: `testing/test-plan.md` - Comprehensive testing strategy
- **Stage 8**: `deployment/deploy.sh` - Deployment automation script
- **Stage 9**: `monitoring/alerts.yaml` - Monitoring and alerting configuration

## Usage Examples

### Complete Feature Implementation
```bash
# Generate all lifecycle stages for JWT authentication
./lifecycle-workflow.sh --feature "User Authentication System"

# Output: lifecycle-output/ directory with all 9 stages
```

### Single Stage Execution
```bash
# Generate only the technical planning stage
./lifecycle-workflow.sh --stage 2 --context "microservices architecture"

# Generate implementation guide with specific context
./lifecycle-workflow.sh --stage 6 --context "OAuth2 integration with existing API"
```

### Typical Workflow
```bash
# 1. Define the problem and generate all stages
./lifecycle-workflow.sh --feature "Payment Processing"

# 2. Review generated templates in lifecycle-output/
ls -la lifecycle-output/

# 3. Use AI assistant to flesh out the templates
# 4. Import Kanban issues to your project management tool
# 5. Follow the implementation guide
```

## Next Steps After Running the Script

1. **Review Generated Templates**: Examine all files in `lifecycle-output/` directory
2. **Enhance with AI**: Use the templates as starting points for AI conversations
3. **Import Issues**: Load `04-kanban-issues.json` into GitHub Issues or JIRA
4. **Implement API**: Use `05-api-specification.yaml` to generate API stubs
5. **Follow Implementation Guide**: Use `implementation/README.md` for development setup
6. **Execute Tests**: Implement tests following `testing/test-plan.md`
7. **Deploy**: Use `deployment/deploy.sh` as deployment automation baseline
8. **Monitor**: Configure alerts using `monitoring/alerts.yaml`

## Script Features

- **Complete automation** of all 9 lifecycle stages
- **Template generation** for immediate use with AI assistants  
- **Structured output** organized by stage and file type
- **Command-line interface** with help and validation
- **Colored output** for clear stage progression
- **Error handling** and validation

## Integration Opportunities

The generated templates work well with:

### Project Management
- **GitHub Issues**: Import `04-kanban-issues.json` using GitHub CLI or API
- **JIRA**: Convert JSON issues to JIRA format for import
- **Azure DevOps**: Transform issues into work items

### Development Tools
- **OpenAPI**: Use `05-api-specification.yaml` with Swagger/Postman
- **Testing**: Implement test plans using generated `testing/test-plan.md`
- **CI/CD**: Adapt `deployment/deploy.sh` for your pipeline

### AI Assistants
- Use generated templates as context for Claude, ChatGPT, or Copilot
- Feed stage outputs into AI for detailed implementation
- Leverage structured prompts for consistent results

## Contributing

To extend this example:
1. Add more detailed stage prompts in a `stage-prompts/` directory
2. Create complete example implementations in `examples/`
3. Add CI/CD integration templates in `ci-integration/`
4. Enhance the bash script with additional features

The current script provides a solid foundation for the complete AI Developer Lifecycle pattern.