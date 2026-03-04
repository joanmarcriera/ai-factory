---
description: Checklist to complete before creating task 001 for any new project
---

# Project Bootstrap Checklist

Complete these steps before writing any task YAML files. Skipping this is how 37.5% of tasks become wasted fix iterations.

## 1. Create `coding-conventions.md`
Define language-specific rules for the project:
- Code style (indentation, naming)
- Anti-patterns to avoid (placeholders, truncation comments)
- Framework-specific rules (e.g., idempotent DOM ops for browser scripts)
- Scraping strategy if applicable (structural selectors vs brittle attributes)

## 2. Define Guardrails
Review `.agents/workflows/pre-task-guardrails.md` and confirm the default checks apply. Add project-specific checks if needed (e.g., `! grep "aria-label" <file>` for Google Maps scraping).

## 3. Define Validation Strategy
Choose per-task validation approach:
- **grep checks**: Fast, good for verifying specific strings/patterns exist
- **Unit tests**: Better for logic verification, requires test infrastructure
- **Both**: Recommended for medium+ risk tasks

## 4. Create Task 001: Scaffolding
First task should set up project structure (directories, empty files, config). This ensures all subsequent tasks have valid `context_files` paths.

## 5. Dry-Run Verification
Run the orchestrator with `--dry-run` (or `-vv` on a trivial task) to verify:
- Conventions are injected into the Aider prompt
- Guardrails are detected and will run
- API key is configured and model is accessible
