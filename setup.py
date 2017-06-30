from cx_Freeze import setup, Executable

base = None


executables = [Executable("kobo.py", base=base)]

packages = [
    "win32api",
    "win32file",
    "win32con",
    "win32gui",
    "string",
    #"ctypes",
    "encodings",
    "time",
    "os",
    "re",
    "sys",
    "shutil",
    "logging",
    "struct",

]
options = {
    'build_exe': {
        'packages':packages,
    },

}

setup(
    name = "kobo",
    options = options,
    version = "0.1",
    description = 'Extracts igc files from Kobos using XCSoar',
    executables = executables
)
