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
    
    docker build -t bdv-image . && \
    docker run -d bdv-image /bin/bash -c "source /app/pipeline.sh && ${command} && tail -f /dev/null"
    return
}

function see-logs() {
    id=(`docker ps | grep bdv-image`)
    id=${id[0]}
    docker logs -f $id
    return
}

function copy-and-close() {
    id=(`docker ps | grep bdv-image`)
    id=${id[0]}
    last=`docker exec -it ${id} /bin/bash -c "source /app/pipeline.sh && bdv-last-stored"`
    path="${id}:/app/editor/output/${last}"
    pathclean="$(echo "$path" | sed 's/\r$//' | tr -d '\n')";
    docker cp ${pathclean} editor/output
    docker stop $id
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
        -sl| --see-logs)
            see-logs
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
            echo "Use -sl| --see-logs flag to only execute see logs function."
            echo "Use -cc| --copy-and-close flag to only execute copy-and-close function."
            echo "If no flag is provided it will run all functions"
            exit 0
            ;;
    esac
    shift
done;

$build_and_run || {
    echo "There was an issue with building or running the container"
    exit 255
}
see-logs
copy-and-close
