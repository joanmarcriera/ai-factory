import requests
from datetime import datetime
import time

def check_uptime(url: str, timeout: int = 10) -> dict:
    start_time = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        response_time_ms = round((time.time() - start_time) * 1000, 2)
        return {
            'url': url,
            'status_code': response.status_code,
            'response_time_ms': response_time_ms,
            'is_up': 200 <= response.status_code < 400,
            'checked_at': datetime.now().isoformat(),
            'error': None
        }
    except requests.RequestException as e:
        return {
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'is_up': False,
            'checked_at': datetime.now().isoformat(),
            'error': str(e)
        }

def check_all_sites(sites: list) -> list:
    return [check_uptime(site['url']) for site in sites]

if __name__ == '__main__':
    import yaml
    sites = yaml.safe_load(open('config/sites.yaml'))['sites']
    results = check_all_sites(sites)
    import json
    print(json.dumps(results, indent=4))
