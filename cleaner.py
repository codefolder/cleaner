import os.path
import pickle
import random

from tkinter import Button
from tkinter import END
from tkinter import Entry
from tkinter import Frame
from tkinter import Label
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox
from psutil._compat import xrange

__author__="codefolder@users.noreply.github.com"

class Cleaner(Tk):
    def __init__(self, parent):
        Tk.__init__(self,parent)
        ################# class scope variable initialization ##############
        self.cleanAllRequested = False # flag which is set when only a batch dialog is needed, supresses the dir confirm dialogs
        self.settingsFileName = "cleaner.pickle"
        self.__pathpanels__ = {} # __pathpanels__ = {intPanelNumber:[instanceOfPanelakaTkFrame, entryWidget]}
        self.__persistentStorage__ = [] # [[panelNumber, entry.get()],[...]]        
        ####################################################################
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Key-Escape>", lambda event: self.destroy())

        self.mainFrm = Frame(self,name="mainFrm",relief="raised",border=1)
        self.mainFrm.pack(fill="x",padx=3,pady=3)
        ################# class scope variable initialization ##############
        self.restoreState() # __pathpanels__
        ####################################################################        
        buttonAddDir = Button(self,text="Add new", command=lambda: self.createNewPathPanel(addNewPanel=True))
        buttonCleanAll = Button(self,text="Clean all", command=lambda: self.purgeAllDirectories())
        buttonCleanAll.pack(side="right",anchor="n",padx=20,pady=8)
        buttonAddDir.pack(side="right",anchor="n",padx=0,pady=8)

        self.center()      
        try:
            settingsFile = open(self.settingsFileName,"rb")
            self.__persistentStorage__ = pickle.load(settingsFile)
            settingsFile.close()
        except IOError:
            print("Could not load settings file.")
 

    def center(self):
        ############## center on screen ################        
        self.update()        
        ww, wh, w, h = self.winfo_screenwidth(), self.winfo_screenheight(), self.winfo_width(), self.winfo_height()
        self.geometry("%dx%d+%d+%d" % (684,h,(ww-w)/2,(wh-h)/2))
        ################################################

    def destroy(self):
        self.saveState()
        self.quit()

    def restoreState(self):
        try:
            settingsFile = open(self.settingsFileName,"rb")
            self.__persistentStorage__ = pickle.load(settingsFile)
            settingsFile.close()
        except IOError:
            print("Could not load settings file.")
        for i in self.__persistentStorage__:
            self.createNewPathPanel(panelNumber=i[0], pathToDir=i[1])

    def saveState(self):
        try:
            settingsFile = open(self.settingsFileName,"wb")
            pickle.dump(self.__persistentStorage__, settingsFile)
            settingsFile.close()
        except IOError:
            print("Could not save settings file.")
        
    def createNewPanelNumber(self):
        panelNumber = random.randint(0, 999999)
        while panelNumber in self.__pathpanels__:
            panelNumber = random.randint(0, 999999)
        return panelNumber

    def processEvent(self, panelNumber, cmd):
        if panelNumber and cmd is not None:
            entryWidget = self.__pathpanels__[panelNumber][1]
            ########################### debug ################################
            print ("--- The order ["+cmd+"] is dispatched from panel number ["+str(panelNumber)+"] ---")
            print ("--- Entry text reads ["+entryWidget.get()+"] ---")
            ##################################################################
            if cmd == "Relinquish":
                #################### remove panel from gui ###################
                self.__pathpanels__[panelNumber][0].grid_forget()
                self.__pathpanels__.pop(panelNumber)
                self.geometry("") # re-pack toplevel
                #################### remove panel from storage ###############
                for i in xrange(0, len(self.__persistentStorage__)):
                    if self.__persistentStorage__[i][0]==panelNumber:
                        self.__persistentStorage__.pop(i)
                        break
                ##############################################################
                return
            
            if cmd == "Change":
                #################### change path in gui ########################
                currDir = entryWidget.get()
                pathToDir = filedialog.askdirectory(initialdir=currDir,parent=self,title="Choose a directory to clean",mustexist=True)
                if not pathToDir:
                    return
                else:
                    entryWidget.delete(0, END)
                    entryWidget.insert(0, pathToDir)
                #################### change path in storage ####################
                    for i in xrange(0, len(self.__persistentStorage__)):
                        if self.__persistentStorage__[i][0]==panelNumber:
                            self.__persistentStorage__[i][1]=pathToDir
                            break
            if cmd == "Clean":
                ##### purge root directory of all files and subdirectories #####
                rootDir = entryWidget.get()
                self.purgeDirectory(rootDir)
                ################################################################

    def createNewPathPanel(self, panelNumber=None, pathToDir=None, addNewPanel=False):
        usrhome = os.path.expanduser('~')
        if not pathToDir: # create panel from scratch
            pathToDir = filedialog.askdirectory(initialdir=usrhome,parent=self,title="Choose a directory to clean",mustexist=True)
            if not pathToDir: # file dialog cancelled or closed by user
                return
        if not panelNumber: # continue creating panel from scratch
            panelNumber = self.createNewPanelNumber()
        # in this section it does not matter if the panel is created from scratch or not - the same execution code
        frm = Frame(self.mainFrm,name=str(panelNumber),relief="raised",border=1)
        frm.grid()
        label = Label(frm, text="Path to directory: ")
        entry = Entry(frm, width=40)
        entry.insert(0, pathToDir)
        buttonRemove = Button(frm,text="Relinquish",command=lambda pn=panelNumber,cmd="Relinquish": self.processEvent(pn,cmd))
        buttonChange = Button(frm,text="Change",command=lambda pn=panelNumber,cmd="Change": self.processEvent(pn,cmd))
        buttonClean = Button(frm,text="Clean",command=lambda pn=panelNumber,cmd="Clean": self.processEvent(pn,cmd))
        # The following lines recently started to cause a GUI geometry conflict
        #label.pack(side="left",anchor="w",padx=1,pady=1)
        #entry.pack(side="left",fill="x",expand="True",padx=1,pady=1)
        label.grid(row=0,padx=1,pady=1)
        entry.grid(row=0,column=1,padx=1,pady=1)
        buttonRemove.grid(row=0,column=2,padx=1,pady=1)
        buttonChange.grid(row=0,column=3,padx=1,pady=1)
        buttonClean.grid(row=0,column=4,padx=1,pady=1)
        self.__pathpanels__[panelNumber] = [frm, entry]
        if addNewPanel:
            self.__persistentStorage__.append([panelNumber,entry.get()])
            self.geometry("") # some trick! not to be found in any docs! needs a null parameter to re-pack.

    def purgeAllDirectories(self):
        confirmed = messagebox.askyesno(
            message="Clean all directories by deleting all files in them?",
            icon="question", title="Final sanity check");
        if not confirmed: return
        self.cleanAllRequested = True
        for i in self.__pathpanels__.keys():
            self.purgeDirectory(self.__pathpanels__[i][1].get())
        self.cleanAllRequested = False

    def purgeDirectory(self,  rootDir=None):
        if rootDir == None: return
        if self.cleanAllRequested == False: # not to bring up dialog for every dir in a batch
            confirmed = messagebox.askyesno(
                message="Delete all files in this directory?",
                icon="question", title="Final sanity check");
            if not confirmed: return
        if os.access(rootDir,  os.F_OK):
            print("Path ["+rootDir+"] exists, ok.")
        else:
            print("Path ["+rootDir+"] does not exist.")
            return
        if os.access(rootDir,  os.W_OK):
            print("...and I even have write access! Nice...")
            print("Attempting to enumerate files...\n-------------------")
            for root, dirs, files in os.walk(rootDir,  topdown=False): # False to start walking from farthermost subfolders all the way to the root directory
                print(root+" [ROOT-DIR]")
                for fileName in files:
                    print(fileName)
                    os.remove(os.path.join(root, fileName)) # this is dangerous
                for dirName in dirs:
                    print(dirName+" [dir]")
                    os.rmdir(os.path.join(root, dirName)) # this is dangerous
        else:
            print("...oops, ran into a problem: no write access to directory! Sorry...")
if __name__ == "__main__":
    app = Cleaner(None)
    app.resizable(False, False)
    app.title("Cleaner - v1.1")
    app.center()
    app.mainloop()
    
