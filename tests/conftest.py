import pandas as pd
import pytest

# test data
info = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
test_dict = {
    'FIRST_NAME': info,
    'LAST_NAME': info,
    'WORK_TITLE': info,
    'WORK_COMPANY_NAME1': info,
    'SCHOOL1': info,
    'SCHOOL3': info
}


@pytest.fixture(scope='session')
def xlsx_file(tmpdir_factory):
    """Creates a temporary .xlsx file for all tests."""
    excel_file = 'test.xlsx'
    xlsx_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))  # attaches to /tmp directory
    df = pd.DataFrame(test_dict)
    writer = pd.ExcelWriter(xlsx_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='TestSheet1')
    writer.save()
    return xlsx_file_path


@pytest.fixture(scope='session')
def xls_file(tmpdir_factory):
    """Creates a temporary .xls file for all tests."""
    excel_file = 'test.xls'
    xls_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))  # attaches to /tmp directory
    df = pd.DataFrame(test_dict)
    writer = pd.ExcelWriter(xls_file_path, engine='xlwt')
    df.to_excel(writer, sheet_name='TestSheet1', index=False)
    writer.save()
    return xls_file_path


@pytest.fixture(scope='session')
def csv_file(tmpdir_factory):
    """Creates a temporary .csv file for all tests."""
    csv_file = 'test.csv'
    csv_file_path = str(tmpdir_factory.mktemp('test').join(csv_file))  # attaches to /tmp directory
    df = pd.DataFrame(test_dict)
    df.to_csv(csv_file_path, index=False)
    return csv_file_path
