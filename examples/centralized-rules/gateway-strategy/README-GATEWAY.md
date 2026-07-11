# Centralized Rules Example

This example demonstrates the three-layer architecture for centralizing AI rules across an organization using the Claude SDK.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ai-dev-cli │ ──► │  ai-gateway │ ──► │  Claude API │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │            ┌──────┴──────┐
       │            │  Org Rules  │
       │            │  Logging    │
       │            │  Filters    │
       │            └─────────────┘
       │
       └──────────► @yourorg/org-ai-client (alternative)
```

## Components

### 1. ai-gateway/

Internal service that owns all org rules and calls the Claude API.

**Features**:
- Centralized system prompts with org rules
- Bounded, non-content event and token-usage logging
- Bearer-token authentication and a conservative in-process request cap
- Loopback-only binding unless remote exposure is explicitly acknowledged
- Input/output filtering hooks

### 2. org-ai-client/

Shared SDK wrapper that embeds org rules. Use this if you don't want a network service yet.

**Features**:
- Org rules baked into system prompts
- Consistent interface across all repos
- Version-controlled rule updates

### 3. ai-dev-cli/

Developer CLI that calls the gateway or wrapper library.

**Features**:
- Simple commands: `ai-dev plan`, `ai-dev refactor`
- Auto-detects repo context
- Consistent UX across tools

## Setup

### Prerequisites

- Node.js 18+
- `ANTHROPIC_API_KEY` environment variable
- `AI_GATEWAY_TOKEN` containing at least 32 random bytes

### Install dependencies

```bash
cd ai-gateway && npm ci && npm run build
cd ../org-ai-client && npm ci && npm run build
cd ../ai-dev-cli && npm ci && npm run build
```

### Run the gateway

```bash
cd ai-gateway
export AI_GATEWAY_TOKEN="$(openssl rand -hex 32)"
npm start
# Gateway running on http://127.0.0.1:3000
```

### Use the CLI

```bash
cd ai-dev-cli
export AI_GATEWAY_TOKEN="<the same token used by ai-gateway>"
npm link
ai-dev plan "Implement idempotent refund API"
```

The example binds to `127.0.0.1` and permits at most ten provider-backed requests per minute in one
process. Treat those as development safeguards, not production controls. Remote binding additionally
requires `ALLOW_REMOTE_AI_GATEWAY=true`; before enabling it, put the service behind organizational
identity, distributed rate limiting, per-user request and token budgets, audit controls, and network
policy. Never expose the example directly to an untrusted network.

## Customization

### Modify org rules

Edit the system prompt in `ai-gateway/src/claudeClient.ts` or `org-ai-client/src/index.ts`:

```typescript
const systemPrompt = `
You are the org AI pair programmer.
Follow ORG RULES v1.4:
- Use spec-first development.
- Your custom rules here...
`;
```

### Add input/output filters

Extend the gateway with validation:

```typescript
// Before calling Claude
if (containsSecrets(input)) {
  throw new Error("Input contains secrets");
}

// After receiving response
if (containsBannedPatterns(response)) {
  throw new Error("Response violates policy");
}
```

### Integrate policy-as-code

Add OPA or Cedar policy checks:

```typescript
const allowed = await opa.evaluate("ai/task_allowed", {
  repo: input.repo,
  taskType: input.taskType,
  user: req.user
});
```
