#!/usr/bin/env bash
set -e
THIS_FILE_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
source "$THIS_FILE_DIR/bash_lib/shared.sh"
source .env


SEARCH_STRING="$1"

print_deploy_step "Searching for '$SEARCH_STRING' in '$EPSTEIN_DOCS_DIR'..."
pushd "$EPSTEIN_DOCS_DIR"
egrep --color -i "$SEARCH_STRING" *.txt
popd


print_deploy_step "Searching for '$SEARCH_STRING' in '$EPSTEIN_DOJ_TXTS_20260130_DIR'..."
pushd "$EPSTEIN_DOJ_TXTS_20260130_DIR"
egrep --color -r -i "$SEARCH_STRING" .
popd
