#!/usr/bin/env bash
set -euo pipefail

# Create required directories
mkdir -p config reports_output docker

# Check and create config/sites.yaml if missing
if [ ! -f config/sites.yaml ]; then
    echo "Creating config/sites.yaml from template..."
    cat > config/sites.yaml <<'EOF'
sites:
  - name: Example Corp
    url: https://example.com
    check_interval_seconds: 300
    ssl_check: true
    speed_check: true
    alert_email: examplecorp@example.com
  - name: Test Shop
    url: https://test-shop.example.org
    check_interval_seconds: 300
    ssl_check: true
    speed_check: true
    alert_email: testshop@example.org
  - name: Local Bakery
    url: https://localbakery.co.uk
    check_interval_seconds: 300
    ssl_check: true
    speed_check: true
    alert_email: localbakery@localbakery.co.uk
EOF
else
    echo "Using existing config/sites.yaml"
fi

# Check and create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env with sample values..."
    cat > .env <<'EOF'
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASS=password
WEBHOOK_URL=http://webhook.url
EOF
else
    echo "Using existing .env"
fi

# Check Docker and Docker Compose versions
echo "Checking Docker version..."
docker --version

echo "Checking Docker Compose version..."
docker-compose --version

echo 'Setup complete. Edit config/sites.yaml and .env before running.'
