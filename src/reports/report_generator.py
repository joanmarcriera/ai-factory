import datetime
import json

def generate_report(uptime_results, ssl_results, speed_results, report_date):
    report = {
        "report_date": report_date,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_sites": len(uptime_results),
            "sites_up": len([result for result in uptime_results if result["status"] == "up"]),
            "sites_down": len([result for result in uptime_results if result["status"] == "down"]),
            "avg_response_time_ms": sum(result["response_time_ms"] for result in uptime_results) / len(uptime_results) if uptime_results else 0,
            "ssl_issues_count": len([result for result in ssl_results if result["status"] == "issue"])
        },
        "sites": []
    }

    for result in uptime_results:
        site = {
            "name": result["name"],
            "uptime_status": result["status"],
            "response_time_ms": result["response_time_ms"],
            "ssl_days_remaining": None,
            "page_size_bytes": None
        }
        report["sites"].append(site)

    for result in ssl_results:
        for site in report["sites"]:
            if site["name"] == result["name"]:
                site["ssl_days_remaining"] = result["days_remaining"]

    for result in speed_results:
        for site in report["sites"]:
            if site["name"] == result["name"]:
                site["page_size_bytes"] = result["page_size_bytes"]

    return report

def render_report_text(report):
    report_text = f"Report Date: {report['report_date']}\n\n"
    report_text += f"Summary:\n"
    report_text += f"  Total Sites: {report['summary']['total_sites']}\n"
    report_text += f"  Sites Up: {report['summary']['sites_up']}\n"
    report_text += f"  Sites Down: {report['summary']['sites_down']}\n"
    report_text += f"  Average Response Time (ms): {report['summary']['avg_response_time_ms']}\n"
    report_text += f"  SSL Issues Count: {report['summary']['ssl_issues_count']}\n\n"

    report_text += "Sites:\n"
    for site in report["sites"]:
        report_text += f"  {site['name']}\n"
        report_text += f"    Uptime Status: {site['uptime_status']}\n"
        report_text += f"    Response Time (ms): {site['response_time_ms']}\n"
        report_text += f"    SSL Days Remaining: {site['ssl_days_remaining']}\n"
        report_text += f"    Page Size (bytes): {site['page_size_bytes']}\n\n"

    return report_text

def save_report(report, output_dir):
    report_json = json.dumps(report, indent=4)
    with open(f"{output_dir}/report_{report['report_date']}.json", "w") as f:
        f.write(report_json)

    report_text = render_report_text(report)
    with open(f"{output_dir}/report_{report['report_date']}.txt", "w") as f:
        f.write(report_text)

if __name__ == "__main__":
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

    report_date = datetime.date.today().strftime("%Y-%m-%d")
    report = generate_report(uptime_results, ssl_results, speed_results, report_date)
    save_report(report, "reports_output")
