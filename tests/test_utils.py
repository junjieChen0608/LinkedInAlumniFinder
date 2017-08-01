class TestUtils:
    """Contains tests for util functions"""

    def test_json_reader(self):
        """Checks if json reader works"""
        from alumnifinder.utils import jsonreader
        data = jsonreader.get_credentials()
        assert type(data) == list
        assert len(data) > 0
        assert len(data[0].get("email")) > 0
        assert len(data[0].get("password")) > 0
