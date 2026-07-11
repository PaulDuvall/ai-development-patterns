import express from "express";
import { timingSafeEqual } from "node:crypto";
import { isIP } from "node:net";
import { runOrgTask } from "./claudeClient";

const app = express();
app.use(express.json({ limit: "32kb" }));

const gatewayToken = process.env.AI_GATEWAY_TOKEN;
if (!gatewayToken || Buffer.byteLength(gatewayToken, "utf8") < 32) {
  throw new Error("AI_GATEWAY_TOKEN must contain at least 32 bytes");
}
const expectedToken = Buffer.from(gatewayToken, "utf8");
const MAX_REQUESTS_PER_MINUTE = 10;
const MAX_REPO_SUMMARY_CHARS = 4_000;
const MAX_USER_PROMPT_CHARS = 12_000;
let requestWindowStarted = Date.now();
let requestsInWindow = 0;

type TaskType = "plan" | "refactor" | "spec";

function isTaskType(value: unknown): value is TaskType {
  return value === "plan" || value === "refactor" || value === "spec";
}

function isAuthorized(authorization: string | undefined): boolean {
  if (!authorization?.startsWith("Bearer ")) {
    return false;
  }
  const supplied = Buffer.from(authorization.slice("Bearer ".length), "utf8");
  return supplied.length === expectedToken.length &&
    timingSafeEqual(supplied, expectedToken);
}

function consumeRequestBudget(now = Date.now()): boolean {
  if (now - requestWindowStarted >= 60_000) {
    requestWindowStarted = now;
    requestsInWindow = 0;
  }
  if (requestsInWindow >= MAX_REQUESTS_PER_MINUTE) {
    return false;
  }
  requestsInWindow += 1;
  return true;
}

// Log a fixed event name instead of attacker-controlled request data.
app.use((_req, _res, next) => {
  console.log("Request received");
  next();
});

app.post("/ai/run-task", async (req, res) => {
  try {
    if (!isAuthorized(req.headers.authorization)) {
      return res.status(401).json({ error: "Unauthorized" });
    }
    if (!consumeRequestBudget()) {
      res.setHeader("Retry-After", "60");
      return res.status(429).json({ error: "Request budget exhausted" });
    }
    const { repoSummary, taskType, userPrompt } = req.body;

    // Input validation
    if (
      typeof repoSummary !== "string" || !repoSummary.trim() ||
      repoSummary.length > MAX_REPO_SUMMARY_CHARS ||
      !isTaskType(taskType) ||
      typeof userPrompt !== "string" || !userPrompt.trim() ||
      userPrompt.length > MAX_USER_PROMPT_CHARS
    ) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Never write user-controlled task or repository content to logs.
    console.log("Validated AI task request");

    const result = await runOrgTask({ repoSummary, taskType, userPrompt });

    // Log token usage
    console.log(`Tokens used: ${result.usage.input_tokens} in, ${result.usage.output_tokens} out`);

    res.json(result);
  } catch (_error) {
    console.error("AI task failed");
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

const rawPort = process.env.PORT || "3000";
if (!/^[1-9][0-9]{0,4}$/.test(rawPort)) {
  throw new Error("PORT must be an integer from 1 through 65535");
}
const PORT = Number(rawPort);
if (PORT > 65_535) {
  throw new Error("PORT must be an integer from 1 through 65535");
}
const HOST = (process.env.AI_GATEWAY_HOST || "127.0.0.1").trim();
const validDnsHost = HOST.length <= 253 && HOST.split(".").every(
  label => /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/.test(label)
);
if (!isIP(HOST) && !validDnsHost) {
  throw new Error("AI_GATEWAY_HOST must be an IP address or DNS hostname");
}
const loopbackHosts = new Set(["127.0.0.1", "::1", "localhost"]);
if (!loopbackHosts.has(HOST) && process.env.ALLOW_REMOTE_AI_GATEWAY !== "true") {
  throw new Error(
    "Remote binding requires ALLOW_REMOTE_AI_GATEWAY=true and production controls"
  );
}

app.listen(PORT, HOST, () => {
  console.log(`AI Gateway running on http://${HOST}:${PORT}`);
});
