#!/usr/bin/env bash
#
## Colors and Font format variables and functions
#
# <Esc> character
#ESC=$(printf "\e")
#ESC=$(printf "\x1B")
ESC=$(printf "\033")

## Most common supported control sequences for formatting text
#
# Format reset value
RESET=0
# Font format variables
BOLD=1
DIM=2
ITALIC=3
UNDERLINE=4
BLINK=5
REGULAR=6
REVERSE=7
HIDDEN=8

# Format string end
M=m
# Variables for 256 colors control sequence "<Esc>[X8;5;`ColorNumber`m"
# "<Esc>[38;5;`ColorNumber`m” - Foreground
# "<Esc>[48;5;`ColorNumber`m” - Background
# ColorNumber - Color code from the range {0..255}
FG="38;5"
BG="48;5"

## Format reset string
RST="${ESC}[${RESET}${M}"
format_reset="${ESC}[0${M}"

## Base Colors
#
# Regular font
black="${ESC}[30${M}"
red="${ESC}[31${M}"
green="${ESC}[32${M}"
yellow="${ESC}[33${M}"
blue="${ESC}[34${M}"
magenta="${ESC}[35${M}"
cyan="${ESC}[36${M}"
white="${ESC}[37${M}"
default="${ESC}[39${M}"

# Bold font
black_bold="${ESC}[${BOLD}30${M}"
red_bold="${ESC}[${BOLD};31${M}"
green_bold="${ESC}[${BOLD}32${M}"
yellow_bold="${ESC}[${BOLD}33${M}"
blue_bold="${ESC}[${BOLD}34${M}"
magenta_bold="${ESC}[${BOLD}35${M}"
cyan_bold="${ESC}[${BOLD}36${M}"
white_bold="${ESC}[${BOLD};37${M}"
default_bold="${ESC}[${BOLD}39${M}"

## Color Functions
#
# Colored Regular Font
colorblack() { printf "${black}%s${RST}\n" "$1"; }
colorred() { printf "${red}%s${RST}\n" "$1"; }
colorgreen() { printf "${green}%s${RST}\n" "$1"; }
coloryellow() { printf "${yellow}%s${RST}\n" "$1"; }
colorblue() { printf "${blue}%s${RST}\n" "$1"; }
colormagenta() { printf "${magenta}%s${RST}\n" "$1"; }
colorcyan() { printf "${cyan}%s${RST}\n" "$1"; }
colorwhite() { printf "${white}%s${RST}\n" "$1"; }
colordefault() { printf "${default}%s${RST}\n" "$1"; }

# Colored Bold Font
colorblack_bold() { printf "${black_bold}%s${RST}\n" "$1"; }
colorred_bold() { printf "${red_bold}%s${RST}\n" "$1"; }
colorgreen_bold() { printf "${green_bold}%s${RST}\n" "$1"; }
coloryellow_bold() { printf "${yellow_bold}%s${RST}\n" "$1"; }
colorblue_bold() { printf "${blue_bold}%s${RST}\n" "$1"; }
colormagenta_bold() { printf "${magenta_bold}%s${RST}\n" "$1"; }
colorcyan_bold() { printf "${cyan_bold}%s${RST}\n" "$1"; }
colorwhite_bold() { printf "${white_bold}%s${RST}\n" "$1"; }
colordefault_bold() { printf "${default_bold}%s${RST}\n" "$1"; }

#EOF
