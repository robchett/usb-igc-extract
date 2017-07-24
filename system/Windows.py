import win32file
import win32con
import struct

class Windows:

    def __init__(self):
        pass

    def unmount(self, drive):
        FSCTL_LOCK_VOLUME = 0x0090018
        FSCTL_DISMOUNT_VOLUME = 0x00090020
        IOCTL_STORAGE_MEDIA_REMOVAL = 0x002D4804
        IOCTL_STORAGE_EJECT_MEDIA = 0x002D4808

        drive = drive.replace('\\', '')
        lpFileName = '\\\\.\\%s' % drive
        print lpFileName

        dwDesiredAccess = win32con.GENERIC_READ | win32con.GENERIC_WRITE
        dwShareMode = win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE
        dwCreationDisposition = win32con.OPEN_EXISTING

        hVolume = win32file.CreateFile(lpFileName, dwDesiredAccess, dwShareMode, None, dwCreationDisposition, 0, None)
        win32file.DeviceIoControl(hVolume, FSCTL_LOCK_VOLUME, None, 0, None)
        win32file.DeviceIoControl(hVolume, FSCTL_DISMOUNT_VOLUME, None, 0, None)
        win32file.DeviceIoControl(hVolume, IOCTL_STORAGE_MEDIA_REMOVAL, struct.pack("B", 0), 0, None)
        win32file.DeviceIoControl(hVolume, IOCTL_STORAGE_EJECT_MEDIA, None, 0, None)
        win32file.CloseHandle(hVolume)
