import pytest
import xlsxwriter
import xlwt

from alumnifinder.finder.client import Client


class TestClient:
    """Contains unit tests for Client."""

    @pytest.fixture(scope='session')
    def xlsx_file(self, tmpdir_factory):
        """Creates a temporary .xlsx file for testing."""
        excel_file = 'test.xlsx'
        xlsx_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))  # attaches to /tmp directory
        workbook = xlsxwriter.Workbook(xlsx_file_path)
        workbook.add_worksheet()
        workbook.close()
        return xlsx_file_path

    @pytest.fixture(scope='session')
    def xls_file(self, tmpdir_factory):
        """Creates a temporary .xls file for testing."""
        excel_file = 'test.xls'
        workbook = xlwt.Workbook(encoding='utf-8')
        workbook.add_sheet('Sheet1')
        xls_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))  # attaches to /tmp directory
        workbook.save(xls_file_path)
        return xls_file_path

    @pytest.fixture(scope='session')
    def txt_file(self, tmpdir_factory):
        """Creates a temporary .txt file for testing."""
        temp_file = 'test.txt'
        temp_file_path = str(tmpdir_factory.mktemp('test').join(temp_file))  # attaches to /tmp directory
        file = open(temp_file_path, 'w')
        file.write("temp")
        file.close()
        return temp_file_path

    def test_empty_kwargs(self):
        """Checks if an exception is thrown when **kwargs are empty."""
        with pytest.raises(ValueError):
            Client()

    def test_xlsx_init(self, xlsx_file):
        """Checks if .xlsx file is processed correctly."""
        Client(excel_file=xlsx_file)

    def test_xls_init(self, xls_file):
        """Checks if .xls file is processed correctly."""
        Client(excel_file=xls_file)

    def test_other_file_init(self, txt_file):
        """Checks if an exception is thrown when using a non-excel file."""
        with pytest.raises(ValueError):
            Client(excel_file=txt_file)

    def test_kwargs_init(self):
        Client(linkedin_area='New York City')
