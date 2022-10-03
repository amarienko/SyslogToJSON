#!/usr/bin/bash
#
#    <
#    .SYNOPSIS
#    Syslog file export to JSON format.
#
#    .DESCRIPTION
#    Syslog file export to JSON format. Syslog is a standard for sending and
#    receiving  notification messages–in a particular format from various
#    sources. The syslog messages include time stamps, event messages, severity,
#    host IP addresses, diagnostics and more.
#
#    The Syslog protocol was initially written by Eric Allman and is defined in
#    RFC 3164 https://www.ietf.org/rfc/rfc3164.txt Since 2009, syslog has been
#    standardized by the IETF in RFC 5424. The RFC 5424 is available at the URL:
#    https://www.rfc-editor.org/rfc/rfc5424.html
#
#    The full format of a syslog message seen on the wire has three discernable
#    parts. The first part is called the PRI, the second part is the HEADER, and
#    the third part is the MSG.
#
#    The PRI part MUST have three, four, or five characters and will be bound
#    with angle brackets as the first and last characters.
#
#    The HEADER part contains a timestamp and an indication of the hostname or IP
#    address of the device. The HEADER part of the syslog packet MUST contain
#    visible (printing) characters.
#
#    The HEADER contains two fields called the TIMESTAMP and the HOSTNAME.
#
#    The TIMESTAMP field is the local time and is in the format of "Mmm dd
#    hh:mm:ss" (without the quote marks).
#
#    The HOSTNAME field will contain only the hostname, the IPv4 address, or
#    the IPv6 address of the originator of the message. The preferred value
#    is the hostname.
#
#    The MSG part will fill the remainder of the syslog packet. This will
#    usually contain some additional information of the process that generated
#    the message, and then the # text of the message. There is no ending
#    delimiter to this part.
#
#    The MSG part has two fields known as the TAG field and the CONTENT field.
#    The value in the TAG field will be the name of the program or process that
#    generated the message.
#
#    The CONTENT contains the details of the message. This has traditionally
#    been a freeform message that gives some detailed information of the event.
#
#    The System Log can be found at /var/log/messages (FreeBSD) or /var/log/syslog
#    (Linux), and may contain information not included in other logs. The format
#    of the messages in the syslog file refers to the syntax defined by The Syslog
#    Protocol standard.
#    Syslog files of both types of systems contain the following structure:
#
#    - HEADER  consisting of TIMESTAMP and HOSTNAME fields
#    - MGS     consisting of TAG and CONTENT fields
#
#    Fields format:
#
#    TIMESTAMP Mmm dd hh:mm:ss where:
#
#    Mmm      is the English language abbreviation for the month of the year
#             with the first character in uppercase and the other two characters
#             in lowercase.
#    dd       is the day of the month.  If the day of the month is less than 10,
#             then it MUST be represented as a space and then the number.
#    hh:mm:ss is the local time. The hour (hh) is represented in a 24-hour
#             format.
#
#    HOSTNAME string. Contains hostname or IPv4/IPv6 address
#
#    TAG      A string of ABNF alphanumeric characters that MUST NOT exceed 32
#             characters. This is usually the process name and process id (often
#             known as the "PID") for robust operating systems. The format of
#             "TAG[pid]:" - without the quote marks - is common.
#
#    CONTENT  a freeform message that gives some detailed information of the
#             event. Most commonly, the first character of the CONTENT field
#             that signifies the conclusion of the TAG field has been seen to be
#             the left square bracket character ("["), a colon character (":"),
#             or a space character.
#
#    Syslog Examples
#    <34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8
#    <13>Feb  5 17:32:18 10.0.0.99 Use the BFG!
#
#    The script generates an output JSON file with the following structure:
#
#    {
#      "id": logrow,
#      "message": "Mmm dd HH:MM:SS hostname process[pid]: log message",
#      "creationTimestamp": "YYYY-MM-DDTHH:MM:SSZ",
#      "data": {
#        "month": "Mmm",
#        "day": "dd",
#        "year": null,
#        "time": "HH:MM:SS",
#        "hostname": "hostname",
#        "service": [
#          {
#            "process": "name",
#            "pid": pid
#          }
#        ],
#        "msg": "log mesage"
#      }
#    }
#
#
#    JSON References:
#    https://www.w3schools.com/whatis/whatis_json.asp
#    https://json-schema.org/draft/2020-12/json-schema-core.html
#
#    JSON file format is described in the file 'syslog2json-schema.json' which
#    can be used to validate the outgoing file.
#
#    .PARAMETERS
#    syslog2json [-i string] [-n] [-o string] [-j string] [-c] [-h] [-H] [-v]
#
#    .EXAMPLES
#    syslog2json -v
#    syslog2json -i /var/log/syslog.log
#    syslog2json -i /var/log/syslog -o /var/tmp
#    syslog2json -n -j /usr/local/bin/jq
#
#    .NOTES
#    IMPORTANT! During the processing of syslog file rows, the double quote '"'
#    character in the CONTENT is replaced with a single quote "'" character for
#    compatibility with the JSON format.
#
#    The script uses the basic system utilities installed by default with the
#    operating system 'awk', 'sed' and 'cut'.
#
#    To check the output JSON file, the 'jq' command is used (must be installed
#    in the system). The default path /usr/bin/jq is used to run the 'jq' command.
#    If the executable file is not installed in the /usr/bin directory, then
#    the path to the 'jq' command must be specified in the -j option.
#
#    To disable the check of an output JSON file, you can use the -c option.
#    >
#
#
version="v0.1.8"
#
# Exit immediately if a command exits with a non-zero status
set -e
# Set pipefail so that any failure in a pipeline will return an error
set -o pipefail
# Disable file name generation (globbing)
# set -f

