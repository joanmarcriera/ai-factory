import requests
from typing import List, Dict

def evaluate_alerts(uptime_results: List[Dict], ssl_results: List[Dict]) -> List[Dict]:
    alerts = []
    for result in uptime_results:
        if not result['is_up']:
            alerts.append({
                'site_name': result['site_name'],
                'alert_type': 'site_down',
                'severity': 'critical',
                'message': f"Site {result['site_name']} is down",
                'triggered_at': result['timestamp']
            })
    for result in ssl_results:
        if result['days_until_expiry'] <= 0:
            alerts.append({
                'site_name': result['site_name'],
                'alert_type': 'ssl_expired',
                'severity': 'critical',
                'message': f"SSL certificate for {result['site_name']} has expired",
                'triggered_at': result['timestamp']
            })
        elif result['days_until_expiry'] <= 14:
            alerts.append({
                'site_name': result['site_name'],
                'alert_type': 'ssl_expiring',
                'severity': 'warning',
                'message': f"SSL certificate for {result['site_name']} will expire in {result['days_until_expiry']} days",
                'triggered_at': result['timestamp']
            })
    for result in uptime_results:
        if result['response_time_ms'] > 3000:
            alerts.append({
                'site_name': result['site_name'],
                'alert_type': 'slow_response',
                'severity': 'warning',
                'message': f"Site {result['site_name']} has a slow response time of {result['response_time_ms']}ms",
                'triggered_at': result['timestamp']
            })
    return alerts

def format_alert_text(alert: Dict) -> str:
    return f"Alert: {alert['alert_type']} for {alert['site_name']} - {alert['message']}"

def send_webhook_alert(webhook_url: str, alert: Dict) -> None:
    headers = {'Content-Type': 'application/json'}
    data = {'alert': alert}
    response = requests.post(webhook_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error sending webhook alert: {response.text}")

if __name__ == '__main__':
    uptime_results = [
        {'site_name': 'Example Corp', 'is_up': False, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 4000},
        {'site_name': 'Test Shop', 'is_up': True, 'timestamp': '2023-03-01 12:00:00', 'response_time_ms': 2000}
    ]
    ssl_results = [
        {'site_name': 'Example Corp', 'days_until_expiry': 0, 'timestamp': '2023-03-01 12:00:00'},
        {'site_name': 'Test Shop', 'days_until_expiry': 15, 'timestamp': '2023-03-01 12:00:00'}
    ]
    alerts = evaluate_alerts(uptime_results, ssl_results)
    for alert in alerts:
        print(format_alert_text(alert))
        send_webhook_alert('https://example.com/webhook', alert)
