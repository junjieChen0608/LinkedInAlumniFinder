import sys

import pytest

from src.alumnifinder.gui.app import App

try:
    from tkinter import Tk
except ImportError:
    pass


@pytest.mark.skipif('tkinter' not in sys.modules, reason="tkinter is required for this project.")
class TestApp:
    """Contains unit-tests for App."""
    def test_init(self):
        root = Tk()
        app = App(root)
