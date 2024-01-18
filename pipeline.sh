#!/bin/bash
set +e #Disable automatic exit on error
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

#Path of the environm,ent to use
ENV_PATH=".venv/bin/activate"
#Manual status codes initialization for sourced commands
EXIT_STATUS_FETCH=0
EXIT_STATUS_EDIT=0

function bdv-fetch() {
    #initialize params
    current=`pwd`
    post_id=""

    #check for flags
    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post"
                EXIT_STATUS_FETCH=2
                return
                ;;
        esac
        shift
    done;

    #Move to parent path and activate environment
    cd "$parent_path"
    source $ENV_PATH

    #Run etl script and if it succeeds run the multimedia script
    #On error deactivate the environment and move back to original directory with the manual status code modified
    python etl.py --local false --post-id "${post_id}" --force true &&\
    python multimedia.py --post-id "${post_id}" || {
        echo "There was an issue. exit code: ${?}"
        deactivate
        cd $current
        EXIT_STATUS_FETCH=$?
        return
    }
    #On success deactivate environment and move back to original directory
    deactivate
    cd $current
}

function bdv-edit() {
    #Initialize params
    current=`pwd`
    post_id=""

    #check for flags
    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post from db"
                EXIT_STATUS_EDIT=2
                return
                ;;
        esac
        shift
    done;

    #Move to parent path and activate environment
    cd "$parent_path"
    source $ENV_PATH

    #Run publish script and on error deactivate the environment and move back to original directory with the manual status code modified
    echo $post_id
    python publish.py --post-id "${post_id}" || {
        echo "There was an issue. exit code: ${?}"
        deactivate
        cd $current
        EXIT_STATUS_EDIT=$?
        return
    }
    #On success deactivate environment and move back to original directory
    deactivate
    cd $current
}

function bdv-run() {
    #Initialize params
    post_id=""

    #check for flags
    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
                shift
                post_id=$1
                ;;
            -h| --help)
                echo "Use -p| --post-id flag to provide a post id."
                echo "If no post id provided it will fetch the latest post"
                return
                ;;
        esac
        shift
    done;
    #run fetch script and check the manual exit code
    bdv-fetch -p "${post_id}" 
    if [ $EXIT_STATUS_FETCH -eq 0 ]; then
        #if manual exit code is 0, run edit script
        bdv-edit -p "${post_id}"
    fi
}

function bdv-last-stored() {
    files=(`ls -lt editor/output/ | head -n 2 | tail -n 1`)
    amount=${#files[@]}
    echo ${files[amount-1]}
    return 0
}