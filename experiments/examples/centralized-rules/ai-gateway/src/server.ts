import express from "express";
import { runOrgTask } from "./claudeClient";

const app = express();
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

app.post("/ai/run-task", async (req, res) => {
  try {
    const { repoSummary, taskType, userPrompt } = req.body;

    // Input validation
    if (!repoSummary || !taskType || !userPrompt) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Log usage for metrics
    console.log(`Task: ${taskType}, Repo: ${repoSummary.substring(0, 50)}...`);

    const result = await runOrgTask({ repoSummary, taskType, userPrompt });

    // Log token usage
    console.log(`Tokens used: ${result.usage.input_tokens} in, ${result.usage.output_tokens} out`);

    res.json(result);
  } catch (error) {
    console.error("Error running task:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`AI Gateway running on http://localhost:${PORT}`);
});
