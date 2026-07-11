import express, { Express, NextFunction, Request, Response } from "express";
import { rateLimit } from "express-rate-limit";
import { timingSafeEqual } from "node:crypto";
import { isIP } from "node:net";
import { performance } from "node:perf_hooks";
import { runOrgTask } from "./claudeClient";

const MAX_REQUESTS_PER_MINUTE = 10;
const REQUEST_WINDOW_MS = 60_000;
const MAX_REPO_SUMMARY_CHARS = 4_000;
const MAX_USER_PROMPT_CHARS = 12_000;

type TaskType = "plan" | "refactor" | "spec";
type TaskInput = {
  repoSummary: string;
  taskType: TaskType;
  userPrompt: string;
};
type TaskResult = {
  usage: { input_tokens: number; output_tokens: number };
};
export type TaskRunner = (input: TaskInput) => Promise<TaskResult>;

function isTaskType(value: unknown): value is TaskType {
  return value === "plan" || value === "refactor" || value === "spec";
}

function expectedGatewayToken(): Buffer {
  const gatewayToken = process.env.AI_GATEWAY_TOKEN;
  if (!gatewayToken || Buffer.byteLength(gatewayToken, "utf8") < 32) {
    throw new Error("AI_GATEWAY_TOKEN must contain at least 32 bytes");
  }
  return Buffer.from(gatewayToken, "utf8");
}

function isAuthorized(
  authorization: string | undefined,
  expectedToken: Buffer,
): boolean {
  if (!authorization?.startsWith("Bearer ")) {
    return false;
  }
  const supplied = Buffer.from(authorization.slice("Bearer ".length), "utf8");
  return supplied.length === expectedToken.length &&
    timingSafeEqual(supplied, expectedToken);
}

function requireGatewayAuth(expectedToken: Buffer) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!isAuthorized(req.headers.authorization, expectedToken)) {
      res.status(401).json({ error: "Unauthorized" });
      return;
    }
    next();
  };
}

export function createRequestBudget(
  maxRequests = MAX_REQUESTS_PER_MINUTE,
  windowMs = REQUEST_WINDOW_MS,
  startedAt = performance.now(),
): (now?: number) => boolean {
  let requestWindowStarted = startedAt;
  let requestsInWindow = 0;
  return (now = performance.now()): boolean => {
    if (now < requestWindowStarted) {
      return false;
    }
    if (now - requestWindowStarted >= windowMs) {
      requestWindowStarted = now;
      requestsInWindow = 0;
    }
    if (requestsInWindow >= maxRequests) {
      return false;
    }
    requestsInWindow += 1;
    return true;
  };
}

export function createGatewayApp(taskRunner: TaskRunner = runOrgTask): Express {
  const app = express();
  const consumeRequestBudget = createRequestBudget();
  const taskRateLimit = rateLimit({
    windowMs: REQUEST_WINDOW_MS,
    limit: MAX_REQUESTS_PER_MINUTE,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Request rate limit exhausted" },
  });

  app.use(express.json({ limit: "32kb" }));

  // Log a fixed event name instead of attacker-controlled request data.
  app.use((_req, _res, next) => {
    console.log("Request received");
    next();
  });

  app.post(
    "/ai/run-task",
    taskRateLimit,
    requireGatewayAuth(expectedGatewayToken()),
    async (req, res) => {
      try {
        const { repoSummary, taskType, userPrompt } = req.body;

        if (
          typeof repoSummary !== "string" || !repoSummary.trim() ||
          repoSummary.length > MAX_REPO_SUMMARY_CHARS ||
          !isTaskType(taskType) ||
          typeof userPrompt !== "string" || !userPrompt.trim() ||
          userPrompt.length > MAX_USER_PROMPT_CHARS
        ) {
          return res.status(400).json({ error: "Missing required fields" });
        }

        if (!consumeRequestBudget()) {
          res.setHeader("Retry-After", "60");
          return res.status(429).json({ error: "Request budget exhausted" });
        }

        // Never write user-controlled task or repository content to logs.
        console.log("Validated AI task request");
        const result = await taskRunner({ repoSummary, taskType, userPrompt });
        console.log(
          `Tokens used: ${result.usage.input_tokens} in, ` +
          `${result.usage.output_tokens} out`
        );
        return res.json(result);
      } catch (_error) {
        console.error("AI task failed");
        return res.status(500).json({ error: "Internal server error" });
      }
    },
  );

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });
  return app;
}

export function startGateway() {
  const app = createGatewayApp();
  const rawPort = process.env.PORT || "3000";
  if (!/^[1-9][0-9]{0,4}$/.test(rawPort)) {
    throw new Error("PORT must be an integer from 1 through 65535");
  }
  const port = Number(rawPort);
  if (port > 65_535) {
    throw new Error("PORT must be an integer from 1 through 65535");
  }
  const host = (process.env.AI_GATEWAY_HOST || "127.0.0.1").trim();
  const validDnsHost = host.length <= 253 && host.split(".").every(
    label => /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/.test(label)
  );
  if (!isIP(host) && !validDnsHost) {
    throw new Error("AI_GATEWAY_HOST must be an IP address or DNS hostname");
  }
  const loopbackHosts = new Set(["127.0.0.1", "::1", "localhost"]);
  if (!loopbackHosts.has(host) &&
      process.env.ALLOW_REMOTE_AI_GATEWAY !== "true") {
    throw new Error(
      "Remote binding requires ALLOW_REMOTE_AI_GATEWAY=true and production controls"
    );
  }

  return app.listen(port, host, () => {
    console.log(`AI Gateway running on http://${host}:${port}`);
  });
}

if (require.main === module) {
  startGateway();
}
