#!/usr/bin/env bash
# Use --pickled arg to use pickled data file, otherwise pickled data will always be overwritten
#
#   - ONLY_CURATED=true to skip build/deploy of full emails site.
#   - ONLY_MOBILE=true for only mobile sites
#   - TAG_RELEASE=true to deploy DOJ files site and upload the pkl.gz file to the repo
set -e
source .env

THIS_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
REPO_SCRIPTS_DIR="$THIS_DIR/scripts"
EXTRACT_DOJ_PDFS_PATH="$REPO_SCRIPTS_DIR/extract_doj_pdfs.py"
PICKLE_ARG=$([[ $1 == '--pickled' ]] && echo "" || echo "--overwrite-pickle")
source "$REPO_SCRIPTS_DIR/bash_lib/shared.sh"


if any_uncommitted_changes; then
    exit 1
fi

# Check for new files unless doing --overwrite-pickled
if [[ $PICKLE_ARG != "--overwrite-pickle" ]]; then
    print_deploy_step "Scanning for new files with" "$EXTRACT_DOJ_PDFS_PATH"
    $EXTRACT_DOJ_PDFS_PATH
else
    print_deploy_step "Doing full file rescan"
fi


# Push master changes and build emailers .png (with --overwrite-pickle if --pickled not used)
git push origin master --quiet
epstein_generate --make-clean --suppress-output
print_deploy_step "Building emailer info .png" "$PICKLE_ARG"
$GENERATE_CMD --emailers-info $PICKLE_ARG

if [ -n "$TAG_RELEASE" ]; then
    export TAG_RELEASE
    print_deploy_step "Copying 'the_epstein_files.local.pkl.gz' to 'the_epstein_files.pkl.gz'..."
    scripts/validate_pkl.py
    cp ./the_epstein_files.local.pkl.gz ./the_epstein_files.pkl.gz
fi

# Commit if any changes
if any_uncommitted_changes; then
    git commit -am"Update .png"
    git push origin master --quiet
else
    print_warning "  No changes to emailers .png file..."
fi


# Switch to gh_pages branch and run build_pages.sh
git checkout $GH_PAGES_BRANCH
git merge --no-edit master --quiet

export ONLY_CURATED
export ONLY_MOBILE
export SKIP_CHRONO
export TAG_RELEASE
"$REPO_SCRIPTS_DIR/build_pages.sh"

# Commit changes
copy_custom_html
commit_gh_pages_changes
print_deploy_step "Deployed URLs:"
epstein_generate --show-urls
git checkout master
