#!/bin/bash
set -e

git checkout gh_pages
git merge master --no-edit
git checkout master
git diff gh_pages -- . ':(exclude)docs/*.html' ':(exclude)docs/*.json' ':(exclude)docs/*.txt'
