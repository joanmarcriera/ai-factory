import yaml
import subprocess
import re
from pathlib import Path
from datetime import datetime

CONFIG = {
    "model": "sonnet",
    "max_retries": 2,
    "log_file": ".orchestrator/log.txt"
}

def get_ready_tasks():
    """Return tasks with status=pending and all dependencies done."""
    ready = []
    
    tasks_dir = Path("tasks")
    if not tasks_dir.exists():
        return []

    for task_file in tasks_dir.glob("*.yaml"):
        try:
            task = yaml.safe_load(task_file.read_text())
        except Exception as e:
            log(f"Error loading {task_file}: {e}")
            continue
        
        if task.get("status") != "pending":
            continue
        
        # Check dependencies
        deps_met = True
        for dep in task.get("depends_on", []):
            dep_path = Path(f"tasks/{dep}.yaml")
            if not dep_path.exists():
                deps_met = False
                log(f"Dependency {dep} for task {task.get('id')} not found.")
                break
            
            dep_task = yaml.safe_load(dep_path.read_text())
            if dep_task.get("status") != "done":
                deps_met = False
                break
        
        if deps_met:
            ready.append((task_file, task))
    
    return ready

def execute_task(task_file, task):
    """Execute task with Aider + Claude."""
    
    # Build context
    context_files = task.get("context_files", [])
    
    # Build prompt
    prompt = f"""
Task: {task['title']}

Complete when:
{chr(10).join(f"- {item}" for item in task['done_when'])}

Generate necessary code changes.
"""
    
    # Execute with Aider
    # We use 'uv run aider' to ensure it's running in the project context
    cmd = [
        "aider",
        "--model", CONFIG["model"],
        "--message", prompt,
        "--yes",
        "--no-git-commit",
        "--no-auto-commits",
        *context_files
    ]
    
    log(f"Executing task {task['id']}: {task['title']}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract token info if available
    metrics = {}
    if result.stdout:
        # Regex to capture: Tokens: 2.8k sent, 108 received. Cost: $0.01 message, $0.01 session.
        match = re.search(r"Tokens:\s*([\d\.k]+)\s*sent,\s*([\d\.k]+)\s*received\.\s*Cost:\s*\$([\d\.]+)\s*message", result.stdout)
        if match:
            metrics = {
                "tokens_sent": match.group(1),
                "tokens_received": match.group(2),
                "cost": float(match.group(3))
            }
            log(f"Metrics: Sent={metrics['tokens_sent']}, Received={metrics['tokens_received']}, Cost=${metrics['cost']:.4f}")
            task["metrics"] = metrics

    if result.returncode != 0:
        log(f"{task['id']} ✗ Aider execution failed (return code {result.returncode})")
        log(f"STDOUT: {result.stdout}")
        log(f"STDERR: {result.stderr}")
        return
    else:
        log(f"{task['id']} Aider finished successfully (exit code 0)")
        # log(f"Aider STDOUT: {result.stdout}") # Commented out to reduce log noise, keep if needed
        # log(f"Aider STDERR: {result.stderr}")

    # Check if any changes were actually made (optional but helpful)
    # Aider should have created hello.py for task 001
    
    # Validate
    validation_passed = True
    for cmd_str in task.get("validate", []):
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            validation_passed = False
            log(f"{task['id']} ✗ Validation command failed: {cmd_str}")
            log(f"Validation STDERR: {res.stderr}")
            log(f"Validation STDOUT: {res.stdout}")
            break
    
    # Update status
    if validation_passed:
        task["status"] = "done"
        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_file.write_text(yaml.dump(task, sort_keys=False))
        log(f"{task['id']} ✓ (Metrics stored in YAML)")
    else:
        log(f"{task['id']} ✗ validation failed")

def log(message):
    log_path = Path(CONFIG["log_file"])
    log_path.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    with open(log_path, "a") as f:
        f.write(f"{formatted_message}\n")
    print(formatted_message)

if __name__ == "__main__":
    tasks = get_ready_tasks()
    if not tasks:
        print("No tasks ready for execution.")
    
    for task_file, task in tasks:
        execute_task(task_file, task)
