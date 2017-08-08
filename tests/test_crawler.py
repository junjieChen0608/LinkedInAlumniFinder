from alumnifinder.excel.handler import Handler
from alumnifinder.finder.crawler import Crawler


class TestCrawler:
    """Contains unit tests for Crawler."""

    def test_init(self, xls_file):
        h = Handler(xls_file)
        c = Crawler(data=h.data)
        print(c.data)
