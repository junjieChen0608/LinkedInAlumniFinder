class TestPreSetup:
    """Contains pre-setup tests."""

    def test_python_version(self):
        """Checks if correct python version is installed."""
        import sys
        assert sys.version_info[0] == 3  # major python version
        assert 3 < sys.version_info[1] < 6  # minor python version

    def test_tkinter(self):
        """Checks if Tkinter is pre-installed."""
        try:
            import tkinter
        except ImportError:
            raise ImportError('\'tkinter\' is required for this project')

    def test_numpy(self):
        """Checks if numpy python module is pre-installed."""
        try:
            import numpy
        except ImportError:
            raise ImportError('\'numpy\' is required for this project')

    def test_pandas(self):
        """Checks if pandas python module is pre-installed."""
        try:
            import pandas
        except ImportError:
            raise ImportError('\'pandas\' is required for this project')

    def test_selenium(self):
        """Checks if selenium python module is pre-installed."""
        try:
            import selenium
        except ImportError:
            raise ImportError('\'selenium\' is required for this project')

    def test_xlrd(self):
        """Checks if xlrd python module is pre-installed."""
        try:
            import xlrd
        except ImportError:
            raise ImportError('\'xlrd\' is required for this project')

    def test_xlsxwriter(self):
        """Checks if xlsxwriter python module is pre-installed."""
        try:
            import xlsxwriter
        except ImportError:
            raise ImportError('\'xlsxwriter\' is required for this project')

    def test_xlutils(self):
        """Checks if xlutils python module is pre-installed."""
        try:
            import xlutils
        except ImportError:
            raise ImportError('\'xlutils\' is required for this project')

    def test_xlwt(self):
        """Checks if xlwt python module is pre-installed."""
        try:
            import xlwt
        except ImportError:
            raise ImportError('\'xlwt\' is required for this project')
