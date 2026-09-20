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

BUILD_DIR=${1:-docs/}
GENERATE_CMD="$GENERATE_CMD --build-dir $BUILD_DIR"
GENERATE_MOBILE_CMD="$GENERATE_MOBILE_CMD --build-dir $BUILD_DIR"
GENERATE_SIDE_PANELS_CMD="$GENERATE_CMD --side-panel-notes"

CATEGORIES=(
    crypto
    girls
    money
)


if [[ -z $SKIP_CHRONO ]]; then
    print_build_step "output-most-interesting"
    $GENERATE_SIDE_PANELS_CMD --output-most-interesting
    print_build_step "output-chrono"
    $GENERATE_SIDE_PANELS_CMD --output-chrono
    print_build_step "output-chrono mobile"
    $GENERATE_MOBILE_CMD --output-chrono
else
    print_deploy_step "Skipping chronological builds..."
fi

# Fast pages
print_build_step "output-notes"
$GENERATE_CMD --output-notes
print_build_step "output-bios"
$GENERATE_CMD --output-bios
print_deploy_step "Extracting email signatures" "output-devices"
$GENERATE_CMD --output-devices
print_build_step "all-texts"
$GENERATE_CMD --all-texts
print_build_step "output-word-count"
$GENERATE_CMD --output-word-count --width 125
print_build_step "json-metadata"
$GENERATE_CMD --json-metadata
print_build_step "output-notes"
$GENERATE_CMD --output-notes

# Skip big emails pages if ONLY_MOST_INTERESTING=true
if [ -n "$ONLY_MOST_INTERESTING" ]; then
    print_deploy_step "Skipping build of curated emails and all emails/all other files pages..."
else
    # Categories
    for category in "${CATEGORIES[@]}"; do
        print_deploy_step "Building category page" "$category"
        $GENERATE_SIDE_PANELS_CMD --category $category
    done

    print_deploy_step "Building other files table page" "all-other-files"
    $GENERATE_CMD --all-other-files
    print_build_step "output-curated"
    $GENERATE_SIDE_PANELS_CMD --output-curated
    print_build_step "output-curated mobile"
    $GENERATE_MOBILE_CMD --output-curated
    print_deploy_step "Building all emails page" "all-emailers"
    $GENERATE_CMD --all-emailers
    print_build_step "all-emails-chrono"
    $GENERATE_SIDE_PANELS_CMD --all-emails-chrono
fi

# Only build DOJ files site if TAG_RELEASE=true
if [ -n "$TAG_RELEASE" ]; then
    print_build_step "all-doj-files whole-file"
    $GENERATE_CMD --all-doj-files --whole-file
else
    print_deploy_step "Skipping DOJ files (TAG_RELEASE not set)..."
fi

print_deploy_step "Finished building all pages to '$BUILD_DIR'"
