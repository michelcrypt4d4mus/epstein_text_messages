#!/usr/bin/env bash
# Use --pickled arg to use pickled data file, otherwise pickled data will always be overwritten
# Set ONLY_TEXTS=true to skip build/deploy of full emails site.

source .env
set -e

CURRENT_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
PICKLE_ARG=$([[ $1 == '--pickled' ]] && echo "" || echo "--overwrite-pickle")
URLS_ENV=.urls.env

if [ -n "$BASH_COLORS_PATH" ]; then
    source "$BASH_COLORS_PATH"
    clr_cyan "Sourced '$(clr_green $BASH_COLORS_PATH)'..."
else
    echo -e "bash colors not found, can't print status msgs"
    exit 1
fi

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

# Push changes, switch to gh_pages branch
epstein_generate --make-clean
git push origin master --quiet
git checkout gh_pages
git merge --no-edit master --quiet

# Build files
echo -e ""
print_msg "Building text messages page $PICKLE_ARG"
epstein_generate --build --suppress-output $PICKLE_ARG

if [ -n "$ONLY_TEXTS" ]; then
    print_msg "Skipping build of emails page..."
else
    echo -e ""
    print_msg "Building all emails page..."
    epstein_generate --build --all-emails --all-other-files --suppress-output
fi

echo -e ""
print_msg "Building word counts page..."
./scripts/count_words.py --build --suppress-output --width 125
echo -e ""
print_msg "Building JSON metadata page..."
epstein_generate --build --json-metadata

# Commit changes
git commit -am"Update HTML"
git push origin gh_pages --quiet
git checkout master

epstein_dump_urls --suppress-output
source $URLS_ENV
echo -e ""
print_msg "             texts page" "$TEXT_MSGS_URL"
print_msg "            emails page" "$ALL_EMAILS_URL"
print_msg "       word counts page" "$WORD_COUNT_URL"
print_msg "     json metadata page" "$JSON_METADATA_URL"
echo -e "\n\n"