#. /lib/lsb/init-functions
. include/progress.sh
. include/format.sh
. include/colors.sh
. include/info.sh
if [ -f /etc/os-release ]; then
    . /etc/os-release
    osName=$NAME
    osVer=$VERSION
    homeURL=$HOME_URL
elif [ -f /usr/bin/lsb_release ]; then
    osName=$(lsb_release -sd)
    osVer=$(lsb_release -sc)
    homeURL=""
else
    osName=""
    osVer=""
    homeURL=""
fi

kernelName=$(uname -s)
kernelRelease=$(uname -r)
kernelVersion=$(uname -v)
processorType=$(uname -p)

## Interrupt processing
#
ctrl_break() {
    echo ""
    echo "$(colorred_bold 'Interrupted by user!')"
    echo ""
    clear
    echo "$(colorwhite_bold 'Clean up...')"
    echo ""
    write_log "Interrupted by user!"

    printf "[   ] Deleting an input file"
    rm $inFile 2> /dev/null
    sleep 0.3
    printf "\r"
    printf "[ $(colorgreen $pass) ] Deleting an input file\n"
    printf "[   ] Deleting temporary and output file(s)"
    #rm $logOutput 2> /dev/null
    if [ -f $logOutput.bak ]; then
        rm $logOutput.bak 2> /dev/null
    fi
    rm $outputDir/syslog.* 2> /dev/null
    sleep 0.3
    printf "\r"
    printf "[ $(colorgreen $pass) ] Deleting temporary and output file(s)\n"

    echo ""
    printf "******************************************************************\n"
    printf "Script execution was interrupted by the user. Detailed information\n"
    printf "is saved in the log file: ${scriptLogFile}\n"
    echo ""
    printf "End time: $(TZ=UTC date +%Y-%m-%d@%H:%M:%SZ)\n"
    printf "******************************************************************\n"
    echo "--- End syslog file processing" &>> $scriptLogFile
    echo ""
    trap "" 2 3 15 20
    exit 2
}

## OS tools verification
#
tools_verification() {
    local toolName=$1
    set +e

    typeOutput=$(type -p ${toolName} 2> /dev/null) # &> /dev/null
    typeCheck=$?
    if [[ ! -z "$typeOutput" && $typeCheck -eq 0 ]]; then
        echo 0
    else
        echo 1
    fi

    set -e
}

