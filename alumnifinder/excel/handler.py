class Excel:
    """Contains various methods that will be shared by the handler classes."""
    pass


class XlsHandler(Excel):
    """Read/writing .xls file."""
    pass


class XlsxHandler(Excel):
    """Read/writing .xlsx file."""
    pass


def get(excel_file):
    """Determines which parser to use based on type of excel file."""
    if excel_file.endswith(".xls"):
        return XlsHandler
    elif excel_file.endswith(".xlsx"):
        return XlsxHandler
    else:
        raise ValueError("Invalid file type.")
