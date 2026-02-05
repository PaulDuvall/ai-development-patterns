import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

function orgSystemPrompt(context: { appName: string }) {
  return `
You are the AI assistant for ${context.appName}.
Follow ORG RULES v1.3 from https://internal/ai-rules.
Always:
- Write tests first.
- Call out security risks.
- Use our logging and error-handling patterns.
- Follow the org coding standards.
- Never expose secrets or PII in outputs.
`;
}

export async function planFeature(params: {
  appName: string;
  userPrompt: string;
}) {
  return client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    system: orgSystemPrompt({ appName: params.appName }),
    messages: [
      {
        role: "user",
        content: `Plan the following feature:\n${params.userPrompt}`
      }
    ]
  });
}

export async function refactorCode(params: {
  appName: string;
  userPrompt: string;
}) {
  return client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    system: orgSystemPrompt({ appName: params.appName }),
    messages: [
      {
        role: "user",
        content: `Refactor the following:\n${params.userPrompt}`
      }
    ]
  });
}

export async function writeSpec(params: {
  appName: string;
  userPrompt: string;
}) {
  return client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    system: orgSystemPrompt({ appName: params.appName }),
    messages: [
      {
        role: "user",
        content: `Write a specification for:\n${params.userPrompt}`
      }
    ]
  });
}

// Generic task function
export async function orgClaudeTask(params: {
  appName: string;
  userPrompt: string;
}) {
  return client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1500,
    system: orgSystemPrompt({ appName: params.appName }),
    messages: [{ role: "user", content: params.userPrompt }]
  });
}
