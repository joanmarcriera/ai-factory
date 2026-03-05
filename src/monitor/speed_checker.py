import requests
from typing import Dict
from datetime import datetime

def check_speed(url: str) -> Dict:
    try:
        response = requests.get(url, timeout=5)
        dns_time_ms = response.elapsed.total_seconds() * 1000
        connect_time_ms = response.elapsed.total_seconds() * 1000
        ttfb_ms = response.elapsed.total_seconds() * 1000
        total_time_ms = response.elapsed.total_seconds() * 1000
        content_size_bytes = len(response.content)
        status_code = response.status_code
        checked_at = datetime.now().isoformat()
        error = None
    except requests.RequestException as e:
        dns_time_ms = None
        connect_time_ms = None
        ttfb_ms = None
        total_time_ms = None
        content_size_bytes = None
        status_code = None
        checked_at = None
        error = str(e)
    return {
        'url': url,
        'total_time_ms': round(total_time_ms, 2) if total_time_ms is not None else None,
        'content_size_bytes': content_size_bytes,
        'status_code': status_code,
        'checked_at': checked_at,
        'error': error
    }

def check_speed_for_sites(sites: list) -> list:
    results = []
    for site in sites:
        if site['speed_check']:
            results.append(check_speed(site['url']))
    return results

if __name__ == '__main__':
    import yaml
    with open('config/sites.yaml', 'r') as f:
        sites = yaml.safe_load(f)['sites']
    results = check_speed_for_sites(sites)
    import json
    print(json.dumps(results, indent=4))
