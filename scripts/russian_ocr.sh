#!/bin/bash
# Use tesseract to OCR mixed cyrillic/latin text from image.
set -e
source .env
source "$BASH_COLORS_PATH"

OUTPUT_DIR=source_data/russian_tesseract_output
mkdir -p "$OUTPUT_DIR"

if [[ -z "$1" ]]; then
    echo -e ""
    img_basename="$(ls -Art $SCREENSHOTS_DIR | tail -n 1)"
    echo -e "  $(clr_brownb warning) No argument provided, using most recent file in $(clr_green $SCREENSHOTS_DIR): $(clr_cyan "$img_basename"))\n"
    img_file="$SCREENSHOTS_DIR/$img_basename"
else
    img_file="$1"
fi


img_path=$(realpath "$img_file")
output_basename=$(basename "$img_path")
output_basename=${output_basename// /_}  # Replace space with underscore
output_prefix="$OUTPUT_DIR/$output_basename"
output_path="$output_prefix.txt"
tesseract -l eng+rus "$img_path" "$output_prefix"

echo -e "\n Russian OCR of: $(clr_cyan "$img_path")"
echo -e "  -> written to: $(clr_red "$output_path")\n"
open "$output_path"
