import pandas as pd

from src.alumnifinder.finder.crawler import Crawler


class TestCrawler:
    """Contains unit tests for Crawler."""

    def test_init(self, xls_file):
        df = pd.read_excel(xls_file, engine='xlrd')
        c = Crawler(data=df)
        assert type(c.data) is pd.DataFrame
