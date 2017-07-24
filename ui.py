#!/usr/bin/python

from tkinter import Tk, Label, Button, StringVar, Radiobutton, LabelFrame, Entry, OptionMenu
from tkFileDialog import askopenfilename
import tkMessageBox
import xml.etree.ElementTree as ET
from shutil import copy2
import os
import traceback
import platform

if platform.system() == 'Linux':
    from system import Linux
else:
    from system import Windows

import psutil
from devices.Kobo import Kobo


class GUI:
    FSfile = ''
    radios = []
    drives = {}
    pilots = {
        'N/A': -1
    }

    def __init__(self, master):
        self.master = master

        if platform.system() == 'Linux':
            self.system = Linux.Linux()
        else:
            self.system = Windows.Windows()

        master.title("USB File Extractor")

        self.FSframe = LabelFrame(master, text="FS Comp details")
        self.FSframe.grid(padx=5, pady=5, sticky="N")

        fileInputContent = StringVar()
        fileInputContent.set('')

        fileTitle = Label(self.FSframe, text="FS comp file")
        fileInput = Entry(self.FSframe, textvariable=fileInputContent)
        fileButton = Button(self.FSframe, text="Browse...", command=self.onSelectFSFile)

        fileTitle.grid(row=0, column=0, sticky='E', padx=5, pady=2)
        fileInput.grid(row=0, column=1, columnspan=7, sticky='EW', pady=3)
        fileButton.grid(row=0, column=8, sticky='W', padx=5, pady=2)
        self.fileInputContent = fileInputContent

        pilotTitle = Label(self.FSframe, text="Pilot list:")
        pilotContent = StringVar()
        pilotEntry = Label(self.FSframe, textvariable=pilotContent)

        pilotTitle.grid(row=1, column=0, sticky='E', padx=5, pady=2)
        pilotEntry.grid(row=1, column=1, columnspan=8, sticky='W', pady=3)
        self.pilotContent = pilotContent

        self.selectedDate = StringVar()
        filepathTitle = Label(self.FSframe, text="File write path:")
        filepathContent = StringVar()
        filepathEntry = Label(self.FSframe, textvariable=filepathContent)

        filepathTitle.grid(row=2, column=0, sticky='E', padx=5, pady=2)
        filepathEntry.grid(row=2, column=1, columnspan=8, sticky='W', pady=3)
        self.filepathContent = filepathContent

        dateTitle = Label(self.FSframe, text="Date list:")
        dateContent = StringVar()
        # radios added on load of FS File.

        dateTitle.grid(row=3, column=0, sticky='E', padx=5, pady=2)
        self.dateContent = dateContent

        self.Driveframe = LabelFrame(master, text="Detected Drives")
        self.Driveframe.grid(row=0, column=1, padx=5, pady=5, sticky="N")

        master.after(0, self.checkDeviceList)

        self.Console = LabelFrame(master, text="Console")
        self.Console.grid(padx=5, pady=5, sticky="NWE", columnspan=2)
        self.ConsoleInner = LabelFrame(self.Console, background="black", foreground="green")
        self.ConsoleInner.pack(fill='both')

        self.consoleText = StringVar()
        console = Label(self.ConsoleInner, textvariable=self.consoleText, background='black', foreground="green", height=10, wrap=800, justify='left')
        console.grid(sticky="WE", ipadx=10, ipady=10)

    def checkDeviceList(self):
        for i in self.drives:
            self.drives[i]['partition'] = False
            self.drives[i]['device'] = False

        self.consoleText.set(psutil.disk_partitions())
        for partition in psutil.disk_partitions():
            if partition.fstype == '':
                continue

            mountpoint = partition.mountpoint
            device = partition.device
            if mountpoint not in self.drives:
                self.drives[mountpoint] = {
                    'partition': False,
                    'device': False,
                    '_device': device,
                }
            if not self.drives[mountpoint]['partition']:
                a = Kobo(mountpoint)
                if a.isDevice():
                    self.drives[mountpoint]['device'] = a
                    try:
                        id = a.getPilotId()
                    except:
                        pass

            self.drives[mountpoint]['partition'] = partition

        row = 0
        for mountpoint in self.drives:
            drive = self.drives[mountpoint]
            if 'row' not in drive:
                flightFiles = drive['device'].getFlightFiles() if drive['device'] else ['N/A']
                pilotValue = StringVar()
                pilotValue.set(self.pilots.keys()[0])
                fileValue = StringVar()
                fileValue.set(flightFiles[0])
                drive["row"] = row
                drive["pilotValue"] = pilotValue
                drive["fileValue"] = fileValue
                drive["title"] = Label(self.Driveframe, text=mountpoint)
                drive["button"] = Button(self.Driveframe, text='Import', command=lambda mountpoint=mountpoint: self.doImportFile(mountpoint))
                drive["eject"] = Button(self.Driveframe, text='Eject', command=lambda mountpoint=drive['_device']: self.doEjectDrive(mountpoint))
                drive["pilotList"] = OptionMenu(self.Driveframe, pilotValue, *(self.pilots.keys()), command=lambda value, mountpoint=mountpoint: self.onSelectPilot(mountpoint, value))
                drive["fileList"] = OptionMenu(self.Driveframe, fileValue, *flightFiles, command=lambda value, mountpoint=mountpoint: self.onSelectFile(mountpoint, value))
                drive["title"].grid(row=row, column=0, padx=5, pady=5, sticky="W")

            if drive['device']:
                drive["pilotList"].grid(row=row, column=1, padx=5, pady=5, sticky="WE")
                drive["fileList"].grid(row=row, column=2, padx=5, pady=5, sticky="WE")
                drive["button"].grid(row=row, column=3, padx=5, pady=5, sticky="E")
                drive["eject"].grid(row=row, column=4, padx=5, pady=5, sticky="E")
            else:
                drive["pilotList"].grid_remove()
                drive["fileList"].grid_remove()
                drive["button"].grid_remove()
                drive["eject"].grid_remove()

                pass

            row += 1

        self.master.after(200, self.checkDeviceList)

    def onSelectFSFile(self):
        self.FSfile = askopenfilename()

        for i in self.radios:
            i.grid_remove()

        tree = ET.parse(self.FSfile)
        participants = list(tree.getroot().findall('./FsCompetition/FsParticipants/FsParticipant'))
        dates = list(tree.getroot().iter('FsTask'))

        self.fileInputContent.set(self.FSfile)
        self.pilotContent.set(str(len(participants)) + " pilots found")

        self.pilots = {}

        first = None
        for participant in participants:
            name = participant.attrib['name']
            first = name if first is None else first
            self.pilots[name] = participant.attrib['id']

        if len(self.pilots) == 0:
            self.pilots = {'N/A': -1}

        for d in self.drives:
            drive = self.drives[d]
            flightFiles = drive['device'].getFlightFiles() if drive['device'] else ['N/A']
            drive['pilotValue'].set(first)
            drive['fileValue'].set(flightFiles[0])
            drive['pilotList'].grid_remove()
            drive['fileList'].grid_remove()
            drive['pilotList'] = OptionMenu(self.Driveframe, drive['pilotValue'], *(self.pilots.keys()), command=lambda value, d=d: self.onSelectPilot(d, value))
            drive['fileList'] = OptionMenu(self.Driveframe, drive['fileValue'], *flightFiles, command=lambda value, d=d: self.onSelectFile(d, value))

        row = 3

        for d in dates:
            date = d.find('FsTaskDefinition').find('FsTurnpoint').attrib['open']
            filepath = d.attrib['tracklog_folder']
            self.selectedDate.set(date)
            self.filepathContent.set(filepath)
            b = Radiobutton(self.FSframe, text=date, variable=self.selectedDate, value=filepath, command=self.selectDate)
            b.grid(row=row, column=1, columnspan=8, sticky='W', pady=3)
            self.radios.append(b)
            row += 1

    def selectDate(self):
        self.filepathContent.set(self.selectedDate.get())

    def onSelectFile(self, mountpoint, value):
        print(mountpoint)
        print(value)

    def onSelectPilot(self, mountpoint, value):
        print(mountpoint)
        print(value)

    def doImportFile(self, mountpoint):
        drive = self.drives[mountpoint]
        pilotName = drive["pilotValue"].get()
        pilotID = self.pilots[pilotName]
        file = drive["fileValue"].get()
        dir = os.path.join(os.path.dirname(self.FSfile), str(self.filepathContent.get()))
        dst = dir + '/' + str(pilotName) + '.' + pilotID + '.igc'
        src = drive['device'].getFile(file)
        print "%s -> %s" % (src, dst)
        copy2(src, dst)

    def doEjectDrive(self, mountpoint):
        self.system.unmount(mountpoint)

    def showError(self, *args):
        err = traceback.format_exception(*args)
        tkMessageBox.showerror('Exception',err)


top = Tk()
gui = GUI(top)
top.report_callback_exception = gui.showError
top.mainloop()
