#!/bin/bash
set -e

INDEX_HTML_PATH="docs/index.html"

if any_uncommitted_changes; then
    echo "Uncommitted changes; halting."
    exit
fi

if [ -f "$INDEX_HTML_PATH" ]; then
    echo "Removing '$INDEX_HTML_PATH' on master..."
    rm "$INDEX_HTML_PATH"
fi

git checkout gh_pages
git merge --no-edit master
./epstein_chat_logs_reformatter.py --build
git commit -am"Update HTML"
git push origin gh_pages
git checkout master
