import numpy as np
import pandas as pd


class Handler:
    """Used to process the Excel file data.
    Args:
        excel_file(str): the file path of input excel
        start(int): start row number, 1-based row number in spread sheet
        end(int): end row number

    Attributes:
        original_data_frame (pandas DataFrame): DataFrame representation of the Excel file.
        original_frame_size (int): number of rows in the DataFrame.
        start_row(int): 0-based start row index in the DataFrame representation
        end_row(int): end row index
        divided_data_frame(pandas DataFrame): A portion of DataFrame that truncated from the original DataFrame
        divided_frame_size(int): the number of rows in the truncated DataFrame
        headers (list of str): all of the headers that exist in the DataFrame
        indexes (dict): holds the indexes of the headers based on the value.
    """

    def __init__(self, excel_file: str, start: int, end: int):
        self.original_data_frame = self.read_excel(excel_file)
        self.original_frame_size = len(self.original_data_frame)
        self.start_row, self.end_row = self.parse_search_range(start, end)
        # the divided data frame is the actual portion that user try to search
        # docker workers can spilt it and distribute them to crawlers
        self.divided_data_frame = self.original_data_frame.iloc[self.start_row:self.end_row]
        self.divided_frame_size = len(self.divided_data_frame)
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
        for col in list(self.original_data_frame.columns.values):
            if type(col) is int:
                raise ValueError("File must contain headers, not numerical values.")
            elif type(col) is not str:
                raise ValueError("File must contain headers.")
        return list(self.original_data_frame.columns.values)

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
        if self.divided_frame_size < 2:
            return 1
        else:
            # TODO: find maximum amount of drivers our machine can handle
            max_drivers = 20  # amount of drivers we can run on our machine.
            highest = 2
            lowest = len(self.original_data_frame)
            for i in range(2, self.divided_frame_size):
                if (self.divided_frame_size % i) <= lowest:
                    lowest = self.divided_frame_size % i
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
        return np.array_split(self.divided_data_frame, num)

    def parse_search_range(self, start: int, end: int) -> (int, int):
        """Parse input search range to 0-based index for the handler to divide

        Args:
            start(int): start row number
            end(int): end row number

        Returns:
            A tuple of 0-based start and end index
        """
        if not start or not end:
            return (0, self.original_frame_size)
        elif end > self.original_frame_size:
            return (start-2, self.original_frame_size)
        else:
            return (start-2, end-1)