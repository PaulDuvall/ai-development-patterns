#!/usr/bin/env node

import { program } from "commander";
import * as fs from "fs";
import * as path from "path";

const GATEWAY_URL = process.env.AI_GATEWAY_URL || "http://localhost:3000";

async function callGateway(taskType: string, userPrompt: string) {
  const repoSummary = detectRepoContext();

  const response = await fetch(`${GATEWAY_URL}/ai/run-task`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      repoSummary,
      taskType,
      userPrompt
    })
  });

  if (!response.ok) {
    throw new Error(`Gateway error: ${response.statusText}`);
  }

  return response.json();
}

function detectRepoContext(): string {
  const cwd = process.cwd();
  const parts: string[] = [];

  // Detect package.json
  const pkgPath = path.join(cwd, "package.json");
  if (fs.existsSync(pkgPath)) {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));
    parts.push(`Node.js project: ${pkg.name || "unknown"}`);
  }

  // Detect language
  if (fs.existsSync(path.join(cwd, "tsconfig.json"))) {
    parts.push("TypeScript");
  } else if (fs.existsSync(path.join(cwd, "requirements.txt"))) {
    parts.push("Python");
  } else if (fs.existsSync(path.join(cwd, "go.mod"))) {
    parts.push("Go");
  }

  // Detect test framework
  if (fs.existsSync(path.join(cwd, "jest.config.js"))) {
    parts.push("Jest tests");
  } else if (fs.existsSync(path.join(cwd, "pytest.ini"))) {
    parts.push("Pytest");
  }

  return parts.length > 0 ? parts.join(", ") : "Unknown project type";
}

function extractText(response: any): string {
  if (response.content && Array.isArray(response.content)) {
    return response.content
      .filter((block: any) => block.type === "text")
      .map((block: any) => block.text)
      .join("\n");
  }
  return JSON.stringify(response, null, 2);
}

program
  .name("ai-dev")
  .description("Developer CLI for org AI tasks")
  .version("1.0.0");

program
  .command("plan <feature>")
  .description("Plan a new feature")
  .action(async (feature: string) => {
    try {
      console.log("Planning feature...\n");
      const result = await callGateway("plan", feature);
      console.log(extractText(result));
    } catch (error) {
      console.error("Error:", error);
      process.exit(1);
    }
  });

program
  .command("refactor <description>")
  .description("Refactor code")
  .action(async (description: string) => {
    try {
      console.log("Generating refactor plan...\n");
      const result = await callGateway("refactor", description);
      console.log(extractText(result));
    } catch (error) {
      console.error("Error:", error);
      process.exit(1);
    }
  });

program
  .command("spec <feature>")
  .description("Write a specification")
  .action(async (feature: string) => {
    try {
      console.log("Writing specification...\n");
      const result = await callGateway("spec", feature);
      console.log(extractText(result));
    } catch (error) {
      console.error("Error:", error);
      process.exit(1);
    }
  });

program.parse();
