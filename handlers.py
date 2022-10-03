"""
`syslog2json` handlers

rowCheck     - syslog row format verification
buildJSON    - syslog record parser
schemaImport - JSON schema import
stringToRaw  - log row conversion to raw string format
"""
import os
import sys
from datetime import datetime
import time
import json
import re

from log import logger

__all__ = ["rowCheck", "buildJSON", "schemaImport", "stringToRaw", "printTimeout"]


def rowCheck(rowString: str = ""):
    """Syslog row format verification"""
    if rowString != "":
        rowMonth = rowString[0:3]
        rowDay = int((rowString[3:6]).strip())
        rowTime = rowString[7:15]
        rowHostname = rowString[16:].split(" ", 1)[0].strip()
    else:
        return False

    """ Log record timestamp format 'Mmm dd hh:mm:ss' verification
    """
    checkResults = []
    checkErrors = []
    """ Month format check
     /*
        'Mmm' is the English language abbreviation for the month of the
        year with the first character in uppercase and the other two
        characters in lowercase.
     */
    """
    lstMonths = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    if rowMonth in lstMonths:
        checkResults.append(0)
    else:
        checkResults.append(1)
        checkErrors.append("Month value error!")

    """ Day of the Month format check
     /*
        'dd' is the day of the month.  If the day of the month is less
        than 10, then it MUST be represented as a space and then the number.
     */
    """
    if rowDay in range(1, 32, 1):
        checkResults.append(0)
    else:
        checkResults.append(1)
        checkErrors.append("Invalid day of the month!")

    """ Time format check
     /*
        'hh:mm:ss' is the local time. The hour (hh) is represented in a
        24-hour format.
     */
    """
    timeFormat = "%H:%M:%S"  # 24 hours format
    # timeFormat = "%I:%M:%S %p" #12 hours format
    try:
        timeCheck = bool(datetime.strptime(rowTime, timeFormat))
        checkResults.append(0)
    except ValueError as timeCheckError:
        timeCheck = False
        checkResults.append(1)
        checkErrors.append("Wrong time format!")

    """ Hostname check
     /*
        The maximum length of the host name and of the fully qualified domain
        name (FQDN) is 63 bytes per label and 255 bytes per FQDN.
        RFC1035 2.3.1. Preferred name syntax
        https://www.rfc-editor.org/rfc/rfc1035
        RFC1123 2.1  Host Names and Numbers
        https://datatracker.ietf.org/doc/html/rfc1123
     */
    """
    rowHostnameLenght = len(rowHostname)
    if rowHostnameLenght > 0 and rowHostname != "":
        checkResults.append(0)
        # Hostname lenght
        if rowHostnameLenght < 63:
            checkResults.append(0)
            ## Disabled. Replased to str.isalnum()
            #  hostnameCheck = all(namePart.isalpha() or namePart.isdecimal() or namePart == '-'
            #      for namePart in rowHostname)
            hostnameCheck = all(
                namePart.isalnum() or namePart == "-" for namePart in rowHostname
            )
            # All characters in the string are alphanumeric or hyphen `-`
            if hostnameCheck:
                checkResults.append(0)
                char1st = rowHostname[0:1].strip()
                char1stCheck = char1st.isalpha()
                # First character in `hostname` are in the alphabet
                if char1stCheck:
                    checkResults.append(0)
                else:
                    checkResults.append(1)
                    checkErrors.append(
                        "1st character in the hostname must be a alphabet letter (a-zA-Z)!"
                    )
            else:
                checkResults.append(1)
                checkErrors.append("Hostname contains an invalid character(s)!")
        else:
            checkResults.append(1)
            checkErrors.append("Incorrect hostname lenght `> 63 chars`!")
    else:
        checkResults.append(1)
        checkErrors.append("Incorrect hostname value!")

    # Final check list
    checksQty = len(checkResults)
    finalCheck = 0
    for check in checkResults:
        finalCheck = finalCheck + check

    return (finalCheck, checksQty, checkErrors)


def buildJSON(currentRow: str, totalRows: int, logRow: int) -> dict:
    """Syslog record parser"""
    regexPattern = "((^.*)(\[([0-9]{1,})\]))(\:)$"
    # Disabled for correct processing the days of the month from the
    # 1st to the 9th with leading space, like ' 6'
    #
    # elements = logRow.split(' ', 5)
    elements = [logRow[0:4]]
    logRowRest = logRow[4:].strip().split(" ", 4)
    for eachPart in logRowRest:
        elements.append(eachPart)

    # Extract process name and PID
    regexMatch = re.search(regexPattern, elements[4])
    if regexMatch:
        process = regexMatch.group(2)
        pid = int(regexMatch.group(4))
    else:
        process = elements[4].replace(":", "")
        pid = 0

    logRecord = {
        "id": currentRow,
        "message": logRow,
        "creationTimestamp": datetime.now().strftime("%Y-%m-%dT%I:%M:%S%p%z"),
        "data": {
            "month": elements[0].strip(),
            "day": elements[1].strip(),
            "year": None,
            "time": elements[2].strip(),
            "hostname": elements[3].strip(),
            "service": [{"process": process, "pid": pid}],
            "msg": elements[5].strip(),
        },
    }

    """ ## Disabled # Direct write to file

    # Adding an opening curly brace
    if currentRow == 1:
        logOutput.write('{')
        logOutput.write('"syslog":[')

    logOutput.write('{')
    logOutput.write('"id":{},'.format(str(currentRow)))
    logOutput.write('"message":"{}",'.format(logRow))
    logOutput.write('"creationTimestamp":"{}",'.format(
        datetime.now().strftime('%Y-%m-%dT%I:%M:%S%p%z'))
        )

    logOutput.write('"data":{')
    logOutput.write('"month":"{}",'.format(elements[0]))
    logOutput.write('"day":"{}",'.format(elements[1]))
    logOutput.write('"year":"",')
    logOutput.write('"time":"{}",'.format(elements[2]))
    logOutput.write('"hostname":"{}",'.format(elements[3]))
    logOutput.write('"service":[{')
    logOutput.write('"process":"{}","pid":{}'.format(process, pid))
    logOutput.write('}],')
    logOutput.write('"msg":"{}"'.format(elements[5]))
    logOutput.write('}')

    if currentRow != totalRows:
        # All rows
        logOutput.write('},')
    else:
        # Last row in input file
        logOutput.write('}')

    # Adding an closing curly brace
    if currentRow == totalRows:
        logOutput.write(']}')
    """
    return logRecord


def schemaImport(schemaJSON: str):
    """JSON schema import"""
    if os.path.isfile(schemaJSON):
        with open(schemaJSON, "r", encoding="utf-8") as schemaJSON:
            try:
                mainSchema = json.load(schemaJSON)
                logger.info("Schema file successfully imported.")
                return True, mainSchema
            except json.decoder.JSONDecodeError as schemaError:
                logger.error(
                    "Error while importing schema file! JSON data verification will not be performed."
                )
                return False, None
    else:
        logger.error(f"Schema file {schemaJSON} not found!")
        return False, None


def stringToRaw(stringLine: str):
    """Log row conversion to raw string format"""
    return stringLine.encode("unicode_escape").decode()


def printTimeout(timeOut):
    """Sets timeout"""
    time.sleep(timeOut)
