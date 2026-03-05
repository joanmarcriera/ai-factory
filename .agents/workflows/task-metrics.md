---
description: Standard metrics schema written to every completed task YAML
---

# Task Metrics Schema

Every task with `status: "done"` MUST have a `metrics` block with ALL of the following fields. The orchestrator writes this automatically — agents must never manually set partial metrics.

## Required Fields

```yaml
metrics:
  model: "groq/llama-3.1-8b-instant"       # Model that produced the accepted result
  provider: "groq"                           # Provider name (groq, gemini, openrouter, anthropic, openai, cerebras)
  attempts: 2                                # Total attempts (including retries)
  fallbacks_used: 1                          # Number of model switches due to rate limits or API errors
  fallback_chain:                            # Ordered list of models attempted (even if only one)
    - "groq/llama-3.1-8b-instant"
    - "gemini/gemini-2.0-flash-lite"
  tokens_sent: 4600                          # Prompt tokens (0 if not reported)
  tokens_received: 340                       # Completion tokens (0 if not reported)
  cost: 0.00026                              # USD cost (0.0 for free-tier models)
  duration_seconds: 45                       # Wall-clock time from first attempt to completion
  completed_at: "2026-03-05 00:22:08"        # ISO-ish timestamp
```

## Rules

1. **All fields are mandatory** — use `0` or `0.0` for unknown numeric values, empty list `[]` for empty arrays.
2. **`model`** is the model that passed validation, not the first model tried.
3. **`provider`** is extracted from the model string (everything before the first `/`).
4. **`fallback_chain`** lists every model attempted in order, including the successful one. If only the primary model was used, it's a single-element list.
5. **`fallbacks_used`** = `len(fallback_chain) - 1` (0 if no fallbacks were needed).
6. **`duration_seconds`** is measured by the orchestrator, not by aider.
7. **Manually completed tasks** (e.g., written directly without the orchestrator) should use `model: "manual"`, `provider: "human"`, and zeroed token/cost fields.

## Purpose

Consistent metrics enable:
- Cost tracking per project and per model
- Model reliability comparison (success rate, fallback frequency)
- Task complexity estimation (tokens correlate with difficulty)
- Performance trends over time (duration, retry rates)
