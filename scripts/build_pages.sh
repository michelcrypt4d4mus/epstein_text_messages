#!/bin/bash
# Build the various HTML pages to a temp dir.
set -e

THIS_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
source "$THIS_DIR/bash_lib/shared.sh"

BUILD_DIR=docs/tmp
GENERATE_CMD="$GENERATE_CMD --build-dir $BUILD_DIR"


# Build pages
print_deploy_step "Building curated chronological page with '$GENERATE_CMD'..."
$GENERATE_CMD --output-chrono
print_deploy_step "Building curated chronological mobile page..."
$GENERATE_MOBILE_CMD --output-chrono

# Fast pages
print_deploy_step "Building email signatures page..."
$GENERATE_CMD --output-bios
print_deploy_step "Building email signatures page..."
$GENERATE_CMD --output-devices
print_deploy_step "Building text messages page... "
$GENERATE_CMD --all-texts
print_deploy_step "Building word counts page..."
$GENERATE_CMD --output-word-count --width 125
print_deploy_step "Building JSON metadata page..."
$GENERATE_CMD --json-metadata
print_deploy_step "Building other files table page..."
$GENERATE_CMD --all-other-files

# Slower pages
print_deploy_step "Building curated page..."
$GENERATE_CMD
print_deploy_step "Building curated mobile page... "
$GENERATE_MOBILE_CMD

# Skip big emails pages in ONLY_CURATED=true
if [ -n "$ONLY_CURATED" ]; then
    print_deploy_step "Skipping build of emails pages..."
else
    print_deploy_step "Building all emails page..."
    $GENERATE_CMD --all-emails
    print_deploy_step "Building emails chronological page..."
    $GENERATE_CMD --all-emails-chrono
fi

# Only build DOJ files site if TAG_RELEASE=true
if [ -n "$TAG_RELEASE" ]; then
    print_deploy_step "Building DOJ 2026 files..."
    $GENERATE_CMD --all-doj-files --whole-file
else
    print_deploy_step "Skipping DOJ files (TAG_RELEASE not set)..."
fi

print_deploy_step "Finished building all pages to '$BUILD_DIR'"
