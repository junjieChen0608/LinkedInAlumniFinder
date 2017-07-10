#GUI file for LinkedIN People Finder App
#Written by Jared Brown 7/3/17

import crawler
from tkinter import *
from tkinter import filedialog as fd

validFileTypes=[".xlsx"]
miDict = {}
file=""

class App:
    def __init__(self,master):
        master.title("LinkedIN People Finder")
        frame = Frame(master)
        frame.pack()
        frame.config(padx=5, pady=5)

        self.logo = PhotoImage(file = r".\images\ublogo.gif")
        self.logo = self.logo.subsample(5,5)
        self.ublogo = Label(frame,image=self.logo)
        self.ublogo.grid(row = 0)

        self.appTitle = Label(frame,text="UB LinkedIN Alumni People Finder")
        self.appTitle.grid(row = 0,column=1,columnspan=2)

    # left side; manual input fields
        startRow = 2
        self.leftLabel = Label(frame,text = "Manually enter an Alumni.")
        self.leftLabel.grid(row=1,columnspan=2)
        self.l1 = Label(frame, text="First Name: ")
        self.l2 = Label(frame, text="Last Name: ")
        self.l3 = Label(frame, text="School: ")
        self.l4 = Label(frame, text="Graduation Year: ")
        self.l5 = Label(frame, text="Major: ")
        self.l6 = Label(frame, text="Degree: ")
        self.l1.grid(row=startRow, sticky=W)
        self.l2.grid(row=startRow+1, sticky=W)
        self.l3.grid(row=startRow+2, sticky=W)
        self.l4.grid(row=startRow+3, sticky=W)
        self.l5.grid(row=startRow+4, sticky=W)
        self.l6.grid(row=startRow+5, sticky=W)

        self.e1 = Entry(frame) #first name
        self.e2 = Entry(frame) #last name
        self.e3 = Entry(frame) #school
        self.e4 = Entry(frame) #graduation yr
        self.e5 = Entry(frame) #major
        self.e6 = Entry(frame) #degree
        self.e1.grid(row=startRow, column=1)
        self.e2.grid(row=startRow+1, column=1)
        self.e3.grid(row=startRow+2, column=1)
        self.e4.grid(row=startRow+3, column=1)
        self.e5.grid(row=startRow+4, column=1)
        self.e6.grid(row=startRow+5, column=1)

        okbtn = Button(frame,text = "OK",command=self.ok)
        okbtn.grid(row=startRow+6,columnspan=2,pady=5)
    #end manual input fields

    #right side, file explorer for excel file
        self.rightLabel = Label(frame, text="Search for a document.")
        self.rightLabel.grid(row=1,column=2,padx=5)
        openFileBtn = Button(frame,text = "...",command=self.searchFile)
        openFileBtn.grid(row = startRow, column = 2)
    #end file input

    def searchFile(self):
        file = fd.askopenfile(initialdir="/", title="Select file",
                              filetypes =[("Excel Workbook","*.xlsx"),("All Files","*.*")])
        #xlsx
        if file is None:
            print("No File Selected")
        else:
            print(file.name)
            type=file.name.split('.')
            if(type[1] != "xlsx"):
                types = ""
                for x in validFileTypes:
                    if x == validFileTypes[-1]:
                        types += x
                    else:
                        types += x + ", "
                self.err("File type invalid.\nValid file types are: " + types)

    def ok(self):
        #first,last must be mandatory
        miDict["firstName"] = self.e1.get().strip()
        miDict["lastName"] = self.e2.get().strip()
        miDict["school"] = self.e3.get().strip()
        miDict["gradYr"] = self.e4.get().strip()
        miDict["major"] = self.e5.get().strip()
        miDict["degree"] = self.e6.get().strip()
        print(miDict)
        #school,gradution yr, major, degree
        if miDict["firstName"] == "" or miDict["lastName"] == "":
            self.err("First and last name are required for manual search.")
        else:
            c = crawler.LinkedinCrawler(miDict,"")
            c.crawl_linkedin()
            print(miDict["firstName"] + " " + miDict["lastName"] + " " + miDict["school"] + " " +
                  miDict[" gradYr"] + " " + miDict["major"] + " " + miDict["degree"])

    def err(self,text):
        top = Toplevel()
        top.title("Error")
        top.configure(width=100)
        msg = Message(top,text=text, justify="center")
        msg.configure(width=250)
        msg.pack()
        print("no name")

#initializes tkinter
#creates window with bar and decorations specified by window manager
root = Tk()

app = App(root)

#makes window appear
root.mainloop()