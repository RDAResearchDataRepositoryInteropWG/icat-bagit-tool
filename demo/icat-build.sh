#! /bin/sh

maindir=$(cd $(dirname $0); pwd)

docker build -t local/icat-mariadb $maindir/docker/mariadb
docker build -t local/icat-icat $maindir/docker/icat
docker build -t local/icat-client $maindir/docker/client