## JSON verification
#
json_verification() {
    write_log "Verification of the resulting JSON file"
    write_log "/*"
    # Turn OFF the -e flag. If a `jq` command exits with a non-zero status
    # the error will be handled inside the function. Detailed information
    # about the error will be written to the .log and .err files
    set +e
    #jq -M .syslog[1] $logOutput >> $scriptLogFile 2> $errFile
    testResult=$(${jqPath} -M .syslog[1] $logOutput 2> $errFile)
    exitCode=$?

    if [ $exitCode == 0 ]; then
        sleep 0.3
        printf "\r"
        printf "[ $(colorgreen '√') ] File verification completed!\n"

        write_log "${testResult}" "true"
        write_log "*/"
        write_log "'jq' return code ${exitCode}"
    else
        sleep 0.3
        printf "\r"
        printf "[ $(colorred '×') ] File verification return an error!\n"
        echo ""
        printf "Please see detailed information in the log file ${errFile}\n"

        write_log "{" "true"
        write_log "" "true"
        write_log "  File verification return an error!" "true"
        write_log "  Detailed information about the error is saved in the ${errFile} file." "true"
        write_log "" "true"
        write_log "}" "true"
        write_log "*/"
        write_log "'jq' return code ${exitCode}"
    fi

    # Returns the original value of the -e flag.
    set -e
}

## Logging
#
write_log() {
    local logMsg=$1
    local noTimestamp=$2
    #echo $logMsg $noTimestamp
    if [ -f $scriptLogFile ]; then
        if [[ ! -z "$noTimestamp" && "$noTimestamp" == "true" ]]; then
            printf '%s\n' "$logMsg" &>> $scriptLogFile
        else
            printf '%s %s\n' $(date +%Y-%m-%d@%H:%M:%SZ) "$logMsg" &>> $scriptLogFile
        fi
    fi
}

## Final message
#
operation_completed() {
    # Setting color variable values
    local color_fg="34"
    local foregrnd="${ESC}[${BOLD};${FG};${color_fg}${M}"
    local color="$foregrnd"
    #
    if [ -z "$1" ]; then
        printMessage="Operation completed!"
    else
        printMessage=$1
    fi
    echo ""
    printf "[   ]\t%s" "${printMessage}"
    sleep 0.5
    printf "\r[ %s√%s ]\t%s" $color $RST "${printMessage}!"
    printf "\n"
}

## Default values
#
workDir="/var/log"
logfileName="syslog"
logInput="$workDir/$logfileName"

outputDir="/tmp"
outputFile="syslog.json"

PROGRESS_BAR="yes"
JQ_CMD="yes"
jqPath="/usr/bin/jq"

## Capturing interrupt signals
#
# INT(2)
# QUIT(3)
# TERM(15)
# TSTP(20)
#
# `Ctrl + C` and `Ctrl + Z` keyboard breaks 
#
TRAP_MSG="Exiting now..."
#trap "echo 'Interrupted by user! SIGINT signal received" 2
#trap "echo 'Interrupted by user! SIGTSTP signal received" 20
trap "ctrl_break" INT QUIT TERM TSTP


## Process the input options with `getopts`
#
backupIFS=$IFS
IFS=","
while getopts ":i:o:nj:chHv" option; do
    NUMARG=($2)
    #echo "Total Number of arguments = ${#NUMARG[@]}"
    case $option in
        i )
            # Full path to input syslog file
            if [ ${#NUMARG[@]} -ge 1 ]; then
                logList=$OPTARG
            fi
            #if [ ! -z $OPTARG ]; then
            #    logInput=$OPTARG
            #fi
            ;;
        n )
            # Disable progress bar
            PROGRESS_BAR="no"
            ;;
        o )
            # Output/Work Directory
            if [ ! -z $OPTARG ]; then
                outputDir=$(echo $OPTARG | sed -E 's|((^.*)(\/$))|\2|g')
            fi
            ;;
        j )
            # Path to 'jq' command
            if [ ! -z $OPTARG ]; then
                jqPath=$OPTARG
            fi
            ;;
        c )
            # Disabling output file verification
            JQ_CMD="no"
            ;;
        h )
            # Display short usage
            usage
            exit 0
            ;;
        H )
            # Display short usage
            help
            exit 0
            ;;
        v )
            # Display the version
            version
            exit 0
            ;;
        : )
            echo ""; echo "$(colorred_bold 'Error:') Argument missing for option '-$OPTARG'!"
            echo ""
            exit 1
            ;;
        \? | * )
            # Invalid options
            echo ""; echo "$(colorred_bold 'Error:') Invalid option '-$OPTARG!'"
            echo ""
            usage
            exit 1
            ;;
    esac
