#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

ENV_PATH=".venv/bin/activate"

function bdv-fetch() {
    current=`pwd`
    post_id=""

    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post"
                return 2
                ;;
        esac
        shift
    done;

    cd "$parent_path"
    source $ENV_PATH
    python etl.py --local false --post-id "${post_id}" --force true &&\
    python multimedia.py --post-id "${post_id}" || {
        echo "There was an issue. exit code: ${?}"
        deactivate
        cd $current
        return $?
    }
    deactivate
    cd $current
}

function bdv-edit() {
    current=`pwd`
    post_id=""

    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post from db"
                return 2
                ;;
        esac
        shift
    done;

    cd "$parent_path"
    source $ENV_PATH
    echo $post_id
    python publish.py --post-id "${post_id}" || {
        echo "There was an issue. exit code: ${?}"
        deactivate
        cd $current
        return $?
    }
    deactivate
    cd $current
}

function bdv-run() {
    post_id=""

    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post"
                return 0
                ;;
        esac
        shift
    done;

    bdv-fetch -p "${post_id}" && bdv-edit -p "${post_id}" 
}