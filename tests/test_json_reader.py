from alumnifinder.utils import jsonreader


class TestJsonReader:
    """Contains unit tests for json reader."""

    def test_cred_json(self):
        """Shows how to parse cred.json file."""
        data = jsonreader.get_credentials()
        assert type(data) == list
        assert len(data) > 0
        for account in data:
            assert len(account.get("email")) > 0
            assert len(account.get("password")) > 0

    def test_web_json(self):
        """Shows how to parse web.json file."""
        data = jsonreader.get_web_elements()
        assert type(data) == list
        assert len(data) > 0
        for entry in data:
            assert type(entry) == dict
            assert entry.get('target') is not None
            assert type(entry.get('target')) == str
            assert type(entry.get('routes')) == list
            assert type(entry.get('html')) == list
            assert type(entry.get('xpath')) == list

    def test_patterns_json(self):
        """Shows how to parse patterns.json."""
        data = jsonreader.get_patterns()
        assert type(data) == list
        assert len(data) > 0
        for pattern in data:
            assert type(pattern) == dict
            assert pattern.get('category') is not None
            assert type(pattern.get('category')) == str
            assert type(pattern.get('data')) == list
            assert len(pattern.get('data')) > 0
