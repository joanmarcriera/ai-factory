# orchestrator.py

import yaml
import subprocess
from pathlib import Path

CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
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
        *context_files
    ]
    
    log(f"Executing task {task['id']}: {task['title']}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        log(f"{task['id']} ✗ Aider execution failed: {result.stderr}")
        return

    # Validate
    validation_passed = True
    for cmd_str in task.get("validate", []):
        if subprocess.run(cmd_str, shell=True).returncode != 0:
            validation_passed = False
            log(f"{task['id']} ✗ Validation command failed: {cmd_str}")
            break
    
    # Update status
    if validation_passed:
        task["status"] = "done"
        task_file.write_text(yaml.dump(task, sort_keys=False))
        log(f"{task['id']} ✓")
    else:
        log(f"{task['id']} ✗ validation failed")

def log(message):
    log_path = Path(CONFIG["log_file"])
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{message}\n")
    print(message)

if __name__ == "__main__":
    tasks = get_ready_tasks()
    if not tasks:
        print("No tasks ready for execution.")
    
    for task_file, task in tasks:
        execute_task(task_file, task)
