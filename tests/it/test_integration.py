import pytest

from src.alumnifinder.excel.handler import Handler
from src.alumnifinder.finder.crawler import Crawler


@pytest.mark.skip(reason="Cannot currently test.")
class TestIntegration:
    """Contains integration tests"""

    def test_integration_1(self, xls_file):
        optional = dict({'job_position': 'Software Engineer',
                         'geolocation': 'Buffalo'})
        h = Handler(excel_file=xls_file)
        c = Crawler(data=h.data, **{'jobPosition': 'Software Engineer'})
        assert type(c.job_position) == str
