---
description: How to run project tasks using uv
---

// turbo-all

1. Ensure you are in the project root: `cd /Users/mriera/repos/ai-factory`
2. Export your Anthropic API Key: `export ANTHROPIC_API_KEY="your-key"`
3. Run the orchestrator: `uv run python orchestrator.py`
4. To run aider manually for a specific task: `uv run aider --model sonnet --message "your message"`
5. All dependencies are managed via `uv`. To add a new dependency: `uv add <package>`
