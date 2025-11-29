#!/usr/bin/env bash
# Running 'bash -l' uses the login shell but then the poetry venv isn't set :(
set -e

EMAILS_DIR="../epstein_emails_house_oversight"
INDEX_HTML_PATH="docs/index.html"
EMAILS_INDEX_HTML_PATH="${EMAILS_DIR}/${INDEX_HTML_PATH}"

GITHUB_PAGES_BASE_URL='https://michelcrypt4d4mus.github.io'
EMAILS_PROJECT_NAME=`basename "$EMAILS_DIR"`
TEXT_MSGS_PROJECT_NAME=`basename "$PWD"`
EMAILS_URL="$GITHUB_PAGES_BASE_URL/$EMAILS_PROJECT_NAME/"
TEXT_MSGS_URL="$GITHUB_PAGES_BASE_URL/$TEXT_MSGS_PROJECT_NAME/"


any_uncommitted_changes() {
    if [[ $(git status --porcelain --untracked-files=no | wc -l) -eq 0 ]]; then
        return 1
    else
        return 0
    fi
}

if any_uncommitted_changes; then
    echo "Uncommitted changes; halting."
    exit
fi

git push origin master

if [ -f "$INDEX_HTML_PATH" ]; then
    echo -e "Removing '$INDEX_HTML_PATH' on master..."
    rm "$INDEX_HTML_PATH"
fi

git checkout gh_pages
git merge --no-edit master
echo -e "Building '$INDEX_HTML_PATH'..."
./epstein_chat_logs_reformatter.py --build
git commit -am"Update HTML"
git push origin gh_pages
git checkout master
echo -e "\n\n$TEXT_MSGS_PROJECT_NAME deploy complete: $EMAILS_URL\n"

if [ -n "$ONLY_TEXTS" ]; then
    echo "Skipping deployment of emails site..."
    exit
fi


# Deploy all emails
echo -e "Deploying '$EMAILS_PROJECT_NAME'..."
echo -e "\nBuilding all emails..."
./epstein_chat_logs_reformatter.py --all --build --no-texts
echo "Copying '$INDEX_HTML_PATH' to '$EMAILS_INDEX_HTML_PATH'..."
mv "$INDEX_HTML_PATH" "$EMAILS_INDEX_HTML_PATH"
pushd "$EMAILS_DIR"
git commit -am"Update HTML"
git push origin main
popd
echo -e "\n${EMAILS_PROJECT_NAME} deploy complete: $EMAILS_URL"
