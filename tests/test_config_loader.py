import pytest
from src.monitor.config_loader import load_sites, validate_site, load_and_validate

def test_load_sites_returns_list():
    sites = load_sites()
    assert isinstance(sites, list)

def test_validate_site_valid():
    site = {
        'name': 'Example Corp',
        'url': 'https://example.com',
        'check_interval_seconds': 300,
        'ssl_check': True,
        'speed_check': True,
        'alert_email': 'examplecorp@example.com'
    }
    assert validate_site(site)

def test_validate_site_missing_key():
    site = {
        'name': 'Example Corp',
        'url': 'https://example.com',
        'check_interval_seconds': 300,
        'ssl_check': True,
        'speed_check': True
    }
    assert not validate_site(site)

def test_load_sites_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_sites('nonexistent.yaml')
