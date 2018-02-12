#! /usr/bin/python

from __future__ import print_function
import os
import os.path
import logging
import time
import datetime
import bagit
_have_lxml = None
try:
    from lxml import etree
    _have_lxml = True
except ImportError:
    import xml.etree.ElementTree as etree
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
    query.addIncludes(("investigationUsers.user", "facility"))
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

def datacite_investigation(investigation):
    """Create `DataCite 4.0`_ bibliographic metadata from an investigation.

    .. _DataCite 4.0: https://schema.datacite.org/meta/kernel-4.0/
    """
    datacite = etree.Element("resource")
    identifier = etree.SubElement(datacite, "identifier")
    identifier.set("identifierType", "DOI")
    identifier.text = investigation.doi or "(:unas)"
    creators = etree.SubElement(datacite, "creators")
    for iu in investigation.investigationUsers:
        creator = etree.SubElement(creators, "creator")
        etree.SubElement(creator, "creatorName").text = iu.user.fullName
        orcid = getattr(iu.user, "orcidId", None)
        if orcid:
            nameId = etree.SubElement(creator, "nameIdentifier")
            nameId.set("nameIdentifierScheme", "ORCID")
            nameId.text = oricid
    titles = etree.SubElement(datacite, "titles")
    etree.SubElement(titles, "title").text = investigation.title
    publisher = etree.SubElement(datacite, "publisher")
    publisher.text = (investigation.facility.fullName or 
                      investigation.facility.name)
    etree.SubElement(datacite, "publicationYear").text = "(:unav)"
    if investigation.startDate and investigation.endDate:
        dates = etree.SubElement(datacite, "dates")
        date = etree.SubElement(dates, "date")
        date.set("dateType", "Created")
        date.text = "%s/%s" % (investigation.startDate.date().isoformat(), 
                               investigation.endDate.date().isoformat())
    resourceType = etree.SubElement(datacite, "resourceType")
    resourceType.set("resourceTypeGeneral", "Dataset")
    resourceType.text = "Dataset"
    if investigation.summary:
        descriptions = etree.SubElement(datacite, "descriptions")
        description = etree.SubElement(describtions, "description")
        description.set("descriptionType", "Abstract")
        description.text = investigation.summary
    return etree.ElementTree(datacite)

def download_data(destdir, investigation):
    os.makedirs(destdir)
    datasets = get_datasets(investigation)
    while True:
        backlog = []
        for dataset in datasets:
            try:
                outputfile = os.path.join(destdir, dataset.name + ".zip")
                response = client.getData([dataset])
                with open(outputfile, 'wb') as f:
                    copyfile(response, f)
            except icat.IDSDataNotOnlineError:
                backlog.append(dataset)
        if backlog:
            datasets = backlog
            time.sleep(10)
        else:
            break

def add_metadata(bag, investigation):
    os.chdir(bag.path)

    os.mkdir("metadata")
    fname = os.path.join("metadata", "datacite.xml")
    datacite = datacite_investigation(investigation)
    if _have_lxml:
        datacite.write(fname,  pretty_print=True)
    else:
        datacite.write(fname)

    # recreate tagmanifest files
    for alg in bag.algorithms:
        bagit._make_tagmanifest_file(alg, bag.path, encoding=bag.encoding)

# ------------------------------------------------------------
# do it
# ------------------------------------------------------------

# FIXME: this scripts is still incomplete:
# - datacite metadata still leaves room for improvement.
# - BagIt profile support missing.

investigation = get_investigation(conf.investigation)
download_data(conf.bagdir, investigation)
bag = bagit.make_bag(conf.bagdir)
add_metadata(bag, investigation)
