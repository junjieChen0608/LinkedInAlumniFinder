from tkinter import Tk

from src.alumnifinder.gui.app import App

root = Tk()  # initializes tkinter
app = App(root)  # creates window with bar and decorations specified by window manager
root.mainloop()  # makes window appear
