#!/bin/bash
set -e
source .env


if [[ -z $1 ]]; then
    echo -e "\nERROR: no search term argument!\n"
    exit 1
fi

find "$SOURCE_DATA_DIR" -iname "$1*"
