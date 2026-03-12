#!/bin/bash
# Use tesseract to OCR mixed cyrillic/latin text from image.
set -e
source .env
source "$BASH_COLORS_PATH"

OUTPUT_DIR=$SOURCE_DATA_DIR/russian_tesseract_output
TESSERACT_CMD="tesseract -l eng+rus"

mkdir -p "$PDF_TO_IMAGE_DIR"
mkdir -p "$OUTPUT_DIR"
echo -e ""


export_pdf_to_images() {
    local pdf_path="$1"
    local output_prefix="$2"
    local txt_output_path="$OUTPUT_DIR/$(underscored_basename "$pdf_path").txt"

    echo -e "\nRunning $(clr_green "pdftoppm -png '$pdf_path' '$output_prefix'")"
    pdftoppm -png "$pdf_path" "$output_prefix"

    echo -e "\nRunning tesseract on exported PNGs..."
    for i in $output_prefix* ; do $TESSERACT_CMD "$i" stdout >> "$txt_output_path";  done;
    cat "$txt_output_path"
}

# print the file's basename with underscores replacing spaces
underscored_basename() {
    local file_basename=$(basename "$1")
    echo "${file_basename// /_}"   # Replace space with underscore
}


if [[ -z "$1" ]]; then
    img_basename="$(ls -Art $SCREENSHOTS_DIR | tail -n 1)"
    echo -e "  $(clr_brownb warning) No argument provided, using most recent file in $(clr_green $SCREENSHOTS_DIR): $(clr_cyan "$img_basename"))\n"
    img_file="$SCREENSHOTS_DIR/$img_basename"
elif [[ "$1" =~ .(jpe?g|png)$ ]]; then
    echo -e "  Image detected, running tesseract directly on file..."
    img_file="$1"
elif [[ "$1" =~ .pdf$ ]]; then
    echo -e "  PDF detected, exporting to images first..."
    output_prefix="$PDF_TO_IMAGE_DIR/$(underscored_basename "$1")"
    export_pdf_to_images "$1" "$output_prefix"
    exit
fi


img_path=$(realpath "$img_file")
output_basename=$(underscored_basename "$img_path")
output_prefix="$OUTPUT_DIR/$output_basename"
output_path="$output_prefix.txt"
tesseract -l eng+rus "$img_path" "$output_prefix"

echo -e "\n Russian OCR of: $(clr_cyan "$img_path")"
echo -e "  -> written to: $(clr_red "$output_path")\n"
open "$output_path"
