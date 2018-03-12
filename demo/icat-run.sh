#! /bin/sh

network=icat-test.local

if ! docker network inspect $network > /dev/null 2>&1
then
    docker network create --driver bridge $network
fi

docker run -d --rm --name mysql -h mysql.$network --network=$network \
    local/icat-mariadb

docker run -d --rm --name icat -h icat.$network --network=$network \
    local/icat-icat

