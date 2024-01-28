#!/bin/bash

function build-and-run() {
    post_id=""
    command="bdv-run"
    while [ "${1:-}" != "" ]; do
        case $1 in
            -p| --post-id)
            shift
            if [ -z "$1" ]; then
                echo "a post-id was expected"
                exit 255
            fi
            command="bdv-run -p ${1}"
            ;;
        esac
        shift
    done
    
    docker start bdv && \
    docker exec bdv /bin/bash -c "source /app/pipeline.sh && ${command}" || { 
        docker build -t bdv-image . && \
        docker run --name bdv -it -d bdv-image && {
            echo "Creating container, you'll only have to do this the first time you run the script"
            wait_time=5
            while [ $wait_time -gt 0 ]; do
                echo "Waiting for container to be ready: ${wait_time}s left"
                sleep 1
                wait_time=$(expr $wait_time - 1)
            done
            docker exec bdv /bin/bash -c "source /app/pipeline.sh && ${command}"
        }
    }
    return
}

function copy-and-close() {
    last=`docker exec -it bdv /bin/bash -c "source /app/pipeline.sh && bdv-last-stored"`
    path="bdv:/app/editor/output/${last}"
    pathclean="$(echo "$path" | sed 's/\r$//' | tr -d '\n')";
    docker cp ${pathclean} editor/output
    docker stop bdv
    return
}

#check for flags
build_and_run=$"build-and-run"
while [ "${1:-}" != "" ]; do
    case $1 in
        -br| --build-and-run)
            build-and-run
            exit 0
            ;;
        -brp| --build-and-run-post)
            shift
            build-and-run -p $1
            exit 0
            ;;
        -cc| --copy-and-close)
            copy-and-close
            exit 0
            ;;
        -p| --post-id)
            shift
            build_and_run=$"build-and-run -p $1"
            ;;
        -h| --help)
            echo "Use -br| --build-and-run flag to only execute build and run function."
            echo "Use -brp [POST_ID]| --build-and-run-post [POST_ID] flag to only execute build and run function for an specific post id."
            echo "Use -cc| --copy-and-close flag to only execute copy-and-close function."
            echo "If no flag is provided it will run all functions"
            echo "Use -p [POST_ID]| --post-id [POST_ID] flag will run all fuinctions for the specific post id."
            exit 0
            ;;
    esac
    shift
done;

$build_and_run && copy-and-close || {
    echo "There was an issue with the script execution"
    exit 255
}