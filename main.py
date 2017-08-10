from tkinter import *

import click

from alumnifinder.excel.handler import Handler
from alumnifinder.gui.app import App


@click.command()
@click.option('--gui', is_flag=True)
@click.option('-e', '--excel', type=click.Path(exists=True))
@click.option('-s', '--start', type=int)
@click.option('-f', '--finish', type=int)
def main(gui, excel, start, finish):
    """CLI version of the alumnifinder app."""
    if gui:
        root = Tk()  # initializes tkinter
        app = App(root)  # creates window with bar and decorations specified by window manager
        root.mainloop()  # makes window appear
    elif excel:
        if start and finish:
            handler = Handler(excel_file=excel, start=start, end=finish)
        else:
            handler = Handler(excel_file=excel)
    else:
        pass


if __name__ == '__main__':
    main()
