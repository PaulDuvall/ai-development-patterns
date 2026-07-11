import assert from "node:assert/strict";
import { request as sendHttpRequest } from "node:http";
import { once } from "node:events";
import { test } from "node:test";

const TOKEN = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
process.env.AI_GATEWAY_TOKEN = TOKEN;
process.env.ANTHROPIC_API_KEY = "unused-local-test-key";

// Load after setting the required environment. The guarded module does not listen on import.
const { createGatewayApp, createRequestBudget } = require("./server") as
  typeof import("./server");

function post(
  port: number,
  clientAddress: string,
  authorization: string | undefined,
  body: unknown,
): Promise<number> {
  const payload = JSON.stringify(body);
  const headers: Record<string, string | number> = {
    "Content-Length": Buffer.byteLength(payload),
    "Content-Type": "application/json",
    "X-Forwarded-For": clientAddress,
  };
  if (authorization) {
    headers.Authorization = authorization;
  }
  return new Promise((resolve, reject) => {
    const request = sendHttpRequest({
      host: "127.0.0.1",
      port,
      path: "/ai/run-task",
      method: "POST",
      headers,
    }, response => {
      response.resume();
      response.on("end", () => resolve(response.statusCode || 0));
    });
    request.on("error", reject);
    request.end(payload);
  });
}

test("global request budget caps calls and resets its window", () => {
  const consume = createRequestBudget(2, 1_000, 5_000);
  assert.equal(consume(5_000), true);
  assert.equal(consume(5_500), true);
  assert.equal(consume(5_999), false);
  assert.equal(consume(6_000), true);
  assert.equal(consume(4_000), false, "clock rollback must fail closed");
});

test("gateway enforces auth, per-IP throttling, and the global provider cap", async t => {
  let providerCalls = 0;
  const app = createGatewayApp(async () => {
    providerCalls += 1;
    return { usage: { input_tokens: 1, output_tokens: 1 } };
  });
  // Test-only proxy trust lets one loopback process model distinct source IPs.
  app.set("trust proxy", (address: string) =>
    address === "127.0.0.1" || address === "::ffff:127.0.0.1");
  const server = app.listen(0, "127.0.0.1");
  await once(server, "listening");
  t.after(() => new Promise<void>((resolve, reject) => {
    server.close(error => error ? reject(error) : resolve());
  }));
  const address = server.address();
  assert(address && typeof address !== "string");
  const port = address.port;

  for (let index = 0; index < 11; index += 1) {
    assert.equal(await post(port, "192.0.2.1", undefined, {}), 401);
  }
  assert.equal(providerCalls, 0);

  for (let index = 0; index < 10; index += 1) {
    assert.equal(await post(port, "192.0.2.1", `Bearer ${TOKEN}`, {}), 400);
  }
  assert.equal(await post(port, "192.0.2.1", `Bearer ${TOKEN}`, {}), 429);
  assert.equal(providerCalls, 0, "invalid input must not spend provider budget");

  const validTask = {
    repoSummary: "Local behavior test",
    taskType: "plan",
    userPrompt: "Do not call a provider",
  };
  for (let host = 2; host <= 11; host += 1) {
    assert.equal(
      await post(port, `192.0.2.${host}`, `Bearer ${TOKEN}`, validTask),
      200,
    );
  }
  assert.equal(
    await post(port, "192.0.2.12", `Bearer ${TOKEN}`, validTask),
    429,
  );
  assert.equal(providerCalls, 10, "global cap must span distinct source IPs");
});
