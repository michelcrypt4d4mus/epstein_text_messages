#!/usr/bin/env bash
# Use --pickled arg to use pickled data file, otherwise pickled data will always be overwritten
#
#   - ONLY_CURATED=true to skip build/deploy of full emails site.
#   - ONLY_MOBILE=true for only mobile sites
#   - TAG_RELEASE=true to upload the pkl.gz file to the repo and deploy DOJ files site
set -e
source .env

THIS_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
REPO_SCRIPTS_DIR="$THIS_DIR/scripts"
source "$REPO_SCRIPTS_DIR/bash_lib/shared.sh"


# Preparation (check branch, clean build artifacts, etc.)
if [[ $CURRENT_BRANCH != "master" ]]; then
    clr_red "ERROR: Current branch is not master: ($CURRENT_BRANCH)"
    exit 1
elif any_uncommitted_changes; then
    clr_red "ERROR: Uncommitted changes"
    exit 1
fi

# Check for new files unless doing --overwrite-pickled
if [[ $PICKLE_ARG != "--overwrite-pickle" ]]; then
    print_deploy_step "Scanning for new files with extract_doj_pdfs.py..."
    ./scripts/extract_doj_pdfs.py
else
    print_deploy_step "Doing full file rescan..."
fi


# Push master changes and build emailers .png (with --overwrite-pickle if --pickled not used)
git push origin master --quiet
epstein_generate --make-clean --suppress-output
print_deploy_step "Building emailer info .png... $PICKLE_ARG"
$GENERATE_CMD --emailers-info $PICKLE_ARG

if [ -n "$TAG_RELEASE" ]; then
    print_deploy_step "Copying 'the_epstein_files.local.pkl.gz' to 'the_epstein_files.pkl.gz'..."
    scripts/validate_pkl.py
    cp ./the_epstein_files.local.pkl.gz ./the_epstein_files.pkl.gz
fi

# Commit if any changes
if any_uncommitted_changes; then
    git commit -am"Update .png"
    git push origin master --quiet
else
    print_msg "  No changes to emailers .png file..."
fi


# Switch to gh_pages branch and run build_pages.sh
git checkout gh_pages
git merge --no-edit master --quiet
"$REPO_SCRIPTS_DIR/build_pages.sh"

# Commit changes
copy_custom_html
commit_gh_pages_changes
print_deploy_step "Deployed URLs:"
epstein_generate --show-urls
git checkout master
