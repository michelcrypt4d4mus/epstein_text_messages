#!/usr/bin/env bash
# Use --pickled arg to use pickled data file, otherwise pickled data will always be overwritten
# Set ONLY_TEXTS=true to skip build/deploy of full emails site.
set -e
source .env

GENERATE_CMD='epstein_generate --build --suppress-output'
CURRENT_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
PICKLE_ARG=$([[ $1 == '--pickled' ]] && echo "" || echo "--overwrite-pickle")
URLS_ENV=.urls.env

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


# Preparation (check branch, clean build artifacts, etc.)
if [[ $CURRENT_BRANCH != "master" ]]; then
    clr_red "ERROR: Current branch is not master: ($CURRENT_BRANCH)"
    exit 1
elif any_uncommitted_changes; then
    clr_red "ERROR: Uncommitted changes"
    exit 1
fi

# Build .png and push master changes
epstein_generate --make-clean --suppress-output
print_deploy_step "Building emailer info .png..."
$GENERATE_CMD --emailers-info

if any_uncommitted_changes; then
    git commit -am"Update .png"
    git push origin master --quiet
fi

# Switch to gh_pages branch
git checkout gh_pages
git merge --no-edit master --quiet

# Build files
print_deploy_step "Building text messages page... $PICKLE_ARG"
$GENERATE_CMD $PICKLE_ARG

if [ -n "$ONLY_TEXTS" ]; then
    print_deploy_step "Skipping build of emails pages..."
else
    print_deploy_step "Building all emails page..."
    $GENERATE_CMD --all-emails --all-other-files
    print_deploy_step "Building chronological emails page..."
    $GENERATE_CMD --email-timeline
fi

print_deploy_step "Building word counts page..."
epstein_word_count --build --suppress-output --width 125
print_deploy_step "Building JSON metadata page..."
$GENERATE_CMD --json-metadata
print_deploy_step "Building JSON files data..."
$GENERATE_CMD --json-files

# Commit changes
echo -e ""
git commit -am"Update HTML"
git push origin gh_pages --quiet
git checkout master

source $URLS_ENV
echo -e ""
print_msg "                texts URL:" "$TEXT_MSGS_URL"
print_msg "               emails URL:" "$ALL_EMAILS_URL"
print_msg " chronological emails URL:" "$CHRONOLOGICAL_EMAILS_URL"
print_msg "          word counts URL:" "$WORD_COUNT_URL"
print_msg "        json metadata URL:" "$JSON_METADATA_URL"
print_msg "           json files URL:" "$JSON_FILES_URL"
echo -e "\n\n"
