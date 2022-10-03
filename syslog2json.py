#!/usr/bin/env python3
__version__ = "0.1.13"
#
## Importing modules
#
import sys
import platform
import os
import re
from datetime import datetime
import time
import argparse
import textwrap
import shutil
import tempfile
import signal

try:
    from importlib import metadata
except ImportError:
    # for Python < 3.8
    import importlib_metadata as metadata
import json

try:
    import jsonschema
    from jsonschema import validate
except ImportError:
    print("Module Import Error! Module `jsonshema` not found.")
    jsonVerifyInit = False
    print("Output JSON validation disabled!")
    print()
else:
    ## DeprecationWarning: Accessing jsonschema.__version__ is deprecated
    ## and will be removed in a future release. Use importlib.metadata
    ## directly to query for jsonschema's version.
    #
    # print(jsonschema.__version__)
    # List declaration to store module version [major.minor.micro]
    moduleVersion = []
    for part in metadata.version("jsonschema").split("."):
        moduleVersion.append(int(part))
    if moduleVersion[0] >= 3:
        if moduleVersion[1] >= 2:
            jsonVerifyInit = True
    else:
        jsonVerifyInit = False
        print("Output JSON validation disabled! Installed outdated version of")
        print("the `jsonschema` module. Minimum recommended version is 3.2+.")
        print()

try:
    import progress as pb
    import colors as rgb256
except ImportError as importErrors:
    print(importErrors)
    exit(1)

from log import logger

from handlers import rowCheck
from handlers import buildJSON
from handlers import schemaImport
from handlers import stringToRaw
from handlers import printTimeout

minVersion = "3.9"
# assert sys.version_info >= (3,6), f'Incorrect Python version!'
if sys.version_info.major > 2:
    if sys.version_info.major == 3 and sys.version_info.minor < 9:
        print("Python version can be upgraded to version {}+".format(minVersion))
        print("Now installed: {}".format(sys.version))
        exit(1)
else:
    print("Python version 2.x is not supported!")
    print("Python {}+ must be installed!".format(minVersion))
    exit(1)


def signalHandler(signum, frame):
    """Interruption signal handler"""
    print("Interrupted by user!")
    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")
    print("Signal handler called with signal", signum)
    print()
    print("{}".format(customText.format_string(1, 255, None, "Clean up...")))
    print()
    logger.warning("Process interrupted by user! Signal number: {}".format(signum))
    logger.format("base")
    logger.info("--- End of log file ---")
    logger.shutdown()
    # Closing temporary and output files
    LOG_INPUT.close()
    LOG_OUTPUT.close()
    # Remove output file if exist
    if os.path.isfile(outputFile):
        os.remove(outputFile)
    # Final message
    print("******************************************************************")
    print("Script execution was interrupted by the user. Detailed information")
    print("is saved in the log file: {}".format(scriptLogFile))
    print()
    print("End time: {}".format(datetime.now().strftime("%Y-%m-%d@%I:%M:%S%p%z")))
    print("******************************************************************")
    print()
    exit(signum)


