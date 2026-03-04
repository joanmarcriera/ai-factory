---
description: Automatic guardrail checks run by the orchestrator after every task execution
---

# Pre-Commit Guardrails

These checks run automatically on all `context_files` after Aider finishes and BEFORE task-specific `validate:` commands. A task can opt out with `guardrails: skip` in its YAML (use only for non-code tasks like documentation).

## Checks

### 1. No Truncation Comments
```bash
! grep -E "// (Rest of|\.\.\..*code|existing code|other code|remaining code)" <file>
```
**Why**: Aider frequently replaces function bodies with placeholder comments instead of writing complete code. This was the #1 failure mode (tasks 016, 027).

### 2. No Duplicate Function Definitions
```bash
grep -oE "function [a-zA-Z_][a-zA-Z0-9_]*" <file> | sort | uniq -d | wc -l | grep -q "^0$"
```
**Why**: Aider sometimes creates a second copy of a function rather than editing the existing one (task 028).

### 3. File Not Empty
```bash
test -s <file>
```
**Why**: Aider occasionally empties files on failure but exits 0.

### 4. File Not Truncated (Line Count Check)
Compare line count before and after Aider execution. Fail if file shrunk by more than 20%.
```python
if post_lines < pre_lines * 0.8:
    fail("Suspected truncation: file went from {pre} to {post} lines")
```
**Why**: Even without placeholder comments, Aider may silently drop functions. A significant line count decrease is a strong signal.

### 5. No Unimplemented Placeholders
```bash
! grep -E "// (TODO: implement|add .* here|FIXME|placeholder)" <file>
```
**Why**: Ensures Aider actually wrote the implementation, not just stubs.

## How the Orchestrator Uses These

1. Before calling Aider: snapshot line counts of all `context_files`
2. After Aider exits: run guardrails 1-5 on each context file
3. If any guardrail fails: mark task as failed, include the guardrail error in retry prompt
4. If all guardrails pass: proceed to task-specific `validate:` commands
