#! /bin/sh

maindir=$(cd $(dirname $0); pwd)
network=icat-test.local
invname=180815-EF

expdir=$maindir/export
mkdir -p $expdir
rm -rf $expdir/$invname
chown 1000:100 $expdir
chmod 0755 $expdir

docker run -ti --rm --network=$network \
    -v $expdir:/home/user/export \
    local/icat-client \
    icat-bagit-export -s jbotu --bagdir=export/$invname $invname

