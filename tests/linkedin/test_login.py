from selenium.common.exceptions import NoSuchElementException

from src.alumnifinder.utils import jsonreader


class TestLogin:
    def test_login_elems(self, driver):
        """Check if web elements exist at the login-page. Updates web.json if test fails"""
        for index, entry in enumerate(jsonreader.get_web_elements()):
            if entry.get('phase') == 'login-page':
                driver.get(entry.get('route'))
                for obj in entry.get('html'):  # check each object in 'html'
                    if obj.get('valid'):  # True
                        flag = jsonreader.get_flags(obj.get('type'))
                        try:
                            driver.find_element(flag, obj.get('target'))
                        except NoSuchElementException:
                            jsonreader.update_web_json(index, 'html', obj.get('target'), False)  # updates JSON
                            raise NoSuchElementException(
                                'At: {}, web element not found!\n'
                                'Fix \"web.json\" at index: {} to continue!'.format(entry.get('route'), index))
                    else:  # still False
                        raise ValueError('In web.json (index: {}),'
                                         ' JSON object(\"valid\") is still false!'.format(index))
