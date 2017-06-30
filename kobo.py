# building on above and http://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python
import string
from ctypes import windll
import time
import os
import re
import sys
from shutil import copy2
import logging
import colourer

import win32api, win32gui, win32con, win32file, struct

def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in range(ord('A'), ord('Z')):
        if bitmask & 1:
            drives.append(chr(letter))
        bitmask >>= 1
    return drives

def detect_pilot_id(drive, filename):
    try:
        file = open(drive + ':/XCSoarData/' + filename + '.txt', 'r')
        id = file.read() 
        file.close()
        return id
    except Exception as e:
        logging.warn( "Failed to get pilot ID. " + str(e))
        return False


def set_pilot_id(drive, filename, id):
    try:
        file = open(drive + ':/XCSoarData/' + filename + '.txt', 'w')
        file.write(id) 
        file.close()
    except Exception as e:
        logging.warn( "Failed to set pilot ID. " + str(e))
        return False

def eject_drive(drive):
    FSCTL_LOCK_VOLUME = 0x0090018
    FSCTL_DISMOUNT_VOLUME = 0x00090020
    IOCTL_STORAGE_MEDIA_REMOVAL = 0x002D4804
    IOCTL_STORAGE_EJECT_MEDIA = 0x002D4808


    lpFileName = r"\\.\%s:" % drive
    
    dwDesiredAccess = win32con.GENERIC_READ|win32con.GENERIC_WRITE
    dwShareMode = win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE
    dwCreationDisposition = win32con.OPEN_EXISTING

    try:
        logging.info("Ejecting %s." % drive)
        hVolume = win32file.CreateFile(lpFileName, dwDesiredAccess, dwShareMode, None, dwCreationDisposition, 0, None)

##        cnt = 0
##        maxcnt = 5
##        while(cnt < maxcnt):
##            try:
##                win32file.DeviceIoControl(hVolume, FSCTL_LOCK_VOLUME, None, 0, None)
##                print("Lock obtained" % drive)
##                break;
##            except:
##                logging.warn("Lock failed, retrying %s/%s" % (cnt,maxcnt))
##                time.sleep(1)
##                cnt += 1               
    
        win32file.DeviceIoControl(hVolume, FSCTL_DISMOUNT_VOLUME, None, 0, None)
        win32file.DeviceIoControl(hVolume, IOCTL_STORAGE_MEDIA_REMOVAL, struct.pack("B", 0), 0, None)
        win32file.DeviceIoControl(hVolume, IOCTL_STORAGE_EJECT_MEDIA, None, 0, None)
    except:
        raise
    finally:
        win32file.CloseHandle(hVolume)    

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    comp = 'pilot_id'
    if (len(sys.argv) >= 3):
        comp = ".".join(filter(None, ['pilot_id', sys.argv[2]]))
    logging.info("Pilot ID file is %s" % comp)

    out_default = "Z:/nats 2017/Desktop/NATS 2017/Tracks/task 2"
    if (len(sys.argv) >= 2 and os.path.isdir(sys.argv[1])):
        directory = sys.argv[1]
    else:
        directory = ""
        while (directory == ""):
            directory = input("Please enter the output directory. ")
            if (directory != "" and not os.path.isdir(directory)):
                logging.warn("Directory %s does not exist." % directory)
                directory = ""
    logging.info("Output directory is %s" % directory)
    
    before = set(get_drives())
    while (time.sleep(1) or True): 
        after = set(get_drives())
        drives = after - before
        delta = len(drives)
        before = after
        if (delta):
            for drive in drives:
                if os.system("cd " + drive + ":") == 0:
                    newly_mounted = drive
                    logging.info( "There were %d drives added: %s. Newly mounted drive letter is %s" % (delta, drives, newly_mounted))
                    if (not os.path.isdir(drive + ":/XCSoarData/")):
                        logging.warn("No XCSoarData directory detected")
                        continue
                    pilot_id = detect_pilot_id(drive, comp)
                    if (not pilot_id):
                         pilot_id = input("Please enter the pilots ID: ")
                         set_pilot_id(drive, comp, pilot_id)

                    kobo_path = drive + ":/XCSoarData/logs/"
                    files = os.listdir(kobo_path)
                    date = time.strftime("%Y-%m-%d")
                    cFiles = [file for file in files if re.search("%s.*\.igc" % date, file)]
                    files_c = len(cFiles)
                    index = 0
                    if (files_c == 0):
                        logging.warn("No files matching todays date. Please select manually.")
                        print("0) Continue manually")
                        print("1) Eject device")
                        cnt = 2
                        for file in files:
                            print("%s) %s - %s" % (cnt, file, os.path.getsize(kobo_path + file)))
                            cnt = cnt + 1
                        index = int(input("Select a file "))
                        if (index == 1):
                            eject_drive(drive)
                            continue
                        if (index == 0):                            
                            continue
                        index -= 2
                    else:
                        files = cFiles
                        if (files_c > 1):
                            logging.warn("Multiple (%s) files matching todays date: " % files_c)
                            print("0) Continue manually")
                            print("1) Eject device")
                            cnt = 2
                            for file in files:
                                print("%s) %s - %s" % (cnt, file, os.path.getsize(kobo_path + file)))
                                cnt = cnt + 1
                            index = int(input("Select a file (largest is most likely: "))
                            if (index == 1):
                                eject_drive(drive)
                                continue
                            if (index == 0):
                                continue
                            index -= 2
                    logging.info("Copied %s to %s.igc" % (files[index], pilot_id))
                    copy2(kobo_path + files[index], directory + pilot_id + ".igc")
                    eject_drive(drive)
