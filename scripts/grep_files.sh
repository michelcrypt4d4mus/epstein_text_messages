#!/usr/bin/env bash
source .env


SEARCH_STRING="$1"


echo -e "Searching for '$SEARCH_STRING' in '$EPSTEIN_DOCS_DIR'..."
pushd "$EPSTEIN_DOCS_DIR"
egrep --color -i "$SEARCH_STRING" *.txt
popd


echo -e "Searching for '$SEARCH_STRING' in '$EPSTEIN_DOJ_TXTS_20260130_DIR'..."
pushd "$EPSTEIN_DOJ_TXTS_20260130_DIR"
egrep --color -r -i "$SEARCH_STRING" .
popd