def main(
    logInput: "Input syslog file object",
    logRows: int,
    jsonVerify: bool = True,
    showProgress: bool = True,
):
    """
    Syslog file processing

    .ARGUMENTS:

        logInput        - input syslog file to export to JSON (object)
        logRows         - number of rows in the input file (int)
        jsonVerify      - JSON file verification flag (bool)
        showProgress    - display progress bar (bool)

    """
    # Jump to the beginning of the temporary input file
    logInput.seek(0)
    logRowsLenght = len(str(logRows))

    # Main Arrays
    logRecords = {"syslog": []}
    logErrors = []

    ## Disabled. Start index for `while` loop # idx = 1
    ## Disabled. `while` loop # while (line := logInput.readline()):

    for idx, line in enumerate(logInput, start=1):
        """
        print(len(line))
        if line:
            print("Row {}: {}".format(idx, line.strip()))
        else:
            print("Row {}: ".format(idx), "Error: The row {} is Empty!".format(idx))
        """
        logger.info("Row {:{}d} of {}".format(idx, logRowsLenght, logRows))
        if not line.isspace():
            # Remove line end characters and unescaping HTML special characters and
            # convert message to raw string and replace `\` to `\\`
            # Ref: https://python-tutorials.in/python-raw-strings/
            # Ref: https://realguess.net/2016/07/29/escaping-in-json-with-backslash/
            rawMessage = stringToRaw(line.strip())
            # Disabled # print('Row {}: {}'.format(idx, line.strip()), end = '\n')
            # Rewriting double quotes {"} to single quotes {'} to create correct JSON
            # file structure
            logMessage = rawMessage.replace('"', "'")
            # Checking the structure of the entry in the log file
            verificationResult = rowCheck(logMessage)
            if verificationResult[0] == 0:
                # Structure check completed successfully
                currentElement = buildJSON(idx, logRows, logMessage)
                if jsonVerify:
                    try:
                        validate(instance=currentElement, schema=mainSchema)
                        logger.info(f"JSON data in line {idx} is verified")
                    except jsonschema.exceptions.ValidationError as validationError:
                        logger.error(f"Data on line {idx} contains an error!")
                        logger.error("Error details:\n{}".format(validationError))
                        logErrors.append(idx)
                        logger.warning(
                            "Row {:{}d} processed with error!".format(
                                idx, logRowsLenght
                            )
                        )
                    else:
                        logger.info(
                            "Row {:{}d} processed successfully".format(
                                idx, logRowsLenght
                            )
                        )
                else:
                    logger.info(
                        "Row {:{}d} processing completed".format(idx, logRowsLenght)
                    )

                logRecords["syslog"].append(currentElement)
            else:
                # If the log entry contains an error
                logger.info(
                    "Log entry does not have the correct structure! Row# {}.".format(
                        idx
                    )
                )
                logger.error(
                    "Record structure error: `{}`".format(verificationResult[2])
                )
                logger.error("Error number: {}".format(verificationResult[1]))
                logger.info("Skip processing line {}".format(idx))
        else:
            logger.info("Row {:{}d} processed with an error".format(idx, logRowsLenght))
            logger.error("Empty `null` line in input file! Line number: {}".format(idx))

        ## Disabled. Index for `while` loop # idx += 1

        # Current percent
        completedPercentage = round((idx * 100) / logRows)
        if showProgress is True:
            progressBar.progress(completedPercentage)
            time.sleep(sleepTime)
            if idx == logRows:
                progressBar.stop
        else:
            msgString = f"Row {idx:{logRowsLenght}d} of {logRows}"
            print("\r", end="")
            print(msgString, end="")
            time.sleep(sleepTime)
            if idx == logRows:
                time.sleep(0.3)
                print("\r", end="")
                print(" " * screenCols, end="")

    return logRecords, logErrors


## Process the input options with `argparse`
#
parser = argparse.ArgumentParser(
    add_help=False,
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="",
    description=textwrap.dedent("""Syslog2JSON. Syslog file export to JSON format."""),
)
parser.add_argument(
    "-i",
    "--inlog",
    action="store",
    required=False,
    nargs="+",
    default="/var/log/syslog",
    dest="fileSource",
    metavar="LOGFILE",
    type=str,
    help=textwrap.dedent(
        """\
        path to input syslog file(s). If not specified, the default location
        `%(default)s` is used

        """
    ),
)
parser.add_argument(
    "-o",
    "--outjson",
    action="store",
    required=False,
    default="syslog.json",
    dest="outputFile",
    metavar="OUTJSON",
    type=str,
    help=textwrap.dedent(
        """\
        output JSON filename. If no JSON filename is specified, the default
        filename `%(default)s` will be used

        """
    ),
)
parser.add_argument(
    "-d",
    "--workdir",
    action="store",
    required=False,
    nargs="?",
    default="/tmp",
    const="/tmp",  # nargs must be '?'
    dest="outputDir",
    metavar="OUTPUT DIR",
    type=str,
    help=textwrap.dedent(
        """\
        path to the output directory in which the JSON out syslog file will
        be created and the log files of the script will be placed. Default
        `%(default)s`. If the path is not specified, the output JSON file and script
        logs will be created in the default directory.

        """
    ),
)
parser.add_argument(
    "-n",
    "--no-progress",
    action="store_const",
    required=False,
    default=True,
    const=False,
    dest="showProgress",
    metavar="",
    help=textwrap.dedent(
        """\
        disable progress indicator

        """
    ),
)
parser.add_argument(
    "-f",
    "--format-json",
    action="store_const",
    required=False,
    default=False,
    const=True,
    dest="jsonFormat",
    metavar="",
    help=textwrap.dedent(
        """\
        creating a pretty-printed output JSON file. By default the file is
        created in the minified/raw version.

        """
    ),
)
parser.add_argument(
    "-s",
    "--schema",
    action="store",
    required=False,
    default="validation.json",
    dest="schemaFile",
    metavar="JSONSCHEMA",
    type=str,
    help=textwrap.dedent(
        """\
        full path to JSON schema file. If no schema file is specified, the
        default schema `%(default)s` file in current directory will be used.

        """
    ),
)
parser.add_argument(
    "-c",
    "--no-verify",
    action="store_const",
    required=False,
    default=True,
    const=False,
    dest="jsonVerify",
    metavar="",
    help=textwrap.dedent(
        """\
        do not verify output JSON file

        """
    ),
)
parser.add_argument(
    "-h",
    "--help",
    action="help",
    help=textwrap.dedent(
        """\
        show this help message and exit

        """
    ),
)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="%(prog)s {}".format(__version__),
    help=textwrap.dedent(
        """\
        show the current script version

        """
    ),
)

