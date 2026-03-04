---
description: Guideline for consistent task YAML creation
---

// turbo-all

AI Agents and human contributors MUST follow these rules when creating or modifying files in `tasks/*.yaml`:

### 1. Quoting Style
- Use **DOUBLE QUOTES** (`"`) for all string values (IDs, titles, paths).
- Example: `id: "001"`, `title: "my-task"`

### 2. Status Field
- Always include `status: "pending"` by default for new tasks.
- Keep the status at the **bottom** of the file if possible.

### 3. Delimiters
- Use standard YAML list format with a dash and a space (`- `).

### 4. Naming Convention
- Filenames should follow the pattern: `XXX-description.yaml` where XXX is a 3-digit padded integer.
- Example: `001-hello.yaml`, `002-scaffold.yaml`

### 6. UV Consistency (CRITICAL)
- Use `uv run` for all validation commands that involve python scripts or project tools.
- This ensures the validation runs in the same environment as the orchestrator.
- Example: `uv run python src/my_script.py`

### 7. Robust Validation
- Do NOT just use `test -f`. Use `grep` or other tools to ensure the file is NOT EMPTY and contains expected markers.
- Example: `grep "def my_function" src/file.py`

### 8. Deterministic Prompting (CRITICAL)
- The `done_when` array is injected directly into the Aider prompt.
- If your `validate` array checks for a specific string (e.g. `grep "extractData"`), your `done_when` array **MUST EXPLICITLY INSTRUCT** Aider to write that exact string (e.g., "Create a function exactly named 'extractData'").
- Do not assume Aider will use the same variable/function names you are thinking of unless you enforce it in `done_when`.

### 9. Task Immutability (CRITICAL)
- **NEVER** alter the `id`, `depends_on`, or contents of a task that has `status: "done"`.
- If a task has completed successfully (`done`), it is a proven historical record of what worked. Altering it (e.g. adding extra numbers or changing its prompt) destroys our understanding of which prompts actually succeeded.
- If you need to re-run, modify, or iterate on a completed task, you must explicitly change its `status` back to `"pending"` before making any other changes to the file.

### 10. Human Validation
- If the project results in a user-facing tool (like a browser extension, UI, or interactive script), the sequence of tasks **MUST** include a final task dedicated to generating human-readable instructions.
- This ensures the user knows exactly how to test the final product manually.

### 11. Outcome-Based Validation
- Do not just validate internal logic (like checking if a function exists). You MUST validate the core requirement that makes the file usable in its target environment.
- Example: If creating a Tampermonkey script, you must validate that the `==UserScript==` metadata block is present at the top of the file.

### Example
```yaml
id: "999"
title: "example-task"
type: "test"
risk: "low"
depends_on: []
context_files:
  - "src/example.py"
done_when:
  - "File src/example.py exists"
  - "File prints 'Success'"
validate:
  - "test -f \"src/example.py\""
  - "grep \"print\" src/example.py"
  - "uv run python src/example.py | grep -q \"Success\""
status: "pending"
```
