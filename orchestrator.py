import yaml
import subprocess
import re
import os
import argparse
from pathlib import Path
from datetime import datetime

def load_env():
    """Simple .env loader to avoid extra dependencies."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value

load_env()

# --- Configuration ---
CONFIG = {
    "model": os.environ.get("AI_MODEL", "anthropic/claude-3-5-sonnet-latest"),
    "max_retries": 2,
    "log_file": ".orchestrator/log.txt",
    "verbose": 0  # 0: normal, 1: verbose, 2: debug
}

TRUNCATION_PATTERNS = [
    r"//\s*(Rest of|\.\.\..*code|existing code|other code|remaining code)",
    r"//\s*(TODO: implement|add .* here|FIXME|placeholder)",
]

def log(message, level=0):
    """Log to file and console if level <= CONFIG['verbose']."""
    log_path = Path(CONFIG["log_file"])
    log_path.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    with open(log_path, "a") as f:
        f.write(f"{formatted_message}\n")

    if level <= CONFIG["verbose"]:
        print(formatted_message)

def snapshot_line_counts(context_files):
    """Record line counts of context files before Aider runs."""
    counts = {}
    for cf in context_files:
        cf_path = Path(cf)
        if cf_path.exists():
            counts[cf] = len(cf_path.read_text().splitlines())
        else:
            counts[cf] = 0
    return counts

def run_guardrails(context_files, pre_line_counts):
    """Run built-in guardrail checks on all context files. Returns (passed, errors)."""
    errors = []

    for cf in context_files:
        cf_path = Path(cf)
        if not cf_path.exists():
            continue

        content = cf_path.read_text()
        lines = content.splitlines()

        # Check: file not empty
        if not content.strip():
            errors.append(f"GUARDRAIL: {cf} is empty after Aider execution")
            continue

        # Check: truncation patterns
        for pattern in TRUNCATION_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append(f"GUARDRAIL: {cf}:{i} contains truncation/placeholder comment: {line.strip()}")

        # Check: duplicate function definitions (JS and Python)
        func_names = re.findall(r"(?:function\s+|def\s+)([a-zA-Z_][a-zA-Z0-9_]*)", content)
        seen = {}
        for name in func_names:
            if name in seen:
                errors.append(f"GUARDRAIL: {cf} has duplicate function '{name}'")
            seen[name] = True

        # Check: file didn't shrink >20%
        pre_count = pre_line_counts.get(cf, 0)
        post_count = len(lines)
        if pre_count > 10 and post_count < pre_count * 0.8:
            errors.append(f"GUARDRAIL: {cf} shrunk from {pre_count} to {post_count} lines (suspected truncation)")

    return (len(errors) == 0, errors)

def build_prompt(task, retry_errors=None):
    """Build the Aider prompt, injecting conventions and optionally prior errors."""
    prompt = f"Task: {task['title']}\n\nComplete when:\n" + \
             "\n".join(f"- {item}" for item in task['done_when']) + \
             "\n\nGenerate necessary code changes."

    # Inject conventions
    conventions_file = Path(".agents/workflows/coding-conventions.md")
    if conventions_file.exists():
        prompt += f"\n\n--- CRITICAL PROJECT CONVENTIONS ---\n{conventions_file.read_text()}\n---\n"

    # Inject guardrails so the model knows what checks will run
    guardrails_file = Path(".agents/workflows/pre-task-guardrails.md")
    if guardrails_file.exists():
        prompt += f"\n\n--- AUTOMATIC GUARDRAIL CHECKS (will run after your changes) ---\n{guardrails_file.read_text()}\n---\n"

    # Error-fed retry: include previous failure context
    if retry_errors:
        prompt += "\n\n--- PREVIOUS ATTEMPT FAILED ---\n"
        prompt += "Your previous attempt failed the following checks. Fix these specific issues while preserving ALL existing code:\n"
        for err in retry_errors:
            prompt += f"- {err}\n"
        prompt += "---\n"

    return prompt

def get_ready_tasks():
    """Return tasks with status=pending and all dependencies done, sorted by ID."""
    all_tasks = {}
    tasks_dir = Path("tasks")
    if not tasks_dir.exists():
        return []

    task_files = sorted(tasks_dir.glob("*.yaml"))
    for task_file in task_files:
        try:
            content = yaml.safe_load(task_file.read_text())
            if content and "id" in content:
                all_tasks[str(content["id"])] = {
                    "file": task_file,
                    "data": content
                }
        except Exception as e:
            log(f"Error loading {task_file}: {e}", level=0)

    ready = []
    for task_id, task_info in all_tasks.items():
        task = task_info["data"]
        if task.get("status") != "pending":
            continue

        deps_met = True
        for dep_id in task.get("depends_on", []):
            dep_id_str = str(dep_id)
            if dep_id_str not in all_tasks:
                deps_met = False
                log(f"Dependency {dep_id_str} for task {task_id} not found in any file.", level=0)
                break

            if all_tasks[dep_id_str]["data"].get("status") != "done":
                deps_met = False
                break

        if deps_met:
            ready.append((task_info["file"], task))

    return ready

def run_aider(task, context_files, prompt):
    """Call Aider and return the subprocess result."""
    aider_model = CONFIG["model"]

    cmd = [
        "uv", "run", "aider",
        "--model", aider_model,
        "--message", prompt,
        "--yes",
        "--no-git-commit",
        "--no-auto-commits",
        *context_files
    ]

    for cf in context_files:
        cf_path = Path(cf)
        if not cf_path.parent.exists():
            log(f"Creating directory {cf_path.parent}", level=1)
            cf_path.parent.mkdir(parents=True, exist_ok=True)

    if "ANTHROPIC_API_KEY" not in os.environ:
        log("CRITICAL ERROR: ANTHROPIC_API_KEY not found in environment!", level=0)

    return subprocess.run(cmd, capture_output=True, text=True, env=os.environ)

def extract_metrics(stdout):
    """Extract token/cost metrics from Aider output."""
    if not stdout:
        return {}
    match = re.search(r"Tokens:?\s*([\d\.k]+)\s*sent,\s*([\d\.k]+)\s*received\.?\s*Cost:?\s*\$([\d\.]+)", stdout, re.IGNORECASE)
    if not match:
        return {}
    def k_to_num(s):
        if 'k' in s.lower():
            try: return f"{float(s.lower().replace('k', '')) * 1000:.0f}"
            except: return s
        return s
    return {
        "tokens_sent": k_to_num(match.group(1)),
        "tokens_received": k_to_num(match.group(2)),
        "cost": float(match.group(3))
    }

def check_false_success(result):
    """Detect cases where Aider exits 0 but the LLM call actually failed."""
    stdout_lower = result.stdout.lower() if result.stdout else ""
    return any(err in stdout_lower for err in ["badrequesterror", "llm provider not provided", "notfounderror"])

def run_task_validations(task, aider_result):
    """Run task-specific validate: commands. Returns (passed, errors)."""
    errors = []
    for cmd_str in task.get("validate", []):
        log(f"Validating: {cmd_str}", level=1)
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"Validation failed: {cmd_str} — stdout: {res.stdout.strip()} stderr: {res.stderr.strip()}")
            if CONFIG["verbose"] < 2:
                log(f"--- AIDER STDOUT ---\n{aider_result.stdout}", level=0)
                log(f"--- AIDER STDERR ---\n{aider_result.stderr}", level=0)
            break
        else:
            log(f"PASSED: {cmd_str}", level=1)
    return (len(errors) == 0, errors)

def execute_task(task_file, task):
    """Execute task with retry logic and guardrails."""
    context_files = task.get("context_files", [])
    skip_guardrails = task.get("guardrails") == "skip"
    max_retries = CONFIG["max_retries"]
    retry_errors = None

    for attempt in range(1, max_retries + 1):
        attempt_label = f"(attempt {attempt}/{max_retries})" if max_retries > 1 else ""
        log(f"Executing task {task['id']}: {task['title']} {attempt_label}", level=0)

        # Snapshot line counts before Aider runs
        pre_line_counts = snapshot_line_counts(context_files)

        # Build prompt (includes error context on retry)
        prompt = build_prompt(task, retry_errors=retry_errors)

        # Run Aider
        result = run_aider(task, context_files, prompt)

        # Extract metrics
        metrics = extract_metrics(result.stdout)
        if metrics:
            log(f"Metrics: Sent={metrics['tokens_sent']}, Received={metrics['tokens_received']}, Cost=${metrics['cost']:.4f}", level=1)
            task["metrics"] = metrics

        # Check exit code
        if result.returncode != 0:
            log(f"{task['id']} ✗ Aider failed (code {result.returncode})", level=0)
            log(f"AIDER STDOUT:\n{result.stdout}", level=2)
            log(f"AIDER STDERR:\n{result.stderr}", level=2)
            retry_errors = [f"Aider exited with code {result.returncode}"]
            continue

        # Check false success
        if check_false_success(result):
            log(f"{task['id']} ✗ Aider reported success but LiteLLM/API failed.", level=0)
            log(f"--- AIDER STDOUT ---\n{result.stdout}", level=0)
            return False

        log(f"{task['id']} Aider finished successfully", level=1)
        log(f"AIDER STDOUT:\n{result.stdout}", level=2)

        # Run guardrails (unless skipped)
        all_errors = []
        if not skip_guardrails:
            guardrails_passed, guardrail_errors = run_guardrails(context_files, pre_line_counts)
            if not guardrails_passed:
                for err in guardrail_errors:
                    log(f"{task['id']} ✗ {err}", level=0)
                all_errors.extend(guardrail_errors)

        # Run task-specific validations (even if guardrails failed, to collect all errors)
        validation_passed, validation_errors = run_task_validations(task, result)
        if not validation_passed:
            for err in validation_errors:
                log(f"{task['id']} ✗ {err}", level=0)
            all_errors.extend(validation_errors)

        if all_errors:
            log(f"{task['id']} ✗ Task failed with {len(all_errors)} error(s).", level=0)
            retry_errors = all_errors
            continue

        # All checks passed
        task["status"] = "done"
        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_file.write_text(yaml.dump(task, sort_keys=False))
        log(f"{task['id']} ✓ All validations passed.", level=0)

        commit_msg = f"chore(task): Complete task {task['id']} - {task['title']}"
        subprocess.run(["git", "add", "."], check=False)
        commit_result = subprocess.run(["git", "commit", "-m", commit_msg], check=False, capture_output=True, text=True)
        if commit_result.returncode == 0:
            log(f"Committed changes for task {task['id']}", level=1)
        else:
            log(f"No changes to commit for task {task['id']}", level=1)

        return True

    log(f"{task['id']} ✗ Exhausted {max_retries} retries.", level=0)
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Factory Orchestrator")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (v: verbose, vv: debug)")
    args = parser.parse_args()

    CONFIG["verbose"] = args.verbose

    failed_tasks = set()
    while True:
        tasks = get_ready_tasks()
        ready_to_run = [t for t in tasks if str(t[1]['id']) not in failed_tasks]

        if not ready_to_run:
            log("No more tasks ready for execution or all remaining tasks are blocked.", level=0)
            break

        any_success = False
        for task_file, task in ready_to_run:
            success = execute_task(task_file, task)
            if success:
                any_success = True
            else:
                failed_tasks.add(str(task['id']))

        if not any_success:
            break
