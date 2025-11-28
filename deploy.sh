#!/bin/bash
set -e

INDEX_HTML_PATH="docs/index.html"
EMAILS_DIR="../epstein_emails_house_oversight"
EMAILS_INDEX_HTML_PATH="${EMAILS_DIR}/${INDEX_HTML_PATH}"


if any_uncommitted_changes; then
    echo "Uncommitted changes; halting."
    exit
fi

git push origin master

if [ -f "$INDEX_HTML_PATH" ]; then
    echo "Removing '$INDEX_HTML_PATH' on master..."
    rm "$INDEX_HTML_PATH"
fi

git checkout gh_pages
git merge --no-edit master
echo -e "Building '$INDEX_HTML_PATH'..."
./epstein_chat_logs_reformatter.py --build
git commit -am"Update HTML"
git push origin gh_pages
git checkout master
echo -e "\n\nepstein_text_messages deploy complete.\n"

if [ -n "$ONLY_TEXTS" ]; then
    echo "Skipping deployment of emails site..."
    exit(0)
fi


echo -e "Deploying '$EMAILS_DIR'..."

# Deploy emails
echo -e "\nBuilding all emails..."
./epstein_chat_logs_reformatter.py --build --all --no-texts
echo "Copying '$INDEX_HTML_PATH' to '$EMAILS_INDEX_HTML_PATH'..."
mv "$INDEX_HTML_PATH" "$EMAILS_INDEX_HTML_PATH"
pushd "$EMAILS_DIR"
git commit -am"Update HTML"
git push origin main
popd

echo -e "\n${EMAILS_DIR} deploy complete."
