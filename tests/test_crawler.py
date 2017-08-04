from alumnifinder.finder.crawler import Crawler


class TestCrawler:
    """Contains unit tests for Crawler."""

    def test_init(self):
        c = Crawler(linkedin_area='Buffalo')
        assert c.linkedin_area == 'Buffalo'
