#!/usr/bin/env bash
#
## Progress bar functions
#
progress_cleanup() {
    sleep 1
    # Cleaning progress bar
    ##echo -ne "\r"
    printf "\r"
    printf ' %.s' $(eval "echo {1.."${screenCols}"}")
}

progress() {
    ## Setting color variable values
    local color_fg="15"
    local color_bg="69"
    local foregrnd="${ESC}[${BOLD};${FG};${color_fg}${M}"
    local backgrnd="${ESC}[${BG};${color_bg}${M}"
    local color="$foregrnd$backgrnd"
    #
    if [[ ! $1 == "init" ]]; then
        local progress=$1
    else
        local progress=0
    fi

    if [[ $2 == "error" ]]; then
        local errMsg=$3
        local errPrint="true"
        errMsg=" ${errMsg} "
        errMsgLenght=${#errMsg}
        fills=0
        errs=$errMsgLenght
    else
        errs=0
        # Blank progress bar `0%`
        fills=$(( $blanks * $progress / 100 ))
        #echo ""
        #printf "Progress $progress should be fill:\t$fills cols\n"
    fi

    bracketStart="$bracketStart$color"
    bracketEnd="$RST$bracketEnd"
    printf " %s %s %3d%% %s [" $bracketStart $statusString $progress $bracketEnd
    #        %cs         %ce   $set clr                               $reset clr

    if [ $fills -gt 0 ]; then
        # If progress more then 0
        printf "${fill}%.s" $(eval "echo {1.."${fills}"}")   # Fill
    elif [[ "$fills" -eq 0 && "$errPrint" == "true"  ]]; then
        # If an error message is printed
        printf "%s" "$errMsg"   # Error Message
    fi

    if [[ ! $fills == $blanks ]]; then
        # If task is completed, progress 100%
        if [[ "$errPrint" == "true"  ]]; then
            printf "${space}%.s" $(eval "echo {1.."$(( $blanks - ( $fills + $errs ) ))"}")   # Blank
        else
            printf "${blank}%.s" $(eval "echo {1.."$(( $blanks - ( $fills + $errs ) ))"}")   # Blank
        fi
    fi

    printf "%s" $rightSide

    if [[ $progress -eq 100 ]]; then
        progress_cleanup
    fi

    #sleep 30
}

#EOF
