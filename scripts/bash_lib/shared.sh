# bash functions and variables shared by multiple scripts.
source .env
LIB_DIR=$(dirname -- "$(readlink -f -- "$0";)";)
SCRIPT_DIR=$(realpath "$LIB_DIR/..")

CURRENT_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
GH_PAGES_BRANCH=gh_pages
GENERATE_CMD='epstein_generate --build --suppress-output'
GENERATE_MOBILE_CMD="$GENERATE_CMD --mobile"


if [ -n "$BASH_COLORS_PATH" ]; then
    source "$BASH_COLORS_PATH"
    clr_cyan "Sourced '$(clr_green $BASH_COLORS_PATH)'..."
    ERROR_PFX="$(clr_black clr_redb clr_bold ERROR):"
    WARNING_PFX="$(clr_black clr_brownb clr_bold WARNING):"
else
    echo -e "bash colors not found, can't print status msgs. BASH_COLORS_PATH=$BASH_COLORS_PATH"
    exit 1
fi


print_error() {
    echo -e "\n    $ERROR_PFX $(clr_cyan "$1") $(clr_magenta "$2")\n"
}

print_warning() {
    echo -e "\n    $WARNING_PFX $(clr_cyan "$1") $(clr_magenta "$2")\n"
}


# Running 'bash -l' uses the login shell but then the poetry venv isn't set :(
any_uncommitted_changes() {
    if [[ $(git status --porcelain --untracked-files=no | wc -l) -eq 0 ]]; then
        return 1
    else
        print_error "Uncommitted changes on branch" $CURRENT_BRANCH
        return 0
    fi
}


commit_gh_pages_changes() {
    echo -e ""
    print_deploy_step "Committing changes to" $GH_PAGES_BRANCH
    git commit -am"Update HTML"
    git push origin $GH_PAGES_BRANCH --quiet
}


copy_custom_html() {
    print_deploy_step "Copying custom HTML pages into place..."
    epstein_generate --use-custom-html
}


# Ensure we're on the master branch with no uncommitted changes
ensure_safe_branch() {
    if [[ $CURRENT_BRANCH != "master" ]]; then
        clr_red "ERROR: Current branch is not master: ($CURRENT_BRANCH)"
        exit 1
    elif any_uncommitted_changes; then
        clr_red "ERROR: Uncommitted changes"
        exit 1
    fi
}


print_deploy_step() {
    local msg="$(clr_cyan "$1")"

    if [[ -n "$2" ]]; then
        msg="$msg '$(clr_green $2)'"
    fi

    echo -e "\n$msg..."
}
