import os


class Kobo:
    dir = '/XCSoarData/'

    def __init__(self, mountpoint):
        self.mountpoint = mountpoint
        pass

    def isDevice(self):
        return os.path.isdir(self.mountpoint + self.dir)

    def getPilotId(self, filename):
        try:
            file = open(self.dir + filename + '.txt', 'r')
            id = file.read()
            file.close()
            return id
        except Exception as e:
            logging.warn("Failed to get pilot ID. " + str(e))
            return False

    def setPilotId(self, filename, id):
        try:
            file = open(self.mountpoint + filename + '.txt', 'w')
            file.write(id)
            file.close()
        except Exception as e:
            logging.warn("Failed to set pilot ID. " + str(e))
            return False

    def getFlightFiles(self):
        kobo_path = self.mountpoint + self.dir + "logs/"
        return os.listdir(kobo_path)

    def getFile(self, file):
        return  self.mountpoint + self.dir + "logs/" + file