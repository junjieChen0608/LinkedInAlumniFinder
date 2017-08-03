class Excel:
    """Contains various methods that will be shared by the parser classes."""
    pass


class XlsParser(Excel):
    """Read/writing .xls file."""
    pass


class XlsxParser(Excel):
    """Read/writing .xlsx file."""
    pass


def get(excel_file):
    """Determines which parser to use based on type of excel file."""
    if excel_file.endswith(".xls"):
        return XlsParser
    elif excel_file.endswith(".xlsx"):
        return XlsxParser
    else:
        raise ValueError("Invalid file type.")
