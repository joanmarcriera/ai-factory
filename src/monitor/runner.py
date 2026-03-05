import argparse
from datetime import datetime, date
from src.monitor import config_loader, uptime_checker, ssl_checker, speed_checker
from src.alerts import alert_engine
from src.reports import report_generator
from urllib.parse import urlparse
import os

def run_checks(config_path: str = 'config/sites.yaml', output_dir: str = 'reports_output') -> dict:
    # Load sites
    sites = config_loader.load_and_validate(config_path)
    
    # Run checks
    raw_uptime = uptime_checker.check_all_sites(sites)
    raw_ssl = ssl_checker.check_ssl_for_sites(sites)
    raw_speed = speed_checker.check_speed_for_sites(sites)
    
    # Create mappings
    url_to_name = {site['url']: site['name'] for site in sites}
    hostname_to_name = {}
    url_to_site = {site['url']: site for site in sites}
    hostname_to_site = {}
    for site in sites:
        hostname = urlparse(site['url']).hostname
        if hostname:
            hostname_to_name[hostname] = site['name']
            hostname_to_site[hostname] = site
    
    # Transform uptime results
    transformed_uptime = []
    for result in raw_uptime:
        site = url_to_site.get(result['url'])
        if site:
            site_name = site['name']
            alert_threshold_ms = site['alert_threshold_ms']
        else:
            site_name = url_to_name.get(result['url'], result['url'])
            alert_threshold_ms = 3000  # default
        transformed = {
            'site_name': site_name,
            'name': site_name,
            'url': result['url'],
            'is_up': result['is_up'],
            'status': 'up' if result['is_up'] else 'down',
            'response_time_ms': result['response_time_ms'],
            'timestamp': result['checked_at'],
            'error': result['error'],
            'status_code': result['status_code'],
            'alert_threshold_ms': alert_threshold_ms
        }
        transformed_uptime.append(transformed)
    
    # Transform SSL results
    transformed_ssl = []
    for result in raw_ssl:
        hostname = result['hostname']
        site = hostname_to_site.get(hostname)
        if site:
            site_name = site['name']
            ssl_expiry_warning_days = site['ssl_expiry_warning_days']
        else:
            site_name = hostname_to_name.get(hostname, hostname)
            ssl_expiry_warning_days = 14  # default
        days = result['days_until_expiry']
        is_valid = result['is_valid']
        if not is_valid:
            status = 'issue'
        else:
            status = 'issue' if days <= ssl_expiry_warning_days else 'valid'
        transformed = {
            'site_name': site_name,
            'name': site_name,
            'hostname': hostname,
            'days_until_expiry': days,
            'days_remaining': days,
            'is_valid': is_valid,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'error': result.get('error'),
            'ssl_expiry_warning_days': ssl_expiry_warning_days
        }
        transformed_ssl.append(transformed)
    
    # Transform speed results
    transformed_speed = []
    for result in raw_speed:
        site_name = url_to_name.get(result['url'], result['url'])
        transformed = {
            'name': site_name,
            'url': result['url'],
            'page_size_bytes': result['content_size_bytes']
        }
        transformed_speed.append(transformed)
    
    # Evaluate alerts
    alerts = alert_engine.evaluate_alerts(transformed_uptime, transformed_ssl)
    
    # Generate report
    report_date = date.today().strftime("%Y-%m-%d")
    report = report_generator.generate_report(transformed_uptime, transformed_ssl, transformed_speed, report_date)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    report_generator.save_report(report, output_dir)
    
    # Print summary
    total_sites = len(sites)
    sites_up = sum(1 for r in transformed_uptime if r['is_up'])
    sites_down = total_sites - sites_up
    alerts_count = len(alerts)
    print(f"Checked {total_sites} sites: {sites_up} up, {sites_down} down, {alerts_count} alerts")
    
    return {
        'uptime_results': transformed_uptime,
        'ssl_results': transformed_ssl,
        'speed_results': transformed_speed,
        'alerts': alerts,
        'report': report
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run website monitoring checks')
    parser.add_argument('--config', default='config/sites.yaml', help='Path to sites config file')
    parser.add_argument('--output-dir', default='reports_output', help='Directory to save reports')
    args = parser.parse_args()
    run_checks(args.config, args.output_dir)
