#! /usr/bin/python

from __future__ import print_function
import os
import os.path
import logging
import time
import datetime
import re
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

def checksums(s):
    """Parse the checksums configuration variable.
    """
    algs = set(s.split(','))
    for a in algs:
        if not a in bagit.CHECKSUM_ALGOS:
            raise ValueError()
    algs.add("sha256")
    return algs

def contact(s):
    """Parse the contact configuration variable.
    """
    contactRE = re.compile(r"""^
        (?:(?:(?P<name>.*?)\s+)?(?P<b><))?
        (?P<mail>[a-zA-Z0-9.+-]+@[a-zA-Z0-9.+-]+)
        (?(b)>|)
    $""", re.X | re.A)
    m = contactRE.match(s)
    if not m:
        raise ValueError()
    return (m.group("name"), m.group("mail"))

config = icat.config.Config(ids="mandatory")
config.add_variable('bagdir', ("--bagdir",), 
                    dict(help="directory name of the bag to create"),
                    default="./icat-export", type=os.path.abspath)
config.add_variable('checksums', ("--checksums",), 
                    dict(help="checksum algorithms"),
                    type=checksums, default="sha256,sha512")
config.add_variable('altid_name', ("--altid-name",), 
                    dict(help="name of an alternate identifier"),
                    optional=True)
config.add_variable('altid_format', ("--altid-format",), 
                    dict(help="format string to build the "
                         "alternate identifier"), optional=True)
config.add_variable('contact', ("--contact",), 
                    dict(help="person or entity responsible for the transfer"),
                    type=contact)
config.add_variable('description', ("--description",), 
                    dict(help="brief explanation of the contents and "
                         "provenance"), optional=True)
config.add_variable('source_organization', ("--source-organization",), 
                    dict(help="organization transferring the content"), 
                    optional=True)
config.add_variable('rights_text', ("--rights-text",), 
                    dict(help="rights information"), optional=True)
config.add_variable('rights_uri', ("--rights-uri",), 
                    dict(help="URI for the license"), optional=True)
config.add_variable('investigation', ("investigation",), 
                    dict(help="name and optionally visit id "
                         "(separated by a colon) of the investigation"))
client, conf = config.getconfig()
client.login(conf.auth, conf.credentials)


# ------------------------------------------------------------
# helper
# ------------------------------------------------------------

class MemorySpace(int):
    """Convenience: human readable amounts of memory space.
    """
    sizeB = 1
    sizeKiB = 1024*sizeB
    sizeMiB = 1024*sizeKiB
    sizeGiB = 1024*sizeMiB
    sizeTiB = 1024*sizeGiB
    sizePiB = 1024*sizeTiB
    units = { 'B':sizeB, 'KiB':sizeKiB, 'MiB':sizeMiB, 
              'GiB':sizeGiB, 'TiB':sizeTiB, 'PiB':sizePiB, }

    def __new__(cls, value):
        if isinstance(value, str):
            m = re.match(r'^(\d+(?:\.\d+)?)\s*(B|KiB|MiB|GiB|TiB|PiB)$', value)
            if not m:
                raise ValueError("Invalid size string '%s'" % value)
            v = float(m.group(1)) * cls.units[m.group(2)]
            return super(MemorySpace, cls).__new__(cls, v)
        else:
            v = int(value)
            if v < 0:
                raise ValueError("Invalid size value %d" % v)
            return super(MemorySpace, cls).__new__(cls, v)

    def __str__(self):
        for u in ['PiB', 'TiB', 'GiB', 'MiB', 'KiB']:
            if self >= self.units[u]:
                return "%.2f %s" % (self / self.units[u], u)
        else:
            return "%d B" % (int(self))

    def __rmul__(self, other):
        if type(other) == int:
            return MemorySpace(other*int(self))
        else:
            return super(MemorySpace, self).__rmul__(self, other)

def copyfile(infile, outfile, chunksize=8192):
    """Read all data from infile and write them to outfile.
    """
    size = 0
    while True:
        chunk = infile.read(chunksize)
        size += len(chunk)
        if not chunk:
            break
        outfile.write(chunk)
    return size

def entity_as_dict(obj):
    """Return a dict with the entity object's attributes.

    Note: this will be an Entity method tn the next release of python-icat,
    see https://github.com/icatproject/python-icat/pull/44.
    """
    try:
        return obj.as_dict()
    except AttributeError:
        d = {}
        for a in obj.InstAttr | obj.MetaAttr:
            d[a] = getattr(obj, a)
        return d

def get_investigation(invid):
    query = Query(client, "Investigation")
    query.addIncludes(("investigationUsers.user", "keywords", "facility"))
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

