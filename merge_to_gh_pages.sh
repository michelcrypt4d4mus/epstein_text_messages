#!/bin/bash
set -e

git checkout gh_pages
git merge --no-edit master --quiet