args = parser.parse_args()

## Colors definition
#
customText = rgb256.FormatString()
customStr = rgb256.FormatText()

## Input parameters verification
#
# print(args)
print("Checking the basic required parameters...")
print()

"""Output directory"""
print("{:30s}".format("Output directory"), end="")
# OUTPUT_DIR = os.path.abspath(os.getcwd())
if args.outputDir:
    regexSearch = "((^.*)(\/$))"
    regexDir = re.search(regexSearch, args.outputDir.strip())
    if regexDir:
        OUTPUT_DIT = regexDir.group(2)
    else:
        OUTPUT_DIR = args.outputDir.strip()
print("OK")

## Capturing interrupt signals
#
# INT(2)
# TERM(15)
# TSTP(20)
#
# `Ctrl + C` and `Ctrl + Z` keyboard breaks
#
print("{:30s}".format("Interruption signals"), end="")
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGTSTP, signalHandler)
"""Events that will need to be added for Windows
platform:
signal.CTRL_C_EVENT
signal.CTRL_BREAK_EVENT
"""
print("OK")
print()
time.sleep(1)


## Print System Information
#
# Registered names: ‘posix’, ‘nt’, ‘os2’, ‘ce’, ‘java’ and ‘riscos’.
# 'posix'   linux/bsd/macos
# 'cls'     windows
os.system("cls" if os.name == "nt" else "clear")
print(
    "{}".format(customText.format_string(1, 255, None, "Collected System Information"))
)
# Ref: https://docs.python.org/3/library/platform.html
print()
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    osRelease = platform.freedesktop_os_release()
    print("{} {}".format(osRelease["NAME"], osRelease["VERSION"]), end="\n")

print(
    platform.system(),
    platform.release(),
    platform.version(),
    platform.processor(),
    end="\n",
)
print(
    "Python v{} {} [{}] on {}".format(
        platform.python_version(),
        platform.python_build(),
        platform.python_compiler(),
        platform.system().lower(),
    ),
    end="\n",
)
print()


## Input parameters verification
#
charPass = "√"
charFail = "×"
charCancel = "ø"
charErr = "›"

hideCursor = "\x1b[?25l"
showCursor = "\x1b[?25h"

sleepTime = 5 / 1000
#
print("{}".format(customText.format_string(1, 255, None, "Parameters verification")))
print()

"""Input syslog file(s)"""
print("[   ] {}".format("Input log file(s) to export..."), end="")
fileList = args.fileSource
print("\r", end="")
printTimeout(0.3)
print(
    "[ {}{}{} ] {}".format(
        customStr.fg(34), charPass, customStr.reset, "Input log file(s) to export: "
    ),
    end="",
)
for fileInList in fileList:
    print("{} ".format(repr(fileInList)), end="")
print()

## Disabled. Tempfile is used.
#
# tmpFile = 'inLogFile.log'
# inputFile = OUTPUT_DIR + '/' + tmpFile

print("[   ] {}".format("Output directory..."), end="")
print("\r", end="")
if os.path.exists(OUTPUT_DIR):
    printTimeout(0.3)
    print(
        "[ {}{}{} ] {} {}".format(
            customStr.fg(34),
            charPass,
            customStr.reset,
            "Output directory:",
            repr(OUTPUT_DIR),
        ),
        end="",
    )
    print()
    print("[   ] {}".format("Output directory read/write permition..."), end="")
    print("\r", end="")
    if os.access(OUTPUT_DIR, os.W_OK):
        printTimeout(0.3)
        print(
            "[ {}{}{} ] {}".format(
                customStr.fg(34),
                charPass,
                customStr.reset,
                "Output directory is writable by the user",
            ),
            end="",
        )
        print()
        ## Disabled. Tempfile is used. Tempfile is deleted automatically after use.
        #
        # if os.path.isfile(inputFile):
        #     os.remove(inputFile)
        #     print(f'Existing OLD input log file {destinationFile} has been deleted')
        #
        print("[   ] {}".format("Creating a tempfile for data import..."), end="")
        print("\r", end="")
        try:
            ## Disabled. Tempfile is used.
            #
            # LOG_INPUT = open(inputFile, "a+")
            #
            printTimeout(0.3)
            LOG_INPUT = tempfile.NamedTemporaryFile(mode="w+", dir=OUTPUT_DIR)
            print(
                "[ {}{}{} ] {}".format(
                    customStr.fg(34),
                    charPass,
                    customStr.reset,
                    "Temporary file for data import created",
                ),
                end="",
            )
            print()
        except (OSError, IOError, PermissionError) as fileCreateError:
            print(
                "[ {}{}{} ] Exception! Unable to create temporary input file!".format(
                    customStr.fg(9), charFail, customStr.reset
                ),
                end="",
            )
            print("\n")
            sys.exit(fileCreateError)
    else:
        print(
            '[ {}{}{} ] The user does not have write permission to "{}" directory!'.format(
                customStr.fg(9), charFail, customStr.reset, OUTPUT_DIR
            ),
            end="",
        )
        print("\n")
        exit(1)
