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
                os.environ[key.strip()] = value.strip()

load_env()

# --- Configuration ---
CONFIG = {
    "model": os.environ.get("AI_MODEL", "haiku"),
    "max_retries": 2,
    "log_file": ".orchestrator/log.txt",
    "verbose": 0  # 0: normal, 1: verbose, 2: debug
}

def log(message, level=0):
    """Log to file and console if level <= CONFIG['verbose']."""
    log_path = Path(CONFIG["log_file"])
    log_path.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    # Always log to file
    with open(log_path, "a") as f:
        f.write(f"{formatted_message}\n")
    
    # Only print if level matches verbosity
    if level <= CONFIG["verbose"]:
        print(formatted_message)

def get_ready_tasks():
    """Return tasks with status=pending and all dependencies done, sorted by ID."""
    ready = []
    tasks_dir = Path("tasks")
    if not tasks_dir.exists():
        return []

    task_files = sorted(tasks_dir.glob("*.yaml"))
    for task_file in task_files:
        try:
            task = yaml.safe_load(task_file.read_text())
        except Exception as e:
            log(f"Error loading {task_file}: {e}", level=0)
            continue
        
        if task.get("status") != "pending":
            continue
        
        deps_met = True
        for dep in task.get("depends_on", []):
            dep_path = Path(f"tasks/{dep}.yaml")
            if not dep_path.exists():
                deps_met = False
                log(f"Dependency {dep} for task {task.get('id')} not found.", level=0)
                break
            
            dep_task = yaml.safe_load(dep_path.read_text())
            if dep_task.get("status") != "done":
                deps_met = False
                break
        
        if deps_met:
            ready.append((task_file, task))
    return ready

def execute_task(task_file, task):
    """Execute task with Aider via uv."""
    context_files = task.get("context_files", [])
    prompt = f"Task: {task['title']}\n\nComplete when:\n" + \
             "\n".join(f"- {item}" for item in task['done_when']) + \
             "\n\nGenerate necessary code changes."
    
    cmd = [
        "uv", "run", "aider",
        "--model", CONFIG["model"],
        "--message", prompt,
        "--yes",
        "--no-git-commit",
        "--no-auto-commits",
        *context_files
    ]
    
    # Ensure directories for context_files exist
    for cf in context_files:
        cf_path = Path(cf)
        if not cf_path.parent.exists():
            log(f"Creating directory {cf_path.parent}", level=1)
            cf_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Executing task {task['id']}: {task['title']}", level=0)
    
    if "ANTHROPIC_API_KEY" not in os.environ:
        log("CRITICAL ERROR: ANTHROPIC_API_KEY not found in environment!", level=0)

    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    
    # Metrics
    metrics = {}
    if result.stdout:
        match = re.search(r"Tokens:?\s*([\d\.k]+)\s*sent,\s*([\d\.k]+)\s*received\.?\s*Cost:?\s*\$([\d\.]+)", result.stdout, re.IGNORECASE)
        if match:
            def k_to_num(s):
                if 'k' in s.lower():
                    try: return f"{float(s.lower().replace('k', '')) * 1000:.0f}"
                    except: return s
                return s
            metrics = {
                "tokens_sent": k_to_num(match.group(1)),
                "tokens_received": k_to_num(match.group(2)),
                "cost": float(match.group(3))
            }
            log(f"Metrics: Sent={metrics['tokens_sent']}, Received={metrics['tokens_received']}, Cost=${metrics['cost']:.4f}", level=1)
            task["metrics"] = metrics

    if result.returncode != 0:
        log(f"{task['id']} ✗ Aider failed (code {result.returncode})", level=0)
        log(f"AIDER STDOUT:\n{result.stdout}", level=2)
        log(f"AIDER STDERR:\n{result.stderr}", level=2)
        return
    else:
        log(f"{task['id']} Aider finished successfully", level=1)
        log(f"AIDER STDOUT:\n{result.stdout}", level=2)
        
        # Verify that context files are NOT empty if they were supposed to be created
        for cf in context_files:
            cf_path = Path(cf)
            if cf_path.exists() and cf_path.stat().st_size == 0:
                log(f"WARNING: {cf} is EMPTY. Aider might have failed to write content.", level=0)

    # Validation
    validation_passed = True
    for cmd_str in task.get("validate", []):
        log(f"Validating: {cmd_str}", level=1)
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            validation_passed = False
            log(f"{task['id']} ✗ Validation failed: {cmd_str}", level=0)
            log(f"Val STDERR: {res.stderr}", level=1)
            log(f"Val STDOUT: {res.stdout}", level=1)
            # Full debug info on failure
            if CONFIG["verbose"] < 2:
                log(f"Run with -vv to see full Aider logs for debugging.", level=0)
            break
        else:
            log(f"PASSED: {cmd_str}", level=1)

    if validation_passed:
        task["status"] = "done"
        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_file.write_text(yaml.dump(task, sort_keys=False))
        log(f"{task['id']} ✓ All validations passed.", level=0)
    else:
        log(f"{task['id']} ✗ Task failed.", level=0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Factory Orchestrator")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (v: verbose, vv: debug)")
    args = parser.parse_args()
    
    CONFIG["verbose"] = args.verbose
    
    tasks = get_ready_tasks()
    if not tasks:
        log("No tasks ready for execution.", level=0)
    
    for task_file, task in tasks:
        execute_task(task_file, task)
