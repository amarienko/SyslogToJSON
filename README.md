# Syslog To JSON Export

### Description

Syslog file export to JSON format. Syslog is a standard for sending and receiving notification messages–in a particular format from various sources. The syslog messages include time stamps, event messages, severity, host IP addresses, diagnostics and more.

The Syslog protocol was initially written by Eric Allman and is defined in [RFC 3164](https://www.ietf.org/rfc/rfc3164.txt). Since 2009, syslog has been standardized by the IETF in RFC 5424. The RFC 5424 is available at the URL  [https://www.rfc-editor.org/rfc/rfc5424.html](https://www.ietf.org/rfc/rfc3164.txt)

The full format of a syslog message seen on the wire has three discernable parts. The first part is called the **PRI**, the second part is the **HEADER**, and the third part is the **MSG**.

The **PRI** part MUST have three, four, or five characters and will be bound with angle brackets as the first and last characters.

The **HEADER** part contains a timestamp and an indication of the hostname or IP address of the device. The **HEADER** part of the syslog packet *MUST* contain visible (printing) characters. The **HEADER** contains two fields called the **TIMESTAMP** and the **HOSTNAME**.

The **TIMESTAMP** field is the local time and is in the format of `"Mmm dd hh:mm:ss"` (without the quote marks).

The **HOSTNAME** field will contain only the hostname, the IPv4 address, or the IPv6 address of the originator of the message. The preferred value is the hostname.

The **MSG** part will fill the remainder of the syslog packet. This will usually contain some additional information of the process that generated the message, and then the # text of the message. There is no ending delimiter to this part. The **MSG** part has two fields known as the **TAG** field and the **CONTENT** field. The value in the **TAG** field will be the name of the program or process that generated the message.

The **CONTENT** contains the details of the message. This has traditionally been a freeform message that gives some detailed information of the event.

The System Log can be found at `/var/log/messages` (FreeBSD) or `/var/log/syslog` (Linux), and may contain information not included in other logs. The format of the messages in the syslog file refers to the syntax defined by The Syslog Protocol standard.
Syslog files of both types of systems contain the following structure:

- **HEADER**  consisting of `TIMESTAMP` and `HOSTNAME` fields
- **MGS**     consisting of `TAG` and `CONTENT` fields

**Fields format:**

* *TIMESTAMP* `Mmm dd hh:mm:ss` where:

    `Mmm` is the English language abbreviation for the month of the year with the first character in uppercase and the other two characters in lowercase.
    
    `dd` is the day of the month.  If the day of the month is less than 10, then it MUST be represented as a space and then the number.
    
    `hh:mm:ss` is the local time. The hour (hh) is represented in a 24-hour format.

* *HOSTNAME* string. Contains hostname or IPv4/IPv6 address

* *TAG* A string of ABNF alphanumeric characters that MUST NOT exceed 32 characters. This is usually the process name and process id (often known as the "PID") for robust operating systems. The format of `"TAG[pid]:"` - without the quote marks - is common.

* *CONTENT* a freeform message that gives some detailed information of the event. Most commonly, the first character of the CONTENT field that signifies the conclusion of the TAG field has been seen to be the left square bracket character (`"["`), a colon character (`":"`), or a space character.

### Examples

```
<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8
<13>Feb  5 17:32:18 10.0.0.99 Use the BFG!
```

The script generates an output **JSON** file with the following structure:

```
    {
        "message": ""
        "id": ,
        "creationTimestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "data": {
            "month": "",
            "day": "",
            "year": "",
            "time": "",
            "hostname": "",
            "service": [
                {
                    "process": "",
                    "pid": ""
                }
            ],
            "msg": ""
        }
    }
```

JSON file format is described in the file `schema.json` which can be used to validate the outgoing file.

### Script usage

```
./syslog-to-json-export [-i string] [-n] [-o string] [-j string] [-c] [-h] [-H] [-v]
```
**Options**

```
-i string   path to input syslog file. If not specified, the default location '/var/log/syslog'
            is used.

-n          disable progress indicator

-o string   path to the output directory in which the JSON out syslog file will be created
            and the log files of the script will be placed. Default '/tmp'. If the path is
            not  specified, the  output JSON file  and  script logs will be created in the
            default directory.

-j string   checking the output JSON file with the 'jq' utility. Default option, JSON file
            will be verified by the 'jq' command. If the 'jq' executable is not installed
            in the default directory (/usr/bin), you must specify the full path to the 'jq'
            executable file.

-c          do not verify output JSON file

-h          display short usage and exit

-H          display this help and exit

-v          show the current script version
```

### Important

During the processing of syslog file rows, the double quote `'"'` character in the CONTENT is replaced with a single quote `"'"` character for compatibility with the JSON format.

### Notes

* The script uses the basic system utilities installed by default with the operating system `awk`, `sed` and `cut`

* To check the output JSON file, the `jq` command is used (*must be installed in the system*). The default path `/usr/bin/jq` is used to run the `jq` command. If the executable file is not installed in the `/usr/bin` directory, then the path to the `jq` command must be specified in the `-j` option.

* To disable the check of an output JSON file, you can use the `-c` option.

### References

* [https://www.w3schools.com/whatis/whatis_json.asp](https://www.w3schools.com/whatis/whatis_json.asp)
* [https://json-schema.org/draft/2020-12/json-schema-core.html](https://json-schema.org/draft/2020-12/json-schema-core.html)