def datacite_investigation(investigation, conf, size):
    """Create `DataCite 4.0`_ bibliographic metadata from an investigation.

    .. _DataCite 4.0: https://schema.datacite.org/meta/kernel-4.0/
    """
    if _have_lxml:
        XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
        DC_NAMESPACE = "http://datacite.org/schema/kernel-4"
        DC_XSD = "http://schema.datacite.org/meta/kernel-4/metadata.xsd"
        NSMAP = {"xsi": XSI_NAMESPACE, None: DC_NAMESPACE}
        datacite = etree.Element("resource", nsmap=NSMAP)
        datacite.set("{%s}schemaLocation" % XSI_NAMESPACE, 
                     "%s %s" % (DC_NAMESPACE, DC_XSD))
    else:
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
    if investigation.keywords:
        subjects = etree.SubElement(datacite, "subjects")
        for keyword in investigation.keywords:
            subject = etree.SubElement(subjects, "subject")
            subject.text = keyword.name
    if investigation.startDate and investigation.endDate:
        dates = etree.SubElement(datacite, "dates")
        date = etree.SubElement(dates, "date")
        date.set("dateType", "Created")
        date.text = "%s/%s" % (investigation.startDate.date().isoformat(), 
                               investigation.endDate.date().isoformat())
    if conf.altid_name and conf.altid_format:
        altids = etree.SubElement(datacite, "alternateIdentifiers")
        altid = etree.SubElement(altids, "alternateIdentifier")
        altid.set("alternateIdentifierType", conf.altid_name)
        altid.text = conf.altid_format % entity_as_dict(investigation)
    resourceType = etree.SubElement(datacite, "resourceType")
    resourceType.set("resourceTypeGeneral", "Dataset")
    resourceType.text = "Dataset"
    sizes = etree.SubElement(datacite, "sizes")
    etree.SubElement(sizes, "size").text = str(size)
    if conf.rights_text:
        rights = etree.SubElement(datacite, "rightsList")
        right = etree.SubElement(rights, "rights")
        if conf.rights_uri:
            right.set("rightsURI", conf.rights_uri)
        right.text = conf.rights_text
    if investigation.summary:
        descriptions = etree.SubElement(datacite, "descriptions")
        description = etree.SubElement(descriptions, "description")
        description.set("descriptionType", "Abstract")
        description.text = investigation.summary
    return etree.ElementTree(datacite)

def download_data(destdir, investigation):
    size = 0
    os.makedirs(destdir)
    datasets = get_datasets(investigation)
    while True:
        backlog = []
        for dataset in datasets:
            try:
                outputfile = os.path.join(destdir, dataset.name + ".zip")
                response = client.getData([dataset])
                with open(outputfile, 'wb') as f:
                    size += copyfile(response, f)
            except icat.IDSDataNotOnlineError:
                backlog.append(dataset)
        if backlog:
            datasets = backlog
            time.sleep(10)
        else:
            break
    return MemorySpace(size)

def get_baginfo(investigation, conf, size):
    """Return a dict with metadata to put into the bag info.
    """
    org = (conf.source_organization or 
           investigation.facility.fullName or investigation.facility.name)
    desc = (conf.description or 
            ("Data colleced from measurements at %s." 
             % investigation.facility.name))
    if conf.altid_name and conf.altid_format:
        srcid = conf.altid_format % entity_as_dict(investigation)
    else:
        srcid = None
    profile = ("https://raw.githubusercontent.com/"
               "RDAResearchDataRepositoryInteropWG/bagit-profiles/"
               "master/generic/0.1/profile.json")

    baginfo = {}
    baginfo["Source-Organization"] = org
    if conf.contact[0]:
        baginfo["Contact-Name"] = conf.contact[0]
    baginfo["Contact-Email"] = conf.contact[1]
    if investigation.doi:
        baginfo["External-Identifier"] = investigation.doi
    baginfo["External-Description"] = desc
    baginfo["Bag-Size"] = str(size)
    if srcid:
        baginfo["Source-Identifier"] = srcid
    baginfo["BagIt-Profile-Identifier"] = profile
    return baginfo

def add_metadata(bag, investigation, conf, size):
    os.chdir(bag.path)

    os.mkdir("metadata")
    fname = os.path.join("metadata", "datacite.xml")
    datacite = datacite_investigation(investigation, conf, size)
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

investigation = get_investigation(conf.investigation)
size = download_data(conf.bagdir, investigation)
baginfo = get_baginfo(investigation, conf, size)
bag = bagit.make_bag(conf.bagdir, bag_info=baginfo, checksums=conf.checksums)
add_metadata(bag, investigation, conf, size)
