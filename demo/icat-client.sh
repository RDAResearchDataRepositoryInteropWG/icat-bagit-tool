#! /bin/sh

network=icat-test.local

extdir=`mktemp -d -p /var/tmp icat-client.XXXXXX`
chown 1000:100 $extdir
chmod a+rx $extdir

docker run -ti --rm --network=$network \
    -v $extdir:/home/user/extern \
    local/icat-client

rmdir $extdir
