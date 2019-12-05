#!/bin/sh

set -e

# Usage:
#    /entrypoint.sh web
#    /entrypoint.sh api
#    /entrypoint.sh any-command

# originally we use $PORT, we should keep compability with old deployment
API_PORT=${API_PORT:-8000}
WEB_PORT=${WEB_PORT:-80}
API_URL=${API_URL:-127.0.0.1:${API_PORT}}

run_web() {
    # https://github.com/jwilder/nginx-proxy/blob/master/docker-entrypoint.sh#L22
    local RESOLVERS=$(awk '$1 == "nameserver" {print ($2 ~ ":")? "["$2"]": $2}' ORS=' ' /etc/resolv.conf | sed 's/ *$//g')
    sed -i "s@{{RESOLVERS}}@${RESOLVERS}@g" /etc/nginx/conf.d/default.conf
    sed -i "s@{{WEB_PORT}}@${WEB_PORT:-80}@g;s@{{API_URL}}@${API_URL}@g" /etc/nginx/conf.d/default.conf

    exec nginx -g "daemon off;"
}

run_api() {
    python3 manage.py migrate
    exec gunicorn \
        --bind=0.0.0.0:${API_PORT} \
        --workers=4 \
        --name="CARDPC" \
        nsproject.wsgi
}

help() {
    echo "Usage:"
    echo "    docker run ... web         # start frontend (and http entrypoint)"
    echo "    docker run ... api         # start django server"
    echo "    docker run ... any-command # run specified command in the container"
}

if test -z "$1"; then
    help
    exit 1
fi

case "$1" in
    web)
        run_web
        ;;
    api)
        run_api
        ;;
    *)
        exec "$@"
        ;;
esac
