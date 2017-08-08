from alumnifinder.excel.handler import Handler
from alumnifinder.finder.crawler import Crawler


class TestIntegration:
    """Contains integration tests"""

    def test_integration_1(self, xls_file):
        h = Handler(xls_file)
        c = Crawler(data=h.data, **{'jobPosition': 'Software Engineer'})
        assert type(c.job_position) == str
        # c.crawl_linkedin()  # for debugging
