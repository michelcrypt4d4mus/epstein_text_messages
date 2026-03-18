# bash functions and variables shared by multiple scripts.
source .env

CURRENT_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
GENERATE_CMD='epstein_generate --build --suppress-output'
GENERATE_MOBILE_CMD="$GENERATE_CMD --mobile"
LIB_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
SCRIPT_DIR=$(realpath "$LIB_DIR/..")

echo -e "shared.sh LIB_DIR=$LIB_DIR, SCRIPT_DIR=$SCRIPT_DIR"

if [ -n "$BASH_COLORS_PATH" ]; then
    source "$BASH_COLORS_PATH"
    clr_cyan "Sourced '$(clr_green $BASH_COLORS_PATH)'..."
else
    echo -e "bash colors not found, can't print status msgs. BASH_COLORS_PATH=$BASH_COLORS_PATH"
    exit 1
fi


print_deploy_step() {
    echo -e ""
    clr_cyan "$1"
}

print_msg() {
    local msg="$1"
    local colored_part="$2"

    if [ -n "$colored_part" ]; then
        msg="$msg '$(clr_green $colored_part)'"
    fi

    clr_cyan "$msg"
}

# Running 'bash -l' uses the login shell but then the poetry venv isn't set :(
any_uncommitted_changes() {
    if [[ $(git status --porcelain --untracked-files=no | wc -l) -eq 0 ]]; then
        return 1
    else
        return 0
    fi
}

commit_gh_pages_changes() {
    echo -e ""
    print_deploy_step "Committing changes to gh_pages..."
    git commit -am"Update HTML"
    git push origin gh_pages --quiet
}

copy_custom_html() {
    print_deploy_step "Copying custom HTML pages into place..."
    epstein_generate --use-custom-html
}
