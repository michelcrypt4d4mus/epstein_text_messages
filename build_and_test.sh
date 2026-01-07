#!/bin/bash
# Build a new pickle file and run pytest against it
set -e

epstein_generate --suppress-output --overwrite-pickle
echo -e "\nDone building, launching pytest...\n\n"
PICKLED=true pytest
