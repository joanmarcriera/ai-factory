import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict
from urllib.parse import urlparse

def check_ssl(hostname: str, port: int = 443) -> Dict:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issuer = cert['issuer']
                subject = cert['subject']
                not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.today()).days
                is_valid = days_until_expiry > 0
                error = None
    except ssl.SSLError as e:
        is_valid = False
        error = str(e)
        issuer = None
        subject = None
        not_before = None
        not_after = None
        days_until_expiry = None
    except socket.error as e:
        is_valid = False
        error = str(e)
        issuer = None
        subject = None
        not_before = None
        not_after = None
        days_until_expiry = None
    return {
        'hostname': hostname,
        'issuer': issuer,
        'subject': subject,
        'not_before': not_before,
        'not_after': not_after,
        'days_until_expiry': days_until_expiry,
        'is_valid': is_valid,
        'error': error
    }

def check_ssl_for_sites(sites: list) -> list:
    results = []
    for site in sites:
        if site['ssl_check']:
            hostname = urlparse(site['url']).hostname
            if hostname is None:
                hostname = site['url']  # fallback to full URL if parsing fails
            results.append(check_ssl(hostname))
    return results

if __name__ == '__main__':
    import yaml
    with open('config/sites.yaml', 'r') as f:
        sites = yaml.safe_load(f)
    results = check_ssl_for_sites(sites['sites'])
    import json
    print(json.dumps(results, indent=4))
