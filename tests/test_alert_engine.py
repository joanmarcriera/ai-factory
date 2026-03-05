"""
Tests for alert engine
"""
import pytest
from src.alerts.alert_engine import evaluate_alerts, format_alert_text

def test_site_down_generates_critical_alert():
    uptime_results = [
        {'site_name': 'Example Corp', 'is_up': False, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 4000},
        {'site_name': 'Test Shop', 'is_up': True, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 2000}
    ]
    alerts = evaluate_alerts(uptime_results, [])
    assert len(alerts) == 1
    assert alerts[0]['alert_type'] == 'site_down'
    assert alerts[0]['severity'] == 'critical'
    assert format_alert_text(alerts[0]) != ''

def test_ssl_expiring_generates_warning():
    ssl_results = [
        {'site_name': 'Example Corp', 'days_until_expiry': 7, 'timestamp': '2023-03-01 12:00:00'},
        {'site_name': 'Test Shop', 'days_until_expiry': 15, 'timestamp': '2023-03-01 12:00:00'}
    ]
    alerts = evaluate_alerts([], ssl_results)
    assert len(alerts) == 1
    assert alerts[0]['alert_type'] == 'ssl_expiring'
    assert alerts[0]['severity'] == 'warning'
    assert format_alert_text(alerts[0]) != ''

def test_no_alerts_when_healthy():
    uptime_results = [
        {'site_name': 'Example Corp', 'is_up': True, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 2000},
        {'site_name': 'Test Shop', 'is_up': True, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 2000}
    ]
    ssl_results = [
        {'site_name': 'Example Corp', 'days_until_expiry': 30, 'timestamp': '2023-03-01 12:00:00'},
        {'site_name': 'Test Shop', 'days_until_expiry': 30, 'timestamp': '2023-03-01 12:00:00'}
    ]
    alerts = evaluate_alerts(uptime_results, ssl_results)
    assert len(alerts) == 0

def test_format_alert_text_returns_string():
    alert = {'alert_type': 'site_down', 'site_name': 'Example Corp', 'severity': 'critical', 'message': 'Site Example Corp is down'}
    assert isinstance(format_alert_text(alert), str)
    assert format_alert_text(alert) != ''
