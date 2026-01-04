#!/bin/bash
# Build a new pickle file and run pytest against it

./generate_html.py --build --suppress-output --overwrite-pickle
echo -e "\nDone building, launching pytest...\n\n"
PICKLED=true pytest
