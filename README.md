# Website Monitoring & Maintenance Service

Automated website health monitoring with uptime checks, SSL certificate validation, page speed analysis, configurable alerts, and automated reports.

## Features

- **Uptime Monitoring** — checks site availability and response times
- **SSL Certificate Checking** — warns before certificates expire
- **Page Speed Analysis** — measures load times and page sizes
- **Configurable Alerts** — webhook notifications for downtime and SSL issues
- **Automated Reports** — daily JSON and plain-text reports

## Quick Start

1. Clone the repo
2. Run `bash scripts/setup.sh`
3. Edit `config/sites.yaml` with your sites
4. Run `python src/monitor/runner.py`

## Configuration

Edit `config/sites.yaml` to define monitored sites:

```yaml
sites:
  - name: "Example Corp"
    url: "https://example.com"
    check_interval_minutes: 5
    alert_threshold_ms: 3000
    ssl_expiry_warning_days: 30
```

Each site requires: `name`, `url`, `check_interval_minutes`, `alert_threshold_ms`, `ssl_expiry_warning_days`.

## Docker

```bash
cd docker
docker compose up --build
```

This starts Uptime Kuma (port 3001) and the monitoring service.

## Project Structure

```
src/
  monitor/
    config_loader.py    # Load and validate sites.yaml
    uptime_checker.py   # HTTP availability checks
    ssl_checker.py      # SSL certificate expiry checks
    speed_checker.py    # Page load speed checks
    runner.py           # Main orchestrator
    logger.py           # Logging configuration
  alerts/
    alert_engine.py     # Alert evaluation and webhooks
  reports/
    report_generator.py # Report generation (JSON + text)
config/
  sites.yaml            # Site definitions
  schema.yaml           # Config schema
docker/
  docker-compose.yml    # Docker services
  Dockerfile            # App container
scripts/
  setup.sh              # Project setup script
tests/
  test_config_loader.py
  test_uptime_checker.py
  test_alert_engine.py
  test_report_generator.py
```