done

## Print System Information
#
clear
echo "$(colorwhite_bold 'Collected System Information')"
echo ""
echo "$osName $osVer"
echo "$kernelName $kernelRelease $kernelVersion $processorType"
if [ ! -z $homeURL ]; then
    echo "$homeURL"
fi

## Creating file for import
#

inFile="$outputDir/inLogFile.log"
if [ -f $inFile ]; then
    rm $inFile 2> /dev/null
    echo "Existing OLD input log file ${inFile} has been deleted"
fi
touch $inFile

if [ ${#logList[@]} -ge 1 ]; then
    # the value passed as an argument is used
    declare -a inputLogs
    inputLogs=($logList)
    if [ ${#logList[@]} -gt 1 ]; then
        echo "More than one log file will be imported."
    fi
    #declare -p inputLogs

    for (( idx=0; idx < ${#inputLogs[@]}; idx++ )); do
        if [ -f ${inputLogs[$idx]} ]; then
            cat ${inputLogs[$idx]} >> $inFile
        fi
    done
else
    # default value is used
    #echo "One log file will be imported."
    if [ -f $logInput ]; then
        cat ${logInput} >> $inFile
    fi
fi

IFS=$backupIFS


logInput=$inFile
logOutput="$outputDir/$outputFile"
scriptLogFile="$outputDir/syslogexport.log"
errFile="$outputDir/syslogexport.err"

delimeterSymbol=" "

## Colors global
color_fg=""
color_bg=""
FOREGRND="${ESC}[${FG};${color_fg}${M}"
BACKGRND="${ESC}[${BG};${color_bg}${M}"

## Tools and input parameters verification
#
paramVerifyOK=true
paramVerifyFail=true
echo ""
echo "$(colorwhite_bold 'Parameters verification')"
echo ""

printf "[   ] Input file..."
sleep 0.3
if [ -f $logInput ]; then
    printf "\r[ $(colorgreen '√') ] Input file: ${logInput}\n"
    fileSize=(stat --printf="%s" $logInput)
else
    printf "\r[ $(colorred '×') ] Input file not found!\n"
    paramVerifyFail=false
fi

printf "[   ] Output directory..."
sleep 0.3
if [ -d $outputDir ]; then
    printf "\r[ $(colorgreen '√') ] Output directory: ${outputDir}\n"
    printf "[   ] Directory read/write permition..."
    if [ -w $outputDir ]; then
        printf "\r[ $(colorgreen '√') ] '${outputDir}' directory is writable by the user\n"
        userRW="yes"
    else
        printf "\r[ $(colorred '×') ] The user does not have permission to write to '${outputDir}' directory\n"
        userRW="no"
        paramVerifyFail=false
    fi
else
    printf "\r[ $(colorred '×') ] Output directory not found!\n"
    paramVerifyFail=false
fi

printf "[   ] Output file..."
sleep 0.3
if [[ "$userRW" != "no" ]]; then
    if [ ! -f $logOutput ]; then
        touch $logOutput
        printf "\r[ $(colorgreen '√') ] Output file ${logOutput} created\n"
        echo ""
    else
        printf "\r[ $(colormagenta '√') ] Output file ${logOutput} found in destination directory!\n"
        echo ""
        printf "  •   $(colorwhite_bold 'Existing file will be overwritten!') A backup copy of the existing\n"
        printf "  •   file will be saved in the file ${logOutput}.bak\n"
        cp $logOutput "$logOutput.bak"
        rm $logOutput
        touch $logOutput
        echo ""
    fi
else
    printf "\r[ $(colorred '×') ] Output file not created!\n"
    paramVerifyFail=false
fi

if [[ "$JQ_CMD" == "yes" ]]; then
    printf "[ $(colorgreen '√') ] Output JSON file verification: Enabled (Default)\n"
else
    printf "[ $(colormagenta '√') ] Output file verification: Disabled\n"
fi

sleep 0.1
if [[ "$PROGRESS_BAR" == "yes" ]]; then
    printf "[ $(colorgreen '√') ] Progress bar: Enabled (Default)\n"
else
    printf "[ $(colormagenta '√') ] Progress bar: Disabled\n"
fi
echo ""

echo "$(colorwhite_bold 'Verification of required system components')"
# `awk` | `sed` | `cut` | disabled `tr`
echo ""
os=$(uname -s)
osName=$(echo "${os,,}")
typeVerifyOK=true
typeVerifyFail=true

if [[ "$osName" == "linux" || "$osName" == "freebsd" ]]; then
    toolsList=("awk" "sed" "cut") # "tr"
    tool=0
    while [ $tool -lt ${#toolsList[@]} ]; do
        toolCheck=$(tools_verification ${toolsList[$tool]})
        #echo "${toolsList[$tool]} $toolCheck"
        if [ $toolCheck -eq 0 ]; then
            printf "[ $(colorgreen '√') ] ${toolsList[$tool]}\n"
        else
            printf "[ $(colorred '×') ] ${toolsList[$tool]}\n"
            typeVerifyFail=false
        fi
        sleep 0.1
        ((++tool))
    done
fi

if [[ "$JQ_CMD" == "yes" ]]; then
    echo ""
    printf "[   ] jq..."
    sleep 0.3
    if [[ -f "$jqPath" && -x "$jqPath" ]]; then
        printf "\r[ $(colorgreen '√') ] jq are installed"
        echo ""
    else
        printf "\r[ $(colorred '×') ] jq not found"
        echo ""
        typeVerifyFail=false
    fi
fi


if [[ "$paramVerifyOK" == "$paramVerifyFail" ]]; then
    echo ""; printf "$(colorwhite_bold 'Сompleted!') All parameters are set.\n"
    if [[ "$typeVerifyOK" == "$typeVerifyFail" ]]; then
        printf "$(colorwhite_bold 'Сompleted!') All necessary components are installed.\n"
        echo ""
    else
        printf "$(colorred_bold 'Сompleted!') One or more components are not installed!\n"
        echo ""
        exit 1
    fi
else
    echo ""; printf "$(colorred_bold 'Сompleted!') One or more parameters did not pass validation!\n"
    echo ""
    exit 1
fi

## Log file
#
if [ -f $scriptLogFile ]; then
    rm $scriptLogFile
fi
touch $scriptLogFile
echo "--- Start syslog file processing" &> $scriptLogFile

## Progress bar definition
#
screenCols=$(tput cols)
screenRows=$(tput lines)

operatingLine=$(( screenRows - 1 ))

space=" "
statusString="Progress:"
percent="%"
bracketStart="["
bracketEnd="]"

progress0=0
progress100=100

statusStringFull="$space$bracketStart$space$statusString$space$progress100$space$bracketEnd$space"
# Full string + `%` sign + bar open bracket `[`
statusStringLenght=$(( ${#statusStringFull} + 1 + 1 ))

# Righ side
# '] '
rightSide="] "
rightSideLenght=$(( ${#rightSide} ))

# Qty. of the blank bars calculation
blanks=$(( $screenCols - $statusStringLenght - $rightSideLenght ))

## ASCII characters for fill the progress bar
#  https://coding.tools/ascii-table
#
# `░`    Graphic character, low density dotted
# `▒`    Graphic character, medium density dotted
# `▓`    Graphic character, high density dotted
# `█`    Block, graphic character
#
#blank="."
blank="░"
fill="█"

# Additional ASCII used
pass="√"
fail="×"
#cancel="Ø"
cancel="ø"

#
## Syslog file processing
#
printf "$(colorwhite_bold 'Syslog file processing')\n"
echo ""
logRows=$(awk 'END { print NR }' $logInput)

printf "$(colorcyan $logRows) rows in the log file for processing\n"
printf "Log file processing started at: $(TZ=UTC date +%Y-%m-%d@%H:%M:%SZ)\n"
echo ""
write_log "Start log file processing"

echo ""
#progress 0

startTime=$(date +%s)
backupIFS=$IFS

while IFS= read -r line; do

    ((++rowNumber))
    #echo "Processing line (${rowNumber}): ${line}"

    # Disabled and optimazed after tests
    : '
       logRecord=$(echo "$line" | \
       perl -pe \
           "s/
           (?<month>^[JFMASOND]..)
           [[:space:]]
           (?<day>[0-9]{2})
           [[:space:]]
           (?<time>[[:digit:]]{2}\:[[:digit:]]{2}\:[[:digit:]]{2})
           [[:space:]]
           (?<hostname>([a-z0-9]|[\-])*([a-z0-9]|[\-])+)
           [[:space:]]
           (?<process>([a-z0-9]|\[(.*)\]|[\-])*([a-z0-9]|\[(?<pid>.*)\]|[\-])+)\:
           [[:blank:]]
           (?<msg>.*)$
           /$+{month}\n$+{day}\n$+{time}\n$+{hostname}\n$+{process}\n$+{pid}\n$+{msg}/g")
    '

    write_log "Row ${rowNumber} of ${logRows}"
    #declare -a rowArray &> /dev/null ## Array creation
    nullValue="null"    ## Variable for filling JSON `null` type
    if [ ! -z "$line" ]; then
        ## Reading and processing a line of a log file
        #
        # Removal of double quotes for the correct composition of the JSON file
        line=$(echo ${line} | sed -e "s/\"/\\'/g")
        # Array Idxs from [0] to [3]. Static fields
        #logRecord=$(echo ${line} | cut -d ' ' -f 1-4 | tr ' ' '\n')
        logRecord=$(echo ${line} | cut -d ' ' -f 1-4 | sed -E 's| |\n|g')
        readarray -t rowArray <<< $logRecord

        # Array Idxs [4] and [5]. Variable fields
        index4Test=($(echo ${line} | cut -d ' ' -f 5))
        index4=($(echo ${line} | cut -d ' ' -f 5 | sed -E 's/((^.*)(\[([0-9]{1,})\]))(\:)$/\2/g'))
        if [[ $? -eq 0 && "$index4" == "$index4Test" ]]; then
            rowArray[4]="$(echo "${index4}" | sed -E 's/\://')"
            # Index 5 (Empty, Not Defined)
            #index5=0   ## Disabled # Usage pid=0 replaced with `null` JSON value
            index5=$nullValue
        else
            rowArray[4]="$index4"
            # Index 5 default
            index5=($(echo ${line} | cut -d ' ' -f 5 | sed -E 's/((^.*)(\[([0-9]{1,})\]))(\:)$/\4/g'))
        fi
        rowArray[5]="$index5"

        # Array Idxs [6]. Main message field
        element6=("$(echo ${line} | cut -d ' ' -f 6-)")
        rowArray[6]="$element6"


        for (( arrayIndex=0; arrayIndex < ${#rowArray[@]}; arrayIndex++ )); do
            rowArray[arrayIndex]=$(trim_spaces ${rowArray[arrayIndex]})
        done
        fullLine=$(trim_spaces $(echo ${line}))

        write_log "Row ${rowNumber} processed successfully"
    else
        errorMsg="Empty 'null' line in input file!"
        errorMsgLenght=${#errorMsg}
        msgString="Row ${rowNumber} of ${logRows}"
        msgStringLenght=${#msgString}
        spacesLeft=$(( $screenCols - ( $msgStringLenght + $errorMsgLenght + 1 ) ))

        if [[ "$PROGRESS_BAR" == "no" ]]; then
            printf "\rRow %d of %d %s" $rowNumber $logRows "${errorMsg}"
            printf "${space}%.s" $(eval "echo {1.."${spacesLeft}"}")
            sleep 0.5
        fi
        write_log "Row ${rowNumber} processed with an error"
        write_log "${errorMsg}. Line number: ${rowNumber}"
    fi

    # Building a variables with all fields for printing to a file
    #
    #declare -p rowArray &> /dev/null
    arrayVerification=(${rowArray[@]:+true})
    if [[ ! -z "$arrayVerification" && "$arrayVerification" = "true" ]]; then
        arrayDeclarationStatus="true"
    else
        arrayDeclarationStatus="false"
    fi

    if [[ "$arrayDeclarationStatus" == "true" ]]; then
        #stringPreffix="$(printf '"id%s":{' "${rowNumber}")"                                ## "id1":{
        stringPreffix="$(printf '{')"                                                       ## "{"

        stringPreffix="$stringPreffix$(printf '"id":%d,' ${rowNumber})"                     ## "id":1,
        stringPreffix="$stringPreffix$(printf '"message":"%s",' "$(echo ${fullLine})")"     ## "message":"... ___",
        stringPreffix="$stringPreffix$(printf \
            '"creationTimestamp":"%s",' \
            "$(TZ=UTC date +%Y-%m-%dT%H:%M:%SZ)" \
            )"                                                                              ## "creationTimestamp":"2022-10-03T16:54:47Z",
        stringPreffix="$stringPreffix$(printf '"data":{')"                                  ## "data":{

        if [ $rowNumber == 1 ]; then
            stringPreffix='{"syslog":['$stringPreffix                                       ## {"syslog":[  ## upfront for 1st row
        fi

        finalString="$(printf '"month":"%s",' "${rowArray[0]}")"                            ## "month":"Aug",
        finalString="$finalString$(printf '"day":"%s",' "${rowArray[1]}")"                  ## "day":"3",
        finalString="$finalString$(printf '"year":%s,' "${nullValue}")"                     ## "year":null,
        finalString="$finalString$(printf '"time":"%s",' "${rowArray[2]}")"                 ## "time":"20:34:56",
        finalString="$finalString$(printf '"hostname":"%s",' "${rowArray[3]}")"             ## "hostname":"uls2204-release",
        finalString="$finalString$(printf '"service":[{')"                                  ## "service":[{
        finalString="$finalString$(printf '"process":"%s",' "${rowArray[4]}")"              ## "process":"snapd",
        finalString="$finalString$(printf '"pid":%s}],' "${rowArray[5]}")"                  ## "pid":944}]
        finalString="$finalString$(printf '"msg":"%s"' "${rowArray[6]}")"                   ## "msg":"___"

        if [ $rowNumber == $logRows ]; then
            stringSuffix=$( printf "}}]}")                                                  ## "}}]}"       ## for last row
        else
            stringSuffix=$( printf "}},")                                                   ## "}},"        ## for all other rows
        fi

        # Printing to file
        #jq << EOF >> $logOutput
        cat << EOF >> $logOutput
$stringPreffix$finalString$stringSuffix
EOF

        # Not rounded Percentage (for testing purposes only)
        #div=$(( ( 100 * ($rowNumber * 100) ) / $screenRows ))
        #notRoundedPercent=$(echo "${div:0:-2}.${div: -2}")
        #echo -e ".Dot2 %: $notRoundedPercent %"
        #
        if [ $logRows != 0 ]; then
            executionPercent=$(( ($rowNumber * 100) / $logRows ))
        fi

        if [[ "$PROGRESS_BAR" == "yes" ]]; then
            printf "\r"
            progress $executionPercent
            # Disabled ## Delay updating progress bar when the number of records <= 250
            # if [ $logRows -le 250 ]; then
            #     sleep 0.1
            # fi
        else
            msgString="Row ${rowNumber} of ${logRows}"
            spacesLeft=$(( $screenCols - ${#msgString} ))
            printf "\rRow %d of %d" $rowNumber $logRows
            printf "${space}%.s" $(eval "echo {1.."${spacesLeft}"}")
            if [[ "$rowNumber" == "$logRows" ]]; then
                printf "\r"
                printf ' %.s' $(eval "echo {1.."${screenCols}"}")
                echo ""
            fi
        fi
    else
        errorMsg="Error in input file!"
        if [[ "$rowNumber" -eq 1 && "$logRows" -eq 0 ]]; then
            executionPercent=0
            errorMsg="Error in input file: file is empty!"
        fi
        errorMsgLenght=${#errorMsg}
        msgString="Row ${rowNumber} of ${logRows}"
        spacesLeft=$(( $screenCols - ( ${#msgString} + $errorMsgLenght + 1 ) ))

        if [[ "$PROGRESS_BAR" == "yes" ]]; then
            printf "\r"
            progress $executionPercent "error" "${errorMsg} Row ${rowNumber} of ${logRows}"
        else
            printf "\rRow %d of %d %s" $rowNumber $logRows "${errorMsg}"
            printf "${space}%.s" $(eval "echo {1.."${spacesLeft}"}")
        fi
        sleep 0.5
        write_log "${errorMsg}: Line ${rowNumber} of ${logRows}. Array declaration status: '${arrayDeclarationStatus}'"
    fi

    unset rowArray

done <<< $(cat $logInput)

IFS=$backupIFS
write_log "End syslog file processing"
endTime=$(date +%s)
processingTime=$(( endTime - startTime ))
#echo ""

if [[ ! "$rowNumber" == "$logRows" ]]; then
    printf "\r"
    printf ' %.s' $(eval "echo {1.."${screenCols}"}")
    printf "\n"
    printf "A file processing error occurred! Processed $(colorwhite_bold $rowNumber) rows out of $(colorwhite_bold $logRows)\n"
    printf "\n"

    write_log "A file processing error occurred!"
    write_log "/*"
    write_log "{" "true"
    write_log "" "true"
    write_log "  Rows processed: ${rowNumber}" "true"
    write_log "  Rows total: ${logRows}" "true"
    write_log "" "true"
    write_log "}" "true"
    write_log "*/"
fi

## Adding curly braces "{}" and clean up newline character `\n` in final JSON file
#
# Disabled ## Begining of the file. Added to `Preffix`
# sed -i1~ '1s/^/{/' $logOutput
# Clean up all `\n`s in the file
sed -i2~ -E ':a;N;$!ba;s/\n//g' $logOutput
# Disabled ## End of the file. Added to `Suffix`
# sed -i3~ 's/$/}/' $logOutput

## Output file verification
#
if [[ "$JQ_CMD" == "yes" ]]; then
    if [ $logRows != 0 ]; then
        printf "[   ] JSON file verification..."

        if [[ -f "$jqPath" && -x "$jqPath" ]]; then
            json_verification
        else
            printf "\r"
            echo "Output JSON syslog file verification will not be performed!"
            echo "'jq' commandline JSON processor is not installed. Please see"
            echo "additional information about 'jq' command in the log file."
            echo ""

            write_log "/*"
            write_log "{" "true"
            write_log "" "true"
            write_log "  Output JSON syslog file verification will not be performed!" "true"
            write_log "  'jq' commandline JSON processor is not installed." "true"
            write_log "" "true"
            write_log "  Detailed information about 'jq' can be found at the link:" "true"
            write_log "  https://stedolan.github.io/jq/" "true"
            write_log "" "true"
            write_log "}" "true"
            write_log "*/"
        fi
    else
        printf "[   ] JSON file verification is cancelled!"
        sleep 0.1
        printf "\r"
        printf "[ $(colorred 'ø') ] File verification is cancelled! File is empty.\n"
        write_log "File verification is cancelled!"
        write_log "Reason for cancellation: file is empty."
    fi
fi

## Clean up and remove temporary files
#
write_log "Clean up"
rm $inFile 2> /dev/null
rm $outputDir/syslog.json*~ 2> /dev/null
echo ""
printf "$(colorwhite_bold 'Syslog file import completed!')"
#operation_completed "Syslog file import completed"
echo "--- End syslog file processing" &>> $scriptLogFile

echo ""
printf "Log file processing finished at: $(TZ=UTC date +%Y-%m-%d@%H:%M:%SZ)\n"
echo ""
printf "****************************************************************\n"
printf " Output JSON file saved in '$outputDir' directory with the name:\n"
printf " ${outputFile}\n"
echo ""
printf " File processing time: $(date -d@${processingTime} -u +%H:%M:%S)\n"
printf " Records processed: ${logRows}\n"
if [ $logRows != 0 ]; then
    printf " Average record processing time: $(awk "BEGIN {printf \"%.4f\",($processingTime/$logRows)*1000}") ms\n"
fi
printf "****************************************************************\n"
echo ""


exit 0

#EOF
