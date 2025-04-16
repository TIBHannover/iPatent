import yaml

def load_config():
    with open('/app/shared/config.yaml', 'r') as rf:
        return yaml.safe_load(rf)