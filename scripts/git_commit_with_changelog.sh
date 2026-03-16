#!/bin/bash
# Commit to git and also write the commit message to CHANGELOG.md
set -e

CHANGELOG=CHANGELOG.md
CHANGELOG_TMP=$CHANGELOG.tmp


commit_msg="$1"

if [[ -z $commit_msg ]]; then
    echo -e "\nERROR: no commit message provided!\n"
    exit 1
fi

head -1 $CHANGELOG > $CHANGELOG_TMP
echo "* $commit_msg" >> $CHANGELOG_TMP
tail -n +2 $CHANGELOG >> $CHANGELOG_TMP
mv $CHANGELOG_TMP $CHANGELOG
git commit -am"$commit_msg"

echo -e "\n  (Updating CHANGLOG.md)\n"
