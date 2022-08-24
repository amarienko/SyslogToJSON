#!/usr/bin/env bash
#
## Trim leading and trailing spaces
#
trim_spaces() {
    local str="$*"
    # remove leading whitespace characters
    # optional - remove leading: str="${str## }" # one space per run
    while [[ $str == ' '* ]]; do str="${str## }"; done
    # remove trailing whitespace characters
    # optional - remove trailing: str="${str%%}" # one space per run
    while [[ $str == *' ' ]]; do str="${str%% }"; done
    echo -en "${str}"
    return 0
}

#EOF