else:
    printTimeout(0.75)
    print(
        "[ {}{}{} ] Output directory {} does not exist!".format(
            customStr.fg(9), charFail, customStr.reset, OUTPUT_DIR
        ),
        end="",
    )
    print("\n")
    exit(1)

# Import data to temporary file from input log files
print()
print("{}".format("Importing data into a temporary file:"))
print()

for index, file in enumerate(fileList):
    fileName = file.strip()
    print("[   ] Import data from file: {}".format(repr(fileName)), end="")
    print("\r", end="")
    if os.path.isfile(fileName):
        printTimeout(0.3)
        with open(fileName, "rt") as fileInput:
            LOG_INPUT.write(fileInput.read())
            print(
                "[ {}{}{} ] Data import from file {} completed".format(
                    customStr.fg(34), charPass, customStr.reset, repr(fileName)
                ),
                end="",
            )
            print()
    else:
        printTimeout(0.3)
        print(
            "[ {}{}{} ] Skip! Source file {} not found!".format(
                customStr.fg(124), charCancel, customStr.reset, fileName
            ),
            end="",
        )
        print()


## Logging configuration
#
"""
# The full path to the log file must be added
"""
print()
print("[   ] {:35s}".format("Script logging configuration..."), end="")
print("\r", end="")

printTimeout(0.5)

"""Start logging"""
logger.loggerName = sys.argv[0]
logger.logFileName = OUTPUT_DIR + "/syslogexport.log"
logger.set_filelogger()
logger.set_level()

logger.set_format("base")
logger.info("--- Start of log file ---")
logger.set_format("main")

print(
    "[ {}{}{} ] {:35s}".format(
        customStr.fg(34), charPass, customStr.reset, "Script logging is configured"
    )
)
print()


## Main values
#
"""Output JSON file"""
outputFile = OUTPUT_DIR + "/" + args.outputFile
LOG_OUTPUT = open(outputFile, "w")

"""Optional parameters"""
switchColorID = {True: 106, False: 215}

# Pretty-printed output JSON file
JSON_FORMAT = args.jsonFormat
print()
print(
    "{:35s} {}".format(
        "Pretty-printed output JSON file:",
        customText.format_string(
            1, switchColorID.get(JSON_FORMAT), None, str(JSON_FORMAT)
        ),
    )
)

# Output JSON file verification
if jsonVerifyInit:
    if args.jsonVerify:
        # Importing verification JSON schema
        importResult, mainSchema = schemaImport(args.schemaFile)
        if importResult:
            # Default value is used
            JSON_VERIFY = args.jsonVerify
            logger.info("Output JSON validation enabled")
        else:
            logger.warning("Output JSON file verification disabled.")
            JSON_VERIFY = False
    else:
        # When validation is disabled by the user (option `-c`)
        JSON_VERIFY = False
        mainSchema = None
        logger.info("Output JSON validation disabled by the user")
else:
    JSON_VERIFY = False
    mainSchema = None
    logger.info("Output JSON validation disabled. `jsonschema` module error!")

print(
    "{:35s} {}".format(
        "Output JSON file verification:",
        customText.format_string(
            1, switchColorID.get(JSON_VERIFY), None, str(JSON_VERIFY)
        ),
    )
)

# Show progress bar
SHOW_PROGRESS = args.showProgress
print(
    "{:35s} {}".format(
        "Progress bar:",
        customText.format_string(
            1, switchColorID.get(SHOW_PROGRESS), None, str(SHOW_PROGRESS)
        ),
    )
)
print()


print(
    "{} All initial parameters are set.".format(
        customText.format_string(1, 255, None, "Completed!")
    )
)
print("\n")


