import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function runOrgTask(input: {
  repoSummary: string;
  taskType: "plan" | "refactor" | "spec";
  userPrompt: string;
}) {
  const systemPrompt = `
You are the org AI pair programmer.
Follow ORG RULES v1.3:
- Use spec-first development.
- Respect security rules at https://internal/ai-rules/security.
- Never modify tests in /tests/trusted without explicit instruction.
- Always include error handling and logging.
- Follow the org coding standards for this language.
`;

  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    system: systemPrompt,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: `Repo summary:\n${input.repoSummary}` },
          { type: "text", text: `Task type: ${input.taskType}` },
          { type: "text", text: `Request:\n${input.userPrompt}` }
        ]
      }
    ]
  });

  return response;
}
