from src.alumnifinder.excel.handler import Handler
from src.alumnifinder.finder.crawler import Crawler


class TestIntegration:
    """Contains integration tests"""

    def test_integration_1(self, xls_file):
        h = Handler(excel_file=xls_file)
        c = Crawler(data=h.data, **{'jobPosition': 'Software Engineer'})
        assert type(c.job_position) == str
