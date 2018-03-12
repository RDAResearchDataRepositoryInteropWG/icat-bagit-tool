#! /bin/sh

network=icat-test.local

docker kill mysql icat
docker network rm $network
