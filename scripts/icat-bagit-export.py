#! /usr/bin/python

from __future__ import print_function
import os
import os.path
import logging
import bagit
import icat
import icat.config
from icat.query import Query

logging.basicConfig(level=logging.INFO)

config = icat.config.Config(ids="mandatory")
config.add_variable('bagdir', ("--bagdir",), 
                    dict(help="directory name of the bag to create"),
                    default="./icat-export", type=os.path.abspath)
config.add_variable('investigation', ("investigation",), 
                    dict(help="name and optionally visit id "
                         "(separated by a colon) of the investigation"))
client, conf = config.getconfig()
client.login(conf.auth, conf.credentials)


# ------------------------------------------------------------
# helper
# ------------------------------------------------------------

def copyfile(infile, outfile, chunksize=8192):
    """Read all data from infile and write them to outfile.
    """
    while True:
        chunk = infile.read(chunksize)
        if not chunk:
            break
        outfile.write(chunk)

def get_investigation(invid):
    query = Query(client, "Investigation")
    l = invid.split(':')
    if len(l) == 1:
        # No colon, invid == name
        query.addConditions({"name": "= '%s'" % l[0]})
    elif len(l) == 2:
        # one colon, invid == name:visitId
        query.addConditions({"name": "= '%s'" % l[0], 
                              "visitId": "= '%s'" % l[1]})
    else:
        # too many colons
        raise RuntimeError("Invalid investigation identifier '%s'" % invid)
    return (client.assertedSearch(query)[0])

def get_datasets(inv):
    # Skip empty datasets, e.g. search only datasets that have any
    # datafiles with the location attribute set.
    query = Query(client, "Dataset", 
                  conditions={"investigation.id": "= '%d'" % inv.id, 
                              "datafiles.location": "IS NOT NULL"}, 
                  aggregate="DISTINCT")
    return client.searchChunked(query)

# ------------------------------------------------------------
# do it
# ------------------------------------------------------------

investigation = get_investigation(conf.investigation)

# FIXME: this scripts is still incomplete:
# - must create metadata.
# - data may be not online, must account for that and repeat the
#   getData() call where neccessary.
os.makedirs(conf.bagdir)
for dataset in get_datasets(investigation):
    outputfile = os.path.join(conf.bagdir, dataset.name + ".zip")
    response = client.getData([dataset])
    with open(outputfile, 'wb') as f:
        copyfile(response, f)

bag = bagit.make_bag(conf.bagdir)
