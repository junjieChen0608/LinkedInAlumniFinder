import pytest
from selenium.common.exceptions import NoSuchElementException

from src.alumnifinder.utils import jsonreader as json


@pytest.mark.skip(reason="Cannot currently test.")
class TestLogin:
    """Contains tests for LinkedIn's login page"""

    def test_login_elems(self, driver):
        """Check if web elements exist at the login-page. Updates web.json if test fails"""

        for index, entry in enumerate(json.get_web_elements()):
            if entry.get('phase') == 'login-page':
                driver.get(entry.get('route'))
                for obj in entry.get('html'):  # check each object in 'html'
                    if obj.get('valid'):  # True
                        flag = json.get_flag(obj.get('type'))
                        try:
                            driver.find_element(flag, obj.get('target'))
                        except NoSuchElementException:
                            json.web_json_failure(index, 'html', obj.get('target'), False)  # updates JSON
                            raise NoSuchElementException(
                                'At: {}, web element not found!\n'
                                'Fix \"web.json\" at index: {} to continue!'.format(entry.get('route'), index))
                    else:  # still False
                        raise ValueError('In web.json (index: {}),'
                                         ' JSON object(\"valid\") is still false!'.format(index))
                break

    def test_login_creds(self, driver):
        """Check if login credentials work. Updates creds.json if test fails"""

        for index, account in enumerate(json.get_credentials()):
            login_email = None
            login_password = None
            login_submit = None

            if account.get('valid'):
                driver.get('https://www.linkedin.com/')
                obj = json.get_login_elements()
                try:
                    for elem in obj:
                        if elem.get('target') == 'login-email':
                            flag = json.get_flag(elem.get('type'))
                            login_email = driver.find_element(flag, elem.get('target'))
                        elif elem.get('target') == 'login-password':
                            flag = json.get_flag(elem.get('type'))
                            login_password = driver.find_element(flag, elem.get('target'))
                        elif elem.get('target') == 'login-submit':
                            flag = json.get_flag(elem.get('type'))
                            login_submit = driver.find_element(flag, elem.get('target'))
                        else:
                            pass
                except NoSuchElementException:
                    raise NoSuchElementException("Web element not found!")

                login_email.clear()
                login_email.send_keys(account.get('email'))
                login_password.clear()
                login_password.send_keys(account.get('password'))
                login_submit.click()
                if 'Log In or Sign Up' in driver.title:
                    json.cred_json_failure(index)
                    raise ValueError('In cred.json (index: {}): credential failed!'.format(index))
                driver.delete_all_cookies()
            else:
                raise ValueError('In cred.json (index: {}): account is invalid! '
                                 'Update/delete this credential!'.format(index))