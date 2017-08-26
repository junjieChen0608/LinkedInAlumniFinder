import json
from src.alumnifinder import config

def store_creds(email: str, password: str) -> None:
    """
        Write the creds.json with user input credentials
    """
    with open(config.credentials_path, 'r+') as json_file:
        account_list = json.load(json_file)
        dummy_account = account_list[0]
        dummy_account['email'] = email
        dummy_account['password'] = password
        dummy_account['valid'] = "True"
        account_list[0] = dummy_account
        json_file.seek(0)
        json.dump(account_list, json_file)
        json_file.truncate()
