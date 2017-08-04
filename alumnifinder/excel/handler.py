import numpy as np
import pandas as pd


class Handler:
    """Used to process the Excel file data.

    Attributes:
        data (pandas DataFrame): DataFrame representation of the Excel file.
        size (int): number of rows in the DataFrame.
        headers (list of str): all of the headers that exist in the DataFrame
        indexes (dict): holds the indexes of the headers based on the value.

    """

    def __init__(self, excel_file):
        self.data = self.read_excel(excel_file)
        self.size = len(self.data)
        self.headers = self.get_headers()
        self.indexes = self.find_indexes()

    def read_excel(self, excel_file: str) -> pd.DataFrame:
        """Determines which engine to use based on type of excel file.

        Args:
            excel_file: path to excel file

        Returns:
             A 'pandas' DataFrame object. This allows for more flexible data analysis and does not modify the original
             excel file.

        Raises:
            ValueError: Any file type other than excel.
        """
        if excel_file.endswith(".xls"):
            return pd.read_excel(excel_file, engine='xlrd')
        elif excel_file.endswith(".xlsx"):
            return pd.read_excel(excel_file)
        else:
            raise ValueError("Invalid file type.")

    def get_headers(self) -> list:
        """Checks if file contains headers.

        Stores headers as a member variable if true.

        Returns:
             list containing all of the column headers

        Raises:
            ValueError: If file doesn't contain headers, there's no way to interpret the data.
        """
        for col in list(self.data.columns.values):
            if type(col) is int:
                raise ValueError("File must contain headers, not numerical values.")
            elif type(col) is not str:
                raise ValueError("File must contain headers.")
        return list(self.data.columns.values)

    def find_indexes(self) -> dict:
        """Gets the indexes of the columns that we are interested in.

        Returns:
            dict of the values with the updated indexes.
        """
        # TODO: make more dynamic (if possible)
        # TODO: Determine if this method is still necessary.
        col_targets = dict()
        if self.headers is not None:
            for index, col_name in enumerate(self.headers):
                if col_name == 'FIRST_NAME':
                    col_targets[col_name] = index
                elif col_name == 'LAST_NAME':
                    col_targets[col_name] = index
                elif col_name == 'WORK_TITLE':
                    col_targets[col_name] = index
                elif col_name == 'WORK_COMPANY_NAME1':
                    col_targets[col_name] = index
                elif col_name == 'SCHOOL1':
                    col_targets[col_name] = index
                elif col_name == 'SCHOOL3':
                    col_targets[col_name] = index
        return col_targets

    def find_divisor(self) -> int:
        """Finds the highest divisor that can divide our data equally.

        Returns:
            (int) highest divisor that can divide our data equally.
        """
        if self.size < 2:
            return 1
        else:
            # TODO: find maximum amount of drivers our machine can handle
            max_drivers = 20  # amount of drivers we can run on our machine.
            highest = 2
            lowest = len(self.data)
            for i in range(2, self.size):
                if (self.size % i) <= lowest:
                    lowest = self.size % i
                    if highest < i < max_drivers:
                        highest = i
            return highest

    def split_data(self, num: int) -> list:
        """Splits DataFrame into a list of DataFrames.

        In order to pass seperate sections of data to multiple Crawlers, we use this to split the DataFrame object by
        some number.

        Args:
         num (int): number to divide all of the data by.

        Returns:
            list of DataFrames, each of these DataFrames hold the values of the headers. This is used for indexing the
            rows by their column name, they are NOT part of the actual DataFrame object.
        """
        return np.array_split(self.data, num)
