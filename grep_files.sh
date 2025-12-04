#!/usr/bin/env bash
source .env

SEARCH_STRING="$1"

echo -e "Searching for '$SEARCH_STRING' in '$EPSTEIN_DOCS_DIR'..."
pushd "$EPSTEIN_DOCS_DIR"
egrep --color -i "$SEARCH_STRING" *.txt
popd
