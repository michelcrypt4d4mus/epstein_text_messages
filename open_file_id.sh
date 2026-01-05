#!/bin/bash
# Open a file in a web browser.

BASE_URL="https://epstein.media/files/house_oversight_"
FILE_URL="$BASE_URL$1"

echo -e "Opening URL '$FILE_URL'..."
open "$FILE_URL"
