#!/bin/bash
set -e

if any_uncommitted_changes; then
    echo "Uncommitted changes; halting."
    exit
fi

git checkout gh_pages
git merge master
BUILD=true ./epstein_chat_logs_reformatter.py
git commit -am"Update HTML"
git push origin gh_pages
git checkout master
