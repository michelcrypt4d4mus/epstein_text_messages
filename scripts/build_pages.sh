#!/bin/bash
# Build the various HTML pages. First argument is the --build-dir (if provided).
#
# Env var options:
#   - ONLY_MOST_INTERESTING=true to skip build/deploy of full emails site
#   - SKIP_CHRONO=true to skip chrono builds
#   - TAG_RELEASE=true to deploy DOJ files site
set -e
THIS_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
source "$THIS_DIR/bash_lib/shared.sh"

CATEGORIES=(
    crypto
    girls
    money
)

BUILD_DIR=${1:-docs/}
GENERATE_CMD="$GENERATE_CMD --build-dir $BUILD_DIR"
GENERATE_SIDE_PANELS_CMD="$GENERATE_CMD --side-panel-notes"
print_deploy_step "Building pages to BUILD_DIR '$BUILD_DIR'"


if [[ -z $SKIP_CHRONO ]]; then
    print_deploy_step "Building most interesting page with $GENERATE_SIDE_PANELS_CMD --output-most-interesting"
    $GENERATE_SIDE_PANELS_CMD --output-most-interesting
    print_deploy_step "Building curated chronological page with '$GENERATE_SIDE_PANELS_CMD'"
    $GENERATE_SIDE_PANELS_CMD --output-chrono
    print_deploy_step "Building curated chronological mobile page..."
    $GENERATE_MOBILE_CMD --output-chrono
else
    print_deploy_step "Skipping chronological builds..."
fi

# Fast pages
print_deploy_step "Building notes pages..."
$GENERATE_CMD --output-notes
print_deploy_step "Building biographies page..."
$GENERATE_CMD --output-bios
print_deploy_step "Building email signatures page..."
$GENERATE_CMD --output-devices
print_deploy_step "Building text messages page..."
$GENERATE_CMD --all-texts
print_deploy_step "Building word counts page..."
$GENERATE_CMD --output-word-count --width 125
print_deploy_step "Building JSON metadata page..."
$GENERATE_CMD --json-metadata
print_deploy_step "Building --output-notes..."
$GENERATE_CMD --output-notes

# Skip big emails pages if ONLY_MOST_INTERESTING=true
if [ -n "$ONLY_MOST_INTERESTING" ]; then
    print_deploy_step "Skipping build of curated emails and all emails/all other files pages..."
else
    # Categories
    for category in "${CATEGORIES[@]}"; do
        print_deploy_step "Building category $category page..."
        $GENERATE_SIDE_PANELS_CMD --category $category
    done

    print_deploy_step "Building other files table page..."
    $GENERATE_CMD --all-other-files
    print_deploy_step "Building curated page..."
    $GENERATE_CMD
    print_deploy_step "Building curated mobile page... "
    $GENERATE_MOBILE_CMD
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
