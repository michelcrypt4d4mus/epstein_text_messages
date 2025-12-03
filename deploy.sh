#!/usr/bin/env bash
# Set ONLY_TEXTS=true to skip build/deploy of full emails site.
# Running 'bash -l' uses the login shell but then the poetry venv isn't set :(
source .env
set -e

EMAILS_DIR="../epstein_emails_house_oversight"
DOCS_DIR="docs"
INDEX_HTML_PATH="$DOCS_DIR/index.html"
WORD_COUNT_HTML_PATH="$DOCS_DIR/epstein_emails_word_count.html"
EMAILS_INDEX_HTML_PATH="${EMAILS_DIR}/${INDEX_HTML_PATH}"

GITHUB_PAGES_BASE_URL='https://michelcrypt4d4mus.github.io'
EMAILS_PROJECT_NAME=`basename "$EMAILS_DIR"`
TEXT_MSGS_PROJECT_NAME=`basename "$PWD"`
EMAILS_URL="$GITHUB_PAGES_BASE_URL/$EMAILS_PROJECT_NAME/"
TEXT_MSGS_URL="$GITHUB_PAGES_BASE_URL/$TEXT_MSGS_PROJECT_NAME/"

if [ -n "$BASH_COLORS_PATH" ]; then
    source "$BASH_COLORS_PATH"
    clr_cyan "Sourced '$(clr_green $BASH_COLORS_PATH)'..."
else
    echo -e "bash colors not found, can't print status msgs"
fi

print_msg() {
    local msg="$1"
    local colored_part="$2"

    if [ -n "$colored_part" ]; then
        msg="$msg '$(clr_green $colored_part)'"
    fi

    clr_cyan "$msg..."
}

any_uncommitted_changes() {
    if [[ $(git status --porcelain --untracked-files=no | wc -l) -eq 0 ]]; then
        return 1
    else
        return 0
    fi
}

remove_master_branch_file() {
    local master_file="$1"

    if [ -f "$master_file" ]; then
        print_msg "Removing master branch version of" "$master_file"
        rm "$master_file"
    fi
}


# Preparation / checking for issues
if any_uncommitted_changes; then
    print_msg "Uncommitted changes; halting"
    exit
fi

remove_master_branch_file "$INDEX_HTML_PATH"
remove_master_branch_file "$WORD_COUNT_HTML_PATH"


# Text messages
git push origin master --quiet
git checkout gh_pages
git merge --no-edit master --quiet

print_msg "Building" "$INDEX_HTML_PATH"
./generate.py --build --suppress-output
echo -e ""
print_msg "Building" "$WORD_COUNT_HTML_PATH"
./scripts/count_words.py --build --suppress-output

git commit -am"Update HTML"
git push origin gh_pages --quiet
git checkout master
print_msg "$TEXT_MSGS_PROJECT_NAME deployed to" "$TEXT_MSGS_URL"
echo -e "\n\n"

if [ -n "$ONLY_TEXTS" ]; then
    print_msg "Skipping deployment of emails site"
    exit
fi


# Deploy all emails
print_msg "Building all emails version of" "$INDEX_HTML_PATH"
./generate.py --all-emails --build --no-texts --suppress-output
print_msg "Copying '$INDEX_HTML_PATH' to '$EMAILS_INDEX_HTML_PATH'"
mv "$INDEX_HTML_PATH" "$EMAILS_INDEX_HTML_PATH"
pushd "$EMAILS_DIR" > /dev/null
git commit -am"Update HTML"
git push origin main --quiet
popd > /dev/null
print_msg "${EMAILS_PROJECT_NAME} deployed to" "$EMAILS_URL"
echo -e ""
