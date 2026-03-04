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
    all_tasks = {}
    tasks_dir = Path("tasks")
    if not tasks_dir.exists():
        return []

    # First pass: load all tasks to build a map by ID
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

def execute_task(task_file, task):
    """Execute task with Aider via uv."""
    context_files = task.get("context_files", [])
    prompt = f"Task: {task['title']}\n\nComplete when:\n" + \
             "\n".join(f"- {item}" for item in task['done_when']) + \
             "\n\nGenerate necessary code changes."
             
    # Inject workflows / conventions to ensure determinism
    conventions_file = Path(".agents/workflows/coding-conventions.md")
    if conventions_file.exists():
        prompt += f"\n\n--- THE FOLLOWING ARE CRITICAL PROJECT CONVENTIONS ---\n{conventions_file.read_text()}\n------------------------------------------------------\n"
    
    # Aider likes the model name without the 'anthropic/' prefix if using its own logic,
    # but litellm (which aider uses) sometimes gets confused. 
    # Let's try passing the model exactly as the user provides, but if it fails, 
    # we can try to strip the provider.
    aider_model = CONFIG["model"]
    if "/" in aider_model:
        # If it's a known provider, aider often wants just the model name 
        # but let's be careful. Litellm error suggested it NEEDS provider.
        pass

    cmd = [
        "uv", "run", "aider",
        "--model", aider_model,
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
    
    # Check for "false success" where aider exits 0 but litellm failed
    stdout_lower = result.stdout.lower() if result.stdout else ""
    stderr_lower = result.stderr.lower() if result.stderr else ""
    if any(err in stdout_lower for err in ["badrequesterror", "llm provider not provided", "notfounderror"]):
        log(f"{task['id']} ✗ Aider reported success but LiteLLM/API failed to process the model.", level=0)
        log(f"--- AIDER STDOUT ---\n{result.stdout}", level=0)
        return

    log(f"{task['id']} Aider finished successfully", level=1)
    log(f"AIDER STDOUT:\n{result.stdout}", level=2)
    
    # Verify that context files are NOT empty
    any_empty = False
    for cf in context_files:
        cf_path = Path(cf)
        if cf_path.exists() and cf_path.stat().st_size == 0:
            log(f"ERROR: {cf} is EMPTY. Aider failed to write content.", level=0)
            any_empty = True
    
    if any_empty:
        log(f"{task['id']} ✗ Task failed due to empty context files.", level=0)
        return

    # Validation
    validation_passed = True
    for cmd_str in task.get("validate", []):
        log(f"Validating: {cmd_str}", level=1)
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            validation_passed = False
            log(f"{task['id']} ✗ Validation failed: {cmd_str}", level=0)
            log(f"Val STDERR: {res.stderr}", level=0)
            log(f"Val STDOUT: {res.stdout}", level=0)
            # ALWAYS show Aider output on failure if we haven't already
            if CONFIG["verbose"] < 2:
                log(f"--- AIDER STDOUT ---\n{result.stdout}", level=0)
                log(f"--- AIDER STDERR ---\n{result.stderr}", level=0)
            break
        else:
            log(f"PASSED: {cmd_str}", level=1)

    if validation_passed:
        task["status"] = "done"
        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_file.write_text(yaml.dump(task, sort_keys=False))
        log(f"{task['id']} ✓ All validations passed.", level=0)
        
        # Auto-commit the changes for this task
        commit_msg = f"chore(task): Complete task {task['id']} - {task['title']}"
        subprocess.run(["git", "add", "."], check=False)
        commit_result = subprocess.run(["git", "commit", "-m", commit_msg], check=False, capture_output=True, text=True)
        if commit_result.returncode == 0:
            log(f"Committed changes for task {task['id']}", level=1)
        else:
            log(f"No changes to commit for task {task['id']}", level=1)
            
        return True
    else:
        log(f"{task['id']} ✗ Task failed.", level=0)
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
        
        # If we didn't succeed at any task in this round, no new dependencies will unlock.
        if not any_success:
            break
