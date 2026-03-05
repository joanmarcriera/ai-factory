import pytest
from unittest.mock import patch
import requests  # Add this line
from src.monitor.uptime_checker import check_uptime

def test_check_uptime_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.elapsed.total_seconds.return_value = 0.5
        result = check_uptime('https://example.com')
        assert result['is_up'] is True

def test_check_uptime_failure():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        result = check_uptime('https://example.com')
        assert result['is_up'] is False

def test_check_uptime_returns_dict():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.elapsed.total_seconds.return_value = 0.5
        result = check_uptime('https://example.com')
        assert isinstance(result, dict)
        assert 'site_name' not in result
        assert 'url' in result
        assert 'is_up' in result
        assert 'status_code' in result
        assert 'response_time_ms' in result
        assert 'timestamp' in result
