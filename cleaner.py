#/usr/bin/python3

import os.path
import pickle
import random
from gi.repository import Gtk
from psutil._compat import xrange

__author__="codefolder@users.noreply.github.com"

class Cleaner(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        ################# class scope variable initialization ##############
        self.cleanAllRequested = False # flag which is set when only a batch dialog is needed, supresses the dir confirm dialog
        self.settingsFileName = "cleaner.pickle"
        self.__pathpanels__ = {} # __pathpanels__ = {intPanelNumber:[instanceOfPanel aka Gtk.Box, Gtk.Entry]}
        self.__persistentStorage__ = [] # [[panelNumber, entry.get_text()],[...]]
        ################# class scope variable initialization ##############
        self.box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.restoreState() # __pathpanels__
        ####################################################################
        self.buttonAddDir = Gtk.Button(label="Add new")
        self.buttonCleanAll = Gtk.Button(label="Clean all")
        self.buttonAddDir.connect("clicked", lambda wid: self.createNewPathPanel(addNewPanel=True))
        self.buttonCleanAll.connect("clicked", lambda wid: self.purgeAllDirectories())
        panel = Gtk.Box(spacing=10)
        panel.pack_start(Gtk.Box(), True, True, 0)
        panel.pack_start(self.buttonAddDir, False, True, 0)
        panel.pack_start(self.buttonCleanAll, False, True, 0)
        self.box.add(panel)
        self.add(self.box)
        try:
            settingsFile = open(self.settingsFileName,"rb")
            self.__persistentStorage__ = pickle.load(settingsFile)
            settingsFile.close()
        except IOError:
            print("Could not load settings file.")

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

    def processEvent(self, wid, panelNumber, cmd):
        if panelNumber and cmd is not None:
            entry = self.__pathpanels__[panelNumber][1]
            print ("--- Entry text reads ["+entry.get_text()+"] ---")
            ########################### debug ################################
            print ("--- Command ["+cmd+"] is dispatched from panel number ["+str(panelNumber)+"] ---")
            ##################################################################
            if cmd == "Relinquish":
                #################### remove panel from gui ###################
                self.box.remove(self.__pathpanels__[panelNumber][0])
                self.__pathpanels__.pop(panelNumber)
                self.resize(800, 1)
                self.box.show_all() # re-pack toplevel
                #################### remove panel from storage ###############
                for i in xrange(0, len(self.__persistentStorage__)):
                    if self.__persistentStorage__[i][0]==panelNumber:
                        self.__persistentStorage__.pop(i)
                        break
                ##############################################################
                return

            if cmd == "Change":
                #################### change path in gui ########################
                pathToDir = None
                currDir = entry.get_text()
                dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                                                Gtk.FileChooserAction.SELECT_FOLDER,
                                                 (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                               "Select", Gtk.ResponseType.OK))
                dialog.set_current_folder(currDir)
                response =  dialog.run()
                if response == Gtk.ResponseType.OK:
                    pathToDir = dialog.get_filename()
                    dialog.destroy()
                elif response == Gtk.ResponseType.CANCEL:
                    dialog.destroy()
                if not pathToDir: # file dialog cancelled or closed by user
                    return
                else:
                    entry.set_text(pathToDir)
                #################### change path in storage ####################
                    for i in xrange(0, len(self.__persistentStorage__)):
                        if self.__persistentStorage__[i][0]==panelNumber:
                            self.__persistentStorage__[i][1]=pathToDir
                            break
            if cmd == "Clean":
                ##### purge root directory of all files and subdirectories #####
                rootDir = entry.get_text()
                self.purgeDirectory(rootDir)
                ################################################################

    def createNewPathPanel(self, panelNumber=None, pathToDir=None, addNewPanel=False):
        if not pathToDir: # create panel from scratch
            dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                                            Gtk.FileChooserAction.SELECT_FOLDER,
                                             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                           "Select", Gtk.ResponseType.OK))
            response =  dialog.run()
            if response == Gtk.ResponseType.OK:
                pathToDir = dialog.get_filename()
                dialog.destroy()
            elif response == Gtk.ResponseType.CANCEL:
                dialog.destroy()
            if not pathToDir: # file dialog cancelled or closed by user
                return
        if not panelNumber: # continue creating panel from scratch
            panelNumber = self.createNewPanelNumber()
        # in this section it does not matter if the panel is created from scratch or not - the same execution code
        label = Gtk.Label("Path to directory: ")
        entry = Gtk.Entry()
        entry.set_hexpand(True)
        entry.set_text(pathToDir)
        buttonRemove = Gtk.Button(label="Relinquish")
        buttonChange = Gtk.Button(label="Change")
        buttonClean = Gtk.Button(label="Clean")
        buttonRemove.connect("clicked", lambda wid, pn=panelNumber, cmd="Relinquish": self.processEvent(wid, pn, cmd))
        buttonChange.connect("clicked", lambda wid, pn=panelNumber, cmd="Change": self.processEvent(wid, pn,cmd))
        buttonClean.connect("clicked", lambda wid, pn=panelNumber, cmd="Clean": self.processEvent(wid, pn, cmd))
        panel = Gtk.Box(spacing=4)
        panel.set_name(str(panelNumber))
        panel.add(label)
        panel.add(entry)
        panel.add(buttonRemove)
        panel.add(buttonChange)
        panel.add(buttonClean)
        self.box.add(panel)
        self.box.reorder_child(panel, 0)
        self.box.show_all()
        self.__pathpanels__[panelNumber] = [panel, entry]
        if addNewPanel:
            self.__persistentStorage__.append([panelNumber,entry.get_text()])

    def purgeAllDirectories(self):
        confirmed = False
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.YES_NO, "Final sanity check")
        dialog.format_secondary_text("Clean all directories by deleting all files in them?")
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            confirmed = True
        elif response == Gtk.ResponseType.NO:
            pass 
        dialog.destroy()
        if not confirmed: return
        self.cleanAllRequested = True
        for i in self.__pathpanels__.keys():
            self.purgeDirectory(self.__pathpanels__[i][1].get_text())
        self.cleanAllRequested = False

    def purgeDirectory(self, rootDir=None):
        if rootDir == None: return
        confirmed = False
        if self.cleanAllRequested == False: # not to bring up dialog for every dir in a batch
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, "Final sanity check")
            dialog.format_secondary_text("Delete all files in this directory?")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                confirmed = True
            elif response == Gtk.ResponseType.NO:
               pass 
            dialog.destroy()
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
    
    def saveAndExit(self, wid, gdkevent):
        self.saveState()
        Gtk.main_quit()

if __name__ == "__main__":
    win = Cleaner()
    win.set_default_size(800, 0)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.connect("delete-event", win.saveAndExit)
    win.show_all()
    Gtk.main()
