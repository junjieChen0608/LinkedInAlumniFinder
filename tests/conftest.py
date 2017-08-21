from sys import platform

import pandas as pd
import pytest
from selenium import webdriver

from src.alumnifinder.finder import drivers

# Test data to be used in files mentioned
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
    """Creates a '.xlsx' file located in 'temporary' directory."""
    excel_file = 'test.xlsx'
    xlsx_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))
    df = pd.DataFrame(test_dict)
    writer = pd.ExcelWriter(xlsx_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='TestSheet1', index=False)
    writer.save()
    return xlsx_file_path


@pytest.fixture(scope='session')
def xls_file(tmpdir_factory):
    """Creates a '.xls' file located in 'temporary' directory."""
    excel_file = 'test.xls'
    xls_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))
    df = pd.DataFrame(test_dict)
    writer = pd.ExcelWriter(xls_file_path, engine='xlwt')
    df.to_excel(writer, sheet_name='TestSheet1', index=False)
    writer.save()
    return xls_file_path


@pytest.fixture(scope='session')
def csv_file(tmpdir_factory):
    """Creates a '.csv' file located in 'temporary' directory."""
    csv_file = 'test.csv'
    csv_file_path = str(tmpdir_factory.mktemp('test').join(csv_file))
    df = pd.DataFrame(test_dict)
    df.to_csv(csv_file_path, index=False)
    return csv_file_path


@pytest.fixture(scope='session')
def driver():
    """Sets up the driver depending on which operating system is currently being used."""
    if platform.startswith('linux'):
        chrome_path = drivers.LINUX_DRIVER_PATH
    elif platform.startswith('darwin'):
        chrome_path = drivers.MAC_DRIVER_PATH
    elif platform.startswith('win32') or platform.startswith('cygwin'):
        chrome_path = drivers.WIN_DRIVER_PATH
    else:
        raise OSError("Unsupported operating system.")
    return webdriver.Chrome(chrome_path)
