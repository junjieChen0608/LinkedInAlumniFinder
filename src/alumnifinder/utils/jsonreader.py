import json

from selenium.webdriver.common.by import By

from src.alumnifinder import config


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


def get_flag(elem: str):
    if elem == 'id':
        return By.ID
    elif elem == 'class':
        return By.CLASS_NAME
    elif elem == 'css':
        return By.CSS_SELECTOR
    elif elem == 'link_text':
        return By.LINK_TEXT
    elif elem == 'name':
        return By.NAME
    elif elem == 'partial_link_text':
        return By.PARTIAL_LINK_TEXT
    elif elem == 'xpath':
        return By.XPATH
    elif elem == 'tag_name':
        return By.TAG_NAME


def web_json_failure(index: int, field: str, indicator, new_val):
    with open(config.login_path) as json_file:
        data = json.load(json_file)
        if field == 'html':
            for obj in data[index]['html']:
                if obj['target'] == indicator:
                    obj['valid'] = new_val
                    with open(config.login_path, "w") as json_file:
                        json.dump(data, json_file)


def cred_json_failure(index: int):
    with open(config.credentials_path) as json_file:
        data = json.load(json_file)
        data[index]['valid'] = False
        with open(config.credentials_path, "w") as json_file:
            json.dump(data, json_file)


def get_login_elements() -> list:
    for entry in get_web_elements():
        if entry.get('phase') == 'login-page':
            return [elem for elem in entry.get('html')]
