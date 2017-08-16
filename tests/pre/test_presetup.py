class TestPreSetup:
    """Contains pre-setup tests. Checks to make sure packages outside of pip are installed."""

    def test_tkinter(self):
        """Checks if Tkinter is pre-installed."""
        import tkinter
        assert type(tkinter.TkVersion) == float

    def test_python_version(self):
        """Checks if correct python version is installed."""
        import sys
        assert sys.version_info[0] == 3  # major python version
        assert 3 < sys.version_info[1] < 6  # minor python version

    def test_make(self):
        """Checks if 'make' is installed."""
        try:
            import subprocess
            # subprocess.call(["make", "--help"])
        except OSError as e:
            import errno
            if e.errno == errno.ENOENT:
                raise OSError("\'make\' not installed")
            else:
                raise e  # other error
