import pytest

from alumnifinder.finder.crawler import Crawler


class TestCrawler:
    """Contains unit tests for Crawler."""

    def test_empty_init(self):
        with pytest.raises(ValueError):
            Crawler()

    def test_init(self):
        c = Crawler(linkedin_area='Buffalo')
        assert c.linkedin_area == 'Buffalo'

    def test_incorrect_args(self):
        with pytest.raises(TypeError):
            Crawler(incorrect_arg=42)
