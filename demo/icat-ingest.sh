#! /bin/sh

maindir=$(cd $(dirname $0); pwd)
network=icat-test.local

docker run -ti --rm --network=$network \
    -v $maindir/testcontent:/home/user/content \
    local/icat-client \
    icatingest -s root --upload-datafiles --datafile-dir=content -f XML -i content/icatdump.xml
