from tkinter import *

from alumnifinder.gui.app import App

if __name__ == '__main__':
    root = Tk()  # initializes tkinter
    app = App(root)  # creates window with bar and decorations specified by window manager
    root.mainloop()  # makes window appear
