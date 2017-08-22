from sys import platform

import pandas as pd
import pytest
from selenium import webdriver

from src.alumnifinder.finder import drivers


def get_test_data() -> dict:
    """Returns a dictionary based on the data that our code expects.

    Excel files are expected to contain the following columns:
    ID_NUMBER, FIRST_NAME, LAST_NAME, WORK_TITLE, WORK_COMPANY_NAME1, WORK_CITY, WORK_STATE_CODE, SCHOOL1, DEGREE_CODE1
    DEGREE_YEAR1, MAJOR1, SCHOOL2, DEGREE_CODE2, DEGREE_YEAR2, MAJOR3, SCHOOL3, DEGREE_CODE3, DEGREE_YEAR3, MAJOR3

    Any other columns in the excel file will not affect the execution or result of the code.

    Returns:
        A dictionary filled with test data
    """
    id_numbers = ['0000000001', '0000000002', '0000000003', '0000000004', '0000000005', '0000000006', '0000000007',
                  '0000000008', '0000000009', '0000000010']
    first_names = ['Jane', 'John', 'Kathy', 'Kevin', 'Leslie', 'Lamar', 'Megan', 'Matthew', 'Nancy', 'Nick']
    last_names = ['Jones', 'James', 'King', 'Kelly', 'Lee', 'Lewis', 'Morgan', 'Martin', 'Nicholson', 'Newman']
    job_titles = ['Project Manager', 'Software Engineer', 'Financial Manger', 'Java Developer', 'Business Analyst',
                  'Systems Engineer', 'Network Engineer', 'Senior Software Engineer', 'Web Developer',
                  'Systems Administrator']
    company_names = ['Apple Inc.', 'Amazon.com', 'Alphabet Inc.', 'Microsoft', 'IBM', 'Dell Technologies', 'Intel',
                     'Hewlett Packard Enterprise', 'Oracle', 'Salesforce.com']
    company_city = ['Cupertino', 'Seattle', 'Mountain View', 'Redmond', 'Armonk', 'Austin', 'Santa Clara', 'Palo Alto',
                    'Redwood City', 'San Francisco']
    company_states = ['CA', 'WA', 'CA', 'WA', 'NY', 'TX', 'CA', 'CA', 'CA', 'CA']
    school1 = ['School of Engineering & Applied Science'] * len(id_numbers)
    school2 = ['School of Engineering & Applied Science', '', '', 'School of Engineering & Applied Science', '', '', '',
               'School of Engineering & Applied Science', 'School of Engineering & Applied Science', '']
    school3 = [''] * len(id_numbers)
    major1 = ['Computer Science', 'Computer Engineering', 'Aerospace Engineering', 'Electrical Engineering',
              'Aerospace Engineering', 'Electrical Engineering', 'Computer Science', 'Computer Engineering',
              'Civil Engineering', 'Computer Science']
    major2 = ['Computer Engineering', '', '', 'Computer Science', '', '', '', 'Industrial & Systems Engineering',
              'Computer Science', '']
    major3 = [''] * len(id_numbers)
    degree_code1 = ['Ph.D.', 'B.S.', 'B.S.', 'M.S.', 'B.S.', 'B.S.', 'B.S.', 'M.S.', 'M.S.', 'B.S.']
    degree_code2 = ['M.S.', '', '', 'B.S.', '', '', '', 'B.S.', 'B.S.', '']
    degree_code3 = [''] * len(id_numbers)
    degree_year1 = ['2003', '2016', '2016', '2016', '2016', '2016', '2007', '2010', '2002', '2009']
    degree_year2 = ['1998', '', '', '2012', '', '', '', '2008', '2000', '']
    degree_year3 = [''] * len(id_numbers)
    return {
        'ID_NUMBER': id_numbers,
        'FIRST_NAME': first_names,
        'LAST_NAME': last_names,
        'WORK_TITLE': job_titles,
        'WORK_COMPANY_NAME1': company_names,
        'WORK_CITY': company_city,
        'WORK_STATE_CODE': company_states,
        'SCHOOL1': school1,
        'DEGREE_CODE1': degree_code1,
        'DEGREE_YEAR1': degree_year1,
        'MAJOR1': major1,
        'SCHOOL2': school2,
        'DEGREE_CODE2': degree_code2,
        'DEGREE_YEAR2': degree_year2,
        'MAJOR2': major2,
        'SCHOOL3': school3,
        'DEGREE_CODE3': degree_code3,
        'DEGREE_YEAR3': degree_year3,
        'MAJOR3': major3
    }


@pytest.fixture(scope='session')
def xlsx_file(tmpdir_factory):
    """Creates a '.xlsx' file located in 'temporary' directory."""
    excel_file = 'test.xlsx'
    xlsx_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))
    df = pd.DataFrame(get_test_data())
    writer = pd.ExcelWriter(xlsx_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='TestSheet1', index=False)
    writer.save()
    return xlsx_file_path


@pytest.fixture(scope='session')
def xls_file(tmpdir_factory):
    """Creates a '.xls' file located in 'temporary' directory."""
    excel_file = 'test.xls'
    xls_file_path = str(tmpdir_factory.mktemp('test').join(excel_file))
    df = pd.DataFrame(get_test_data())
    writer = pd.ExcelWriter(xls_file_path, engine='xlwt')
    df.to_excel(writer, sheet_name='TestSheet1', index=False)
    writer.save()
    return xls_file_path


@pytest.fixture(scope='session')
def csv_file(tmpdir_factory):
    """Creates a '.csv' file located in 'temporary' directory."""
    csv_file = 'test.csv'
    csv_file_path = str(tmpdir_factory.mktemp('test').join(csv_file))
    df = pd.DataFrame(get_test_data())
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
