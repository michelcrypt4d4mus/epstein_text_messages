#!/bin/bash
set -e

git merge --no-edit master --quiet
git merge master
