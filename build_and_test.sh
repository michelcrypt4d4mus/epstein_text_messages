#!/bin/bash
# Build a new pickle file and run pytest against it
set -e

epstein_generate --output-other --suppress-output --overwrite-pickle
echo -e "\nDone building, launching pytest...\n\n"
PICKLED=true pytest