## Syslog file processing
#
print("{}".format(customText.format_string(1, 255, None, "Syslog file processing")))
print()
# Jump to the beginning of the temporary input file
LOG_INPUT.seek(0)
LOG_ROWS = len(LOG_INPUT.readlines())
print(
    "{} rows in the log file for processing".format(
        customText.format_string(1, 27, None, str(LOG_ROWS))
    ),
    end="\n",
)

logger.info("Start input syslog file(s) processing...")
logger.info("/*")
startTime = datetime.now()
print(
    "Log file processing started at: {}".format(
        startTime.strftime("%Y-%m-%d@%I:%M:%S%p%z")
    ),
    end="\n\n",
)
beginProcessing = time.time()
print(hideCursor, end="")

if LOG_ROWS > 0:
    ## Progress bar definition
    #

    # Get the size of the terminal
    size = os.get_terminal_size()
    screenCols = size.columns
    screenRows = size.lines

    if SHOW_PROGRESS is True:
        progressBar = pb.SimpleProgress(screenCols, screenRows)
        progressBar.leftSideFG = customStr.style(1)
        # progressBar.leftSideBG = ''
        progressBar.progressColor = f"{customStr.style(1)}{customStr.fg(33)}"  # (1,33)
        progressBar.resetColor = customStr.reset

        progressBar.start

    ## Processing log input
    #
    jsonRecords, logRowsError = main(LOG_INPUT, LOG_ROWS, JSON_VERIFY, SHOW_PROGRESS)
    if SHOW_PROGRESS is True:
        time.sleep(0.3)
        progressBar.clear
    logRowsProcessed = len(jsonRecords["syslog"])

    ## Output data verification result
    #
    if JSON_VERIFY:
        print("[   ] {}".format("JSON values verification..."), end="")
        time.sleep(0.5)

        if len(logRowsError) > 0:
            print("\r", end="")
            print(
                "[ {}{}{} ] JSON values verification error!".format(
                    customStr.fg(9), charFail, customStr.reset
                ),
                end="",
            )
            print("\n")

            print(
                "Detailed error information is saved in the log file `{}`".format(
                    scriptLogFile
                )
            )
            print("Error on line(s):", end="")
            for logRow in logRowsError:
                print(
                    " {}{}{}".format(customStr.fg(255), str(logRow), customStr.reset),
                    end="",
                )
            print("\n")
        else:
            print("\r", end="")
            print(
                "[ {}{}{} ] JSON values verification completed".format(
                    customStr.fg(34), charPass, customStr.reset
                ),
                end="",
            )
            print("\n")

    ## Write output JSON file
    #
    if JSON_FORMAT:
        dump_args = {"indent": 2}
    else:
        dump_args = {}

    json.dump(jsonRecords, LOG_OUTPUT, **dump_args)
else:
    logRowsProcessed = 0
    print(
        "{} {}".format(
            customText.format_string(1, 88, None, "Nothing to process!"),
            "Input file is empty/zero size.",
        )
    )
    print()

print(showCursor, end="")

endTime = datetime.now()
endProcessing = time.time()
logger.info("*/")
logger.info("End input syslog file(s) processing")
execTime = (endProcessing - beginProcessing) * 1000


""" ## Results Test Area

print(type(jsonRecords))
print(type(logRowsError))

## EOF: Test Area """


print()
print(
    "Log file processing finished at: {}".format(
        endTime.strftime("%Y-%m-%d@%I:%M:%S%p%z")
    ),
    end="\n",
)
print(
    "{}".format(customText.format_string(1, 255, None, "Syslog file import completed!"))
)

# Stop logging
logger.set_format("base")
logger.info("--- End of log file ---")
logger.shutdown

print("\n")
print("****************************************************************", end="\n")
print(
    f" Output JSON file saved in {repr(OUTPUT_DIR)} directory with the name:", end="\n"
)
print(f" {repr(LOG_OUTPUT.name)}", end="\n")
print()
# print(' File processing time: {}ms'.format(str(round(execTime, 4))), end = '\n')
print(" File processing time: {}s".format(str(round(execTime / 1000))), end="\n")
print(f" Records processed: {logRowsProcessed}", end="\n")
logRowsSkipped = LOG_ROWS - logRowsProcessed
print(f" Entries skipped: {logRowsSkipped}", end="\n")
if LOG_ROWS != 0:
    print(
        " Average record processing time: {}ms".format(
            str(round(execTime / LOG_ROWS, 4))
        )
    )
print("****************************************************************", end="\n")
print()

# Close the temporary input file (it will be removed)
LOG_INPUT.close()
# Close output file
LOG_OUTPUT.close()


exit(0)
