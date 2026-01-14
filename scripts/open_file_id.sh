#!/bin/bash
# Open file ID in a web browser.

BASE_URL="https://epstein.media/files/house_oversight_"
FILE_ID="${1#HOUSE_OVERSIGHT_}"
FILE_URL="${BASE_URL}${FILE_ID}"

echo -e "Opening URL '$FILE_URL'..."
open "$FILE_URL"
