# GUI file for LinkedIN People Finder App
# Written by Jared Brown 7/3/17

from tkinter import *
from tkinter import filedialog as fd

from alumnifinder.finder import crawler
from alumnifinder.gui import images

validFileTypes = ("*.xlsx", "*.xls")
miDict = {}
file = ""


class App:
    def __init__(self, master):
        self.file_path = ""
        master.title("LinkedIN People Finder")
        frame = Frame(master)
        frame.pack()
        frame.config(padx=5, pady=5)

        try:
            self.logo = PhotoImage(file=images.logo)
            self.logo = self.logo.subsample(5, 5)
            self.ublogo = Label(frame, image=self.logo)
            self.ublogo.grid(row=0)
        except:
            print("file not found")

        self.appTitle = Label(frame, text="UB LinkedIN Alumni People Finder")
        self.appTitle.grid(row=0, column=1, columnspan=2)

        # left side; manual input fields
        start_row = 2
        self.leftLabel = Label(frame, text="Manually enter an Alumni.")
        self.leftLabel.grid(row=1, columnspan=2)
        self.l1 = Label(frame, text="First Name: ")
        self.l2 = Label(frame, text="Last Name: ")
        self.l3 = Label(frame, text="School: ")
        self.l4 = Label(frame, text="Graduation Year: ")
        self.l5 = Label(frame, text="Major: ")
        self.l6 = Label(frame, text="Degree: ")
        self.l1.grid(row=start_row, sticky=W)
        self.l2.grid(row=start_row + 1, sticky=W)
        self.l3.grid(row=start_row + 2, sticky=W)
        self.l4.grid(row=start_row + 3, sticky=W)
        self.l5.grid(row=start_row + 4, sticky=W)
        self.l6.grid(row=start_row + 5, sticky=W)

        self.e1 = Entry(frame)  # first name
        self.e2 = Entry(frame)  # last name
        self.e3 = Entry(frame)  # school
        self.e4 = Entry(frame)  # graduation yr
        self.e5 = Entry(frame)  # major
        self.e6 = Entry(frame)  # degree
        self.e1.grid(row=start_row, column=1)
        self.e2.grid(row=start_row + 1, column=1)
        self.e3.grid(row=start_row + 2, column=1)
        self.e4.grid(row=start_row + 3, column=1)
        self.e5.grid(row=start_row + 4, column=1)
        self.e6.grid(row=start_row + 5, column=1)

        okbtn = Button(frame, text="OK", command=self.ok)
        okbtn.grid(row=start_row + 6, columnspan=2, pady=5)
        # end manual input fields

        # right side, file explorer for excel file
        self.rightLabel = Label(frame, text="Search for a document.")
        self.rightLabel.grid(row=1, column=2, padx=5)
        open_file_btn = Button(frame, text="...", command=self.search_file)
        open_file_btn.grid(row=start_row, column=2)

    # end file input

    def search_file(self):
        self.file_path = fd.askopenfile(initialdir="/", title="Select file",
                                        filetypes=[("Excel Files", validFileTypes), ("All Files", "*.*")])
        # xlsx and xls
        if self.file_path is None:
            print("No File Selected")
        else:
            print("file path: " + self.file_path.name)
            file_type = self.file_path.name.split('.')
            print("type: " + file_type[1])
            if file_type[1] != "xlsx" and file_type[1] != "xls":
                types = ""
                for x in validFileTypes:
                    if x == validFileTypes[-1]:
                        types += x
                    else:
                        types += x + ", "
                self.err_message("File type invalid.\nValid file types are: " + types)

    def ok(self):
        # first,last must be mandatory
        miDict["firstName"] = self.e1.get().strip()
        miDict["lastName"] = self.e2.get().strip()
        miDict["school"] = self.e3.get().strip()
        miDict["gradYr"] = self.e4.get().strip()
        miDict["major"] = self.e5.get().strip()
        miDict["degree"] = self.e6.get().strip()
        print(miDict)
        dict_filled = False
        for val in miDict.values():
            if val != "":
                dict_filled = True

        if dict_filled and self.file_path != "":
            self.err_message("You cannot do manual search and batch search at the same time.")
        elif not dict_filled and self.file_path != "":
            c = crawler.LinkedinCrawler(miDict, self.file_path.name)
            c.crawl_linkedin()
        elif self.file_path == "" and (miDict["firstName"] == "" or miDict["lastName"] == ""):
            self.err_message("First and last name are required for manual search.")
        else:
            c = crawler.LinkedinCrawler(miDict, "")
            c.crawl_linkedin()
            print(miDict["firstName"] + " " + miDict["lastName"] + " " + miDict["school"] + " " +
                  miDict["gradYr"] + " " + miDict["major"] + " " + miDict["degree"])

    def err_message(self, text):
        top = Toplevel()
        top.title("Error")
        top.configure(width=100)
        msg = Message(top, text=text, justify="center")
        msg.configure(width=250)
        msg.pack()
        print("no name")
