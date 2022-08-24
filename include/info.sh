#!/usr/bin/env bash
#
## Script version and usage
#
version() {
    # Print version and exit
    printf "$(colorwhite_bold $0) syslog to JSON export script\n"
    printf "$(colorgreen ${version})\n"; printf "\n"
    exit 0
}

usage() {
    # Print short script usage
    printf "$(colorwhite_bold $0) syslog to JSON export script\n"
    printf "\n"
    printf "Script usage: \n"
    printf "\n"
    printf "$(colorwhite_bold $0) [-i string] [-n] [-o string] [-j string] [-c] [-h] [-H] [-v]\n"
    printf "\n"
    printf "\n"
}

help() {
    # Print script usage
    printf "\n"
    printf "$(colorcyan 'NAME')\n"
    printf "\n"
    printf "$(colorwhite_bold $0) syslog to JSON export script\n"; printf "\n"
    printf "$(colorcyan 'SYNOPSIS')\n"
    printf "\n"
    printf "$(colorwhite_bold $0) [-i string] [-n] [-o string] [-j string] [-c] [-h] [-H] [-v]\n"
    printf "\n"
    printf "$(colorcyan 'DESCRIPTION')\n"
    printf "\n"
    printf "Syslog file export to JSON format. The System Log can be found at /var/log/syslog, and\n"
    printf "may contain information not included in other logs. The format of the messages in the\n"
    printf "syslog file refers to the syntax defined by The Syslog Protocol standard.\n"
    printf "\n"
    printf "The Syslog Protocol is described in the RFC 5424. The RFC 5424 is available at the next\n"
    printf "URL: https://www.rfc-editor.org/rfc/rfc5424.html\n"
    printf "\n"
    printf "$(colorcyan 'OPTIONS')\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-i string')\tpath to input syslog file. If not specified, the default location\n"
    printf "\t         \t'/var/log/syslog' is used.\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-n')       \tdisable progress indicator\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-o string')\tpath to the output directory in which the JSON out syslog file will\n"
    printf "\t         \tbe created and the log files of the script will be placed. Default\n"
    printf "\t         \t'/tmp'. If the path is not specified, the output JSON file and script\n"
    printf "\t         \tlogs will be created in the default directory.\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-j string')\tchecking the output JSON file with the 'jq' utility. Default option, JSON\n"
    printf "\t         \tfile will be verified by the 'jq' command.\n"
    printf "\t         \tIf the 'jq' executable is not installed in the default directory (/usr/bin),\n"
    printf "\t         \tyou must specify the full path to the 'jq' executable file.\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-c')       \tdo not verify output JSON file\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-h')       \tdisplay short usage and exit\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-H')       \tdisplay this help and exit\n"
    printf "\n"
    printf "\t$(colorwhite_bold '-v')       \tshow the current script version\n"
    printf "\n"
    printf "$(colorcyan 'EXAMPLES')\n"
    printf "\n"
    printf "\t$0 -v\n"
    printf "\t$0 -i /var/log/syslog.log\n"
    printf "\t$0 -i /var/log/syslog -o /var/tmp\n"
    printf "\t$0 -n -j /usr/local/bin/jq\n"
    printf "\n"
    printf "\n"
}

#EOF
