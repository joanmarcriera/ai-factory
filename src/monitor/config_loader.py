import yaml

def load_sites(file_path='config/sites.yaml'):
    with open(file_path, 'r') as f:
        sites = yaml.safe_load(f)
    return sites['sites']

def validate_site(site):
    required_keys = ['name', 'url', 'check_interval_seconds', 'ssl_check', 'speed_check', 'alert_email']
    return all(key in site for key in required_keys)

def load_and_validate(file_path='config/sites.yaml'):
    sites = load_sites(file_path)
    valid_sites = [site for site in sites if validate_site(site)]
    if len(valid_sites) != len(sites):
        raise ValueError(f"Invalid sites: {len(sites) - len(valid_sites)}")
    return valid_sites

if __name__ == '__main__':
    sites = load_and_validate()
    print(f"Number of valid sites: {len(sites)}")
