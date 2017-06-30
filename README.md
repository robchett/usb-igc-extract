# usb-igc-extract
Tool to automatically extract igc files from USB mass storage devices

The tool will check for any new USB drives attatched to the computer. If the drive matches the file system of a know GPS device then the following will happen:

0a) Prompts for the competion identifier so we can write unique pilot_id files (optional)

0b) Prompts for the ouptup directory for the tasks IGC files.

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

# Supported Devices

Currently we only support Kobos, for the addition of new devices will need to be provided with the folling:

1) The location of the IGC log files.
2) The format of the IGC filenames (so we can work out wish is the relevant one for a task).
3) A writable directory if one exists for the storage of Comp IDs.

If you can provide these details, please [create an Issue](https://github.com/robchett/usb-igc-extract/issues/new) and I'll update as soon as possible.

# Todos

1) Add more devices.
2) Add support for selecting a date - in case scoring is not on the day of the task.
3) Add a user interface.
