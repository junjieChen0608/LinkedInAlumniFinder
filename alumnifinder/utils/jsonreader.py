import json

from alumnifinder import config


def get_credentials() -> list:
    """Opens cred.json and returns list interpretation."""
    with open(config.credentials_path) as json_file:
        return json.load(json_file)


def get_web_elements() -> list:
    """Opens web.json and returns list interpretation."""
    with open(config.login_path) as json_file:
        return json.load(json_file)


def get_patterns() -> list:
    """Opens patterns.json and returns list interpretation."""
    with open(config.patterns_path) as json_file:
        return json.load(json_file)
