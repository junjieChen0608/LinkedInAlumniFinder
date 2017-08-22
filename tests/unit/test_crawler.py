from pandas import read_excel, DataFrame

from src.alumnifinder.finder.crawler import Crawler


class TestCrawler:
    """Contains unit tests for Crawler."""

    def test_init_no_kwargs(self, xls_file):
        df = read_excel(xls_file, engine='xlrd')
        c = Crawler(input_data=df, output_data=df)
        assert type(c.input_data) is DataFrame
        assert type(c.output_data) is DataFrame
        assert type(c.geolocation) is str
        assert type(c.job_position) is str
        assert type(c.row_counter) is int
        assert c.geolocation == ""
        assert c.job_position == ""
        assert c.row_counter == 2
        assert c.driver is None
        c.setup_driver()
        assert c.driver is not None
        c.random_pause()

    def test_init_kwargs(self, xls_file):
        start_row = 3
        end_row = 9
        gl = 'Buffalo'
        jp = 'Software Engineer'
        optional = dict({'start_row': str(start_row),
                         'end_row': str(end_row),
                         'geolocation': str(gl),
                         'job_position': str(jp)})
        df = read_excel(xls_file, engine='xlrd')
        c = Crawler(input_data=df, output_data=df, **optional)
        assert type(c.input_data) is DataFrame
        assert type(c.output_data) is DataFrame
        assert type(c.geolocation) is str
        assert type(c.job_position) is str
        assert type(c.row_counter) is int
        assert c.geolocation != ""
        assert c.geolocation == gl
        assert c.job_position != ""
        assert c.job_position == jp
        assert not (c.row_counter < 2)
        assert c.row_counter == start_row
        assert c.driver is None
        c.setup_driver()
        assert c.driver is not None
        c.random_pause()
