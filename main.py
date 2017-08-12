from tkinter import *

import click

from src.alumnifinder.excel.handler import Handler
from src.alumnifinder.finder.crawler import Crawler
from src.alumnifinder.gui.app import App


@click.command()
@click.option('--gui', is_flag=True, help="Launch GUI")
@click.option('-e', '--excel', type=click.Path(exists=True), help="Path to excel file")
@click.option('-s', '--start', type=int, help="Index to start (Ignores headers)")
@click.option('-f', '--finish', type=int, help="Index to finish")
@click.option('-j', '--job_position', type=str, help="Job Position")
@click.option('-g', '--geo_location', type=str, help="Geographical location to search")
def main(gui: bool, excel: str, start: int, finish: int, job_position: str, geo_location: str) -> None:
    """CLI version of the AlumniFinder app."""

    if gui:
        root = Tk()  # initializes tkinter
        app = App(root)  # creates window with bar and decorations specified by window manager
        root.mainloop()  # makes window appear
    elif excel:
        if start and finish:
            check_start_finish(start=start, finish=finish)
            handler = Handler(excel_file=excel, start=start, end=finish)
        else:
            arguments = check_if_none(job_position, geo_location)
            handler = Handler(excel_file=excel)
            n = handler.find_divisor()
            pie = handler.split_data(n)
            cage = []
            for slice in pie:
                cage.append(Crawler(slice, **arguments))
                # TODO: implement multi-threading
    else:
        click.echo("Please provide an excel file or use GUI")


def check_start_finish(start: int, finish: int) -> None:
    """Error checking start and finish"""
    if start and not finish:
        raise ValueError("Please specify a finish option")
    elif finish and not start:
        raise ValueError("Please specify a start option")
    elif start < 0:
        raise ValueError("Start option cannot be negative")
    elif finish < 0:
        raise ValueError("Finish option cannot be negative")
    elif start > finish:
        raise ValueError("Start option cannot be greater than finish option")
    elif finish < start:
        raise ValueError("Finish option cannot be smaller than start option")
    else:
        pass


def check_if_none(job_position: str, geo_location: str) -> dict:
    """Options can be type None if they are not used"""
    result = {}
    if job_position is not None:
        result.update({'job_position': job_position})
    if geo_location is not None:
        result.update({'geo_location': geo_location})
    return result


if __name__ == '__main__':
    main()
