import dbus


class Linux:

    def __init__(self):
        pass

    def unmount(self, mountpoint):
        bus = dbus.SystemBus()

        manager_obj = bus.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks')
        manager = dbus.Interface(manager_obj, 'org.freedesktop.UDisks')
        print mountpoint
        path = manager.FindDeviceByDeviceFile(mountpoint)
        proxy = bus.get_object('org.freedesktop.UDisks', path)
        drive_if = dbus.Interface(proxy, 'org.freedesktop.UDisks.Device')
        drive_if.FilesystemUnmount('')

        device_props = dbus.Interface(proxy, dbus.PROPERTIES_IFACE)
        drive = device_props.Get('org.freedesktop.UDisks.Device', "PartitionSlave")
        drive_obj = bus.get_object("org.freedesktop.UDisks", drive)
        drive_if = dbus.Interface(drive_obj, 'org.freedesktop.UDisks.Device')
        drive_if.DriveEject([])