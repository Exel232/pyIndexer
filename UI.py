import tkinter as tk
import tkinter.filedialog as tkfile
import Controller
import os.path


class OutputView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.searchbar = tk.Entry(self)
        self.text = tk.Listbox(self)

        self.searchbar.pack(side="top", fill="x")
        self.text.pack(side="bottom", fill="both", expand=True)
        # add a search bar and a list for found files

    def populateList(self, data):
        self.text.delete(0, "end")
        for d in data:
            self.text.insert("end", d)


class ControlView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.oldlabel = tk.Label(self, text="Old file extension")
        self.newlabel = tk.Label(self, text="New file extension")
        self.oldentry = tk.Entry(self, textvariable=self.parent.oldvar)
        self.newentry = tk.Entry(self, textvariable=self.parent.newvar)

        self.changebutton = tk.Button(self, text="Change file extensions",
                                      command=self.parent.changeClick)

        self.showlabel = tk.LabelFrame(self, text="Output options")
        self.viewlist = tk.Listbox(self.showlabel, selectmode="single")
        self.updatebutton = tk.Button(self.showlabel, text="Update view",
                                      command=self.parent.updateView)
        self.filebutton = tk.Button(self, text="Update file list",
                                    command=self.parent.dirClick)

        # set static content of viewlist
        self.viewlist.insert("end", "Show unlinked")
        self.viewlist.insert("end", "Show linked")
        self.viewlist.insert("end", "Show all")
        # bind listbox changes to viewlist update
        self.viewlist.bind("<<ListboxSelect>>", self.parent.updateView)

        # set layout using grid layout to realize multiple rows of controls
        self.oldlabel.grid(row=0)
        self.oldentry.grid(row=1)
        self.newlabel.grid(row=2)
        self.newentry.grid(row=3)
        self.changebutton.grid(row=4)

        self.showlabel.grid(row=5)

        # implement as listbox instead
        self.viewlist.pack(anchor="e", fill="x")
        self.updatebutton.pack(anchor="e", fill="x")

        self.filebutton.grid(row=6)
        # double entry field for old and new extension name
        # button to do changes
        # button to show files with missing new extensions


class StatusBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.showLog("Welcome to the file linker.")

        self.statuslabel = tk.Label(self, text=self.message, fg=self.color)

        self.statuslabel.pack(side="left", fill="x")

        # statusbar showing output from last operation
        # colored for green - all fine, red - error, black - normal status
    def showLog(self, text):
        self.message = text
        self.color = "black"

    def showSuccess(self, text):
        self.message = text
        self.color = "green"

    def showFailure(self, text):
        self.message = text
        self.color = "red"


class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.oldvar = tk.StringVar(self, ".test")
        self.newvar = tk.StringVar(self, ".new")

        self.parent = parent
        self.output = OutputView(self)
        self.control = ControlView(self)
        self.status = StatusBar(self, borderwidth=1, relief="sunken")

        self.status.pack(side="bottom", fill="x")
        self.control.pack(side="right", fill="y", anchor="center", expand=True)
        self.output.pack(side="left", fill="both", expand=True)

        # load config from file config.txt
        path = self.readDir()
        if path:
            self.controller = Controller.Controller(workingdir=path)
        else:
            self.controller = Controller.Controller(self.updateDir())
        
        expr = self.readExpr()
        if expr:
            self.controller.changeExpr(expr)

    def updateView(self, var="dummy"):
        # get list of files depending on view options
        # view old checked - view old files
        print(var)
        try:
            viewstate = self.control.viewlist.curselection()[0]
        except IndexError:
            self.status.showFailure("No view option selected, try to select a \
                                    view option")
        print(type(viewstate))
        print(viewstate)
        if viewstate == 2:
            result = self.controller.getAll()
            self.output.populateList(result)
            self.status.showLog("Displaying all files")
        elif viewstate == 0:
            result = self.controller.getOld()
            self.output.populateList(result)
            self.status.showLog("Displaying unlinked files")
        else:
            result = self.controller.getNew()
            self.output.populateList(result)
            self.status.showLog("Displaying linked files")

    def updateDir(self):
        newpath = tkfile.askdirectory()
        self.status.showLog("Working directory updated, file list updated")
        # save dir to config file
        with open("dir.txt", "w") as config:
            config.write(newpath)
        return newpath

    def dirClick(self):
        self.controller.changeDir(self.updateDir())
        self.fsUpdate()
        self.updateView()

    def readDir(self):
        configname = "dir.txt"
        if os.path.isfile(configname):
            with open(configname, "r") as configfile:
                dirline = configfile.read()
            return dirline
        else:
            return 0

    def readExpr(self):
        configname = "expr.txt"
        if os.path.isfile(configname):
            with open(configname) as configfile:
                ext1 = configfile.readline()  # old
                ext2 = configfile.readline()  # new
            return ext1, ext2
        else:
            return 0

    def fsUpdate(self):
        self.controller.crawlDir()

    def changeClick(self):
        self.controller.linkFiles()
        self.updateView()
        self.status.showLog("Files linked to new extension")

    def updateExpr(self):
        # get changed extensions from entry fields
        oldstr = self.oldvar
        newstr = self.newvar
        with open("expr.txt", "w") as exprfile:
            exprfile.writeline(oldstr)
            exprfile.writeline(newstr)
        self.status.showSuccess("File endings saved to file")

    def searchChange(self):
        pass


def main():
    root = tk.Tk()
    root.minsize(600, 400)
    root.configure(background='white')
    MainWindow(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == '__main__':
    main()
