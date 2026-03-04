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
