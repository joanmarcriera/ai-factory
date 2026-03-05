"""
Tests for report generator
"""
import pytest
from src.reports.report_generator import generate_report, render_report_text

def test_generate_report_returns_dict():
    uptime_results = [
        {"name": "Example Corp", "status": "up", "response_time_ms": 100},
        {"name": "Test Shop", "status": "down", "response_time_ms": 200},
        {"name": "Local Bakery", "status": "up", "response_time_ms": 50}
    ]

    ssl_results = [
        {"name": "Example Corp", "status": "issue", "days_remaining": 30},
        {"name": "Test Shop", "status": "valid", "days_remaining": 60},
        {"name": "Local Bakery", "status": "issue", "days_remaining": 15}
    ]

    speed_results = [
        {"name": "Example Corp", "page_size_bytes": 1000},
        {"name": "Test Shop", "page_size_bytes": 2000},
        {"name": "Local Bakery", "page_size_bytes": 500}
    ]

    report_date = "2023-03-05"
    report = generate_report(uptime_results, ssl_results, speed_results, report_date)
    assert isinstance(report, dict)
    assert "report_date" in report
    assert "generated_at" in report
    assert "summary" in report
    assert "sites" in report

def test_summary_fields():
    uptime_results = [
        {"name": "Example Corp", "status": "up", "response_time_ms": 100},
        {"name": "Test Shop", "status": "down", "response_time_ms": 200},
        {"name": "Local Bakery", "status": "up", "response_time_ms": 50}
    ]

    ssl_results = [
        {"name": "Example Corp", "status": "issue", "days_remaining": 30},
        {"name": "Test Shop", "status": "valid", "days_remaining": 60},
        {"name": "Local Bakery", "status": "issue", "days_remaining": 15}
    ]

    speed_results = [
        {"name": "Example Corp", "page_size_bytes": 1000},
        {"name": "Test Shop", "page_size_bytes": 2000},
        {"name": "Local Bakery", "page_size_bytes": 500}
    ]

    report_date = "2023-03-05"
    report = generate_report(uptime_results, ssl_results, speed_results, report_date)
    assert "total_sites" in report["summary"]
    assert "sites_up" in report["summary"]
    assert "sites_down" in report["summary"]
    assert "avg_response_time_ms" in report["summary"]
    assert "ssl_issues_count" in report["summary"]

def test_render_report_text_returns_string():
    uptime_results = [
        {"name": "Example Corp", "status": "up", "response_time_ms": 100},
        {"name": "Test Shop", "status": "down", "response_time_ms": 200},
        {"name": "Local Bakery", "status": "up", "response_time_ms": 50}
    ]

    ssl_results = [
        {"name": "Example Corp", "status": "issue", "days_remaining": 30},
        {"name": "Test Shop", "status": "valid", "days_remaining": 60},
        {"name": "Local Bakery", "status": "issue", "days_remaining": 15}
    ]

    speed_results = [
        {"name": "Example Corp", "page_size_bytes": 1000},
        {"name": "Test Shop", "page_size_bytes": 2000},
        {"name": "Local Bakery", "page_size_bytes": 500}
    ]

    report_date = "2023-03-05"
    report = generate_report(uptime_results, ssl_results, speed_results, report_date)
    report_text = render_report_text(report)
    assert isinstance(report_text, str)
    assert report_text != ""
