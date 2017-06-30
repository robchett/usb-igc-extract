# usb-igc-extract
Tool to automatically extract igc files from USB mass storage devices

The tool will check for any new USB drives attatched to the computer. If the drive matches the file system of a know GPS device then the following will happen:

1a) Checks the pilot ID. The source of this can be changed so that seperate competions don't overlap.

1b) Writes a pilot ID if none is found

2a) Checks for flights from the given date

2b) Prompts for the selection of a specific file if multiple match or none.

3a) Ejects the device.

# Usage

## Binary 
Get the latest release from the [releases page](https://github.com/robchett/usb-igc-extract/releases) and run the self extrator.

## Command line
Install python on your system.
run `python setup.py install` from the source directoy
run `kobo.py`

# Command line options
`kobo.py [output directory] [comp name] [date*]`
* Date is not yet implemented


