import numpy as np
import pandas as pd


class Handler:
    """Used to process the Excel file data.

    Args:
        excel_file (str): the file path of input excel
        kwargs:
        - start (int): start row number, 1-based row number in spread sheet
        - end (int): end row number

    Attributes:
        data (pandas DataFrame): DataFrame representation of the Excel file.
        headers (list of str): all of the headers that exist in the DataFrame
        size (int): number of rows in the DataFrame.
        start_row(int): 0-based start row index in the DataFrame representation
        end_row(int): end row index
    """

    def __init__(self, excel_file: str, **kwargs):
        self.data = self.read_excel(excel_file)
        self.headers = self.check_headers()
        self.size = len(self.data)
        if 'start' in kwargs and 'end' in kwargs:
            self.check_start_finish(kwargs['start'], kwargs['finish'])
            self.start_row, self.end_row = self.parse_search_range(kwargs['start'], kwargs['end'])
            self.divided_data = self.data.iloc[self.start_row:self.end_row]
            self.divided_data_size = len(self.divided_data)
        elif ('start' in kwargs and 'end' not in kwargs) or ('start' not in kwargs and 'end' in kwargs):
            raise ValueError('Not enough start/end arguments.')

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

    def check_headers(self) -> list:
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

    def parse_search_range(self, start: int, end: int) -> (int, int):
        """Parse input search range to 0-based index for the handler to divide

        Args:
            start (int): start row number
            end (int): end row number

        Returns:
            A tuple of 0-based start and end index
        """
        if not start or not end:
            return (0, self.size)
        elif end > self.size:
            return (start - 2, self.size)
        else:
            return (start-2, end-1)

    def check_start_finish(self, start: int, finish: int) -> None:
        """Error checking start and finish"""
        if start < 0:
            raise ValueError("Start option cannot be negative")
        elif finish < 0:
            raise ValueError("Finish option cannot be negative")
        elif start > finish:
            raise ValueError("Start option cannot be greater than finish option")
        elif finish < start:
            raise ValueError("Finish option cannot be smaller than start option")
        else:
            pass
