#!/usr/bin/env bash
# Use --pickled arg to use pickled data file, otherwise pickled data will always be overwritten
#
#   - ONLY_MOBILE=true for only mobile sites
#   - ONLY_CURATED=true to skip build/deploy of full emails site.
#   - TAG_RELEASE=true to upload the pkl.gz file to the repo and deploy DOJ files site
set -e
source .env

SCRIPT_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
echo -e "SCRIPT_DIR=$SCRIPT_DIR"
exit

CURRENT_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
PICKLE_ARG=$([[ $1 == '--pickled' ]] && echo "" || echo "--overwrite-pickle")
GENERATE_CMD='epstein_generate --build --suppress-output'
GENERATE_MOBILE_CMD="$GENERATE_CMD --mobile"

if [ -n "$BASH_COLORS_PATH" ]; then
    source "$BASH_COLORS_PATH"
    clr_cyan "Sourced '$(clr_green $BASH_COLORS_PATH)'..."
else
    echo -e "bash colors not found, can't print status msgs. BASH_COLORS_PATH=$BASH_COLORS_PATH"
    exit 1
fi


print_deploy_step() {
    echo -e ""
    clr_cyan "$1"
}

print_msg() {
    local msg="$1"
    local colored_part="$2"

    if [ -n "$colored_part" ]; then
        msg="$msg '$(clr_green $colored_part)'"
    fi

    clr_cyan "$msg"
}

# Running 'bash -l' uses the login shell but then the poetry venv isn't set :(
any_uncommitted_changes() {
    if [[ $(git status --porcelain --untracked-files=no | wc -l) -eq 0 ]]; then
        return 1
    else
        return 0
    fi
}

commit_gh_pages_changes() {
    echo -e ""
    print_deploy_step "Committing changes to gh_pages..."
    git commit -am"Update HTML"
    git push origin gh_pages --quiet
}

copy_custom_html() {
    print_deploy_step "Copying custom HTML pages into place..."
    epstein_generate --use-custom-html
}


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


# Switch to gh_pages branch
git checkout gh_pages
git merge --no-edit master --quiet

# Build pages
print_deploy_step "Building curated chronological page..."
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

if [ -n "$ONLY_MOBILE" ]; then
    commit_gh_pages_changes
    print_deploy_step "ONLY_MOBILE in effect, exiting after building mobile pages..."
    copy_custom_html
    exit
fi

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


# Commit changes
copy_custom_html
commit_gh_pages_changes
print_deploy_step "Deployed URLs:"
epstein_generate --show-urls
git checkout master
