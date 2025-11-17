#!/bin/bash
set -e

if any_uncommitted_changes; then
    echo "Uncommitted changes; halting."
    exit
fi

# ./extract_text.sh
git commit -am"Update HTML"
git checkout gh_pages
git merge master
git push origin gh_pages
git checkout master
