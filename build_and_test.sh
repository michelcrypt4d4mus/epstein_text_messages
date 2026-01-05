#!/bin/bash
# Build a new pickle file and run pytest against it

epstein_generate --build --suppress-output --overwrite-pickle
echo -e "\nDone building, launching pytest...\n\n"
PICKLED=true pytest
