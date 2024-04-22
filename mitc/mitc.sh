#!/usr/bin/env bash

DOCKER_ROOT=$(dirname $0)
args=$@

mitc_is_up() {
    curl -q --fail-with-body http://127.0.0.1:3000/ >& /dev/null
}

mitc_build() {
    echo "building mitc image"
    $(cd $DOCKER_ROOT ; docker build -t registry2.omb.gov:mitc -f mitc.dockerfile .)
    echo "server image has been built"
}

mitc_down() {
    echo "stopping mitc test server"
    docker stop mitc
    echo "removing the mitc container"
    docker rm mitc
    echo "mitc has been stopped"
}

mitc_clean() {
    echo "removing the mitc container"
    docker rm mitc
    echo "mitc has been cleaned"
}

mitc_up() {
    echo "starting mitc test server"
    cd $DOCKER_ROOT
    docker run --detach --name mitc --publish 3000:3000 registry2.omb.gov:mitc
    if [ $? != 0 ]
    then
        echo " SERVER FAILED TO START"
        exit 1
    fi
    echo -n "waiting for server initialization"
    for i in {1..10}
    do
        if mitc_is_up;
        then
            echo "server is ready and listening on http://127.0.0.1:3000"
            return 0
        else
            echo -n "."
            sleep 1
        fi
    done
    echo " SERVER FAILED TO START"
    exit 1
}

case "$1" in
build)
    mitc_build
    ;;
start)
    if mitc_is_up;
    then
        echo "mitc is already up"
    else
        mitc_up
    fi
    ;;
stop)
    if mitc_is_up;
    then
        mitc_down
    else
        echo "mitc is already stopped"
    fi
    ;;
clean)
    if mitc_is_up;
    then
        mitc_down
    else
        mitc_clean
    fi
    ;;
status)
    if mitc_is_up;
    then
        echo "up"
        exit 0
    else
        echo "down"
        exit 1
    fi
    ;;
*)
    echo "Usage: $0 {start|stop|status|build}" >&2
    exit 1
    ;;
esac

exit 0
