import json

from alumnifinder.config import credentials_path


def get_credentials() -> list:
    """Reads json file and returns list interpretation."""
    with open(credentials_path) as json_file:
        return json.load(json_file)
