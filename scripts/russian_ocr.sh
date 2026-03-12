#!/bin/bash
# Use tesseract to OCR mixed cyrillic/latin text from image.
set -e
source .env
source "$BASH_COLORS_PATH"

OUTPUT_DIR=source_data/russian_tesseract_output
mkdir -p "$OUTPUT_DIR"


img_path=$(realpath "$1")
output_basename=$(basename "$img_path")
output_basename=${output_basename// /_}  # Replace space with underscore
output_path="$OUTPUT_DIR/$output_basename"
tesseract -l eng+rus "$img_path" "$output_path"

echo -e "\n Russian OCR of: $(clr_cyan "$1")"
echo -e "  -> written to: $(clr_red "$output_path")\n"
