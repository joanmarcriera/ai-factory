---
description: Project Coding Conventions and Guidelines
---

# OVERALL GOAL
We are building a "Website Monitoring & Maintenance" toolkit — a set of scripts and configurations that:
1. Monitor website uptime, SSL expiry, and page speed for multiple client sites
2. Generate automated monthly health reports
3. Alert on issues via email/webhook
4. Run as a self-hosted solution using Docker (Uptime Kuma) and Python scripts

# PYTHON CONVENTIONS
- Use Python 3.12+ with type hints on all function signatures.
- Use `pathlib.Path` instead of `os.path`.
- Use f-strings for string formatting.
- Follow PEP 8 with 4-space indentation.
- Use `yaml.safe_load` / `yaml.safe_dump` for YAML handling.
- Use `argparse` for CLI tools.
- Use `requests` for HTTP calls. Do NOT use `urllib`.
- All scripts must be executable via `uv run python <script>`.
- **NO PLACEHOLDERS & NO REGRESSIONS**: Never use comments like `# Rest of code...` or truncate files. You must always maintain the complete file contents.
- **NO DUPLICATE FUNCTIONS**: Never create two functions with the same name in the same file.

# SHELL SCRIPT CONVENTIONS
- Use `#!/usr/bin/env bash` shebang.
- Use `set -euo pipefail` at the top.
- Quote all variables: `"${var}"`.

# DOCKER / DOCKER COMPOSE CONVENTIONS
- Use `docker-compose.yml` (v3.8+ syntax).
- Pin image versions (no `latest` tags).
- Use named volumes for persistent data.
- Expose only necessary ports.

# CONFIGURATION CONVENTIONS
- All client/site configuration goes in `config/sites.yaml`.
- Secrets (API keys, SMTP credentials) go in `.env` and are NEVER committed.
- Config schema is defined in `config/schema.yaml`.

# FILE STRUCTURE
```
src/
  monitor/        # Core monitoring scripts
  reports/        # Report generation
  alerts/         # Alert/notification logic
config/
  sites.yaml      # Site configurations
  schema.yaml     # Config validation schema
docker/
  docker-compose.yml
scripts/
  setup.sh        # Initial setup script
tests/
  test_monitor.py
  test_reports.py
```

# VALIDATION RULES
- Every Python file must pass `python -m py_compile <file>`.
- Config files must be valid YAML (`python -c "import yaml; yaml.safe_load(open('<file>'))"` must succeed).
- Docker compose must pass `docker compose config -q` (or equivalent dry-run).
