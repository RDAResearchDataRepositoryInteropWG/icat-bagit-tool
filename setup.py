#! /usr/bin/python
"""icat-bagit-tool - Export data from ICAT into BagIt packages

This tool implements the export scientific data from an `ICAT`__ into
a BagIt package as defined by the `RDA Research Data Repository
Interoperability WG`__.

.. __: https://www.icatproject.org/
.. __: https://rd-alliance.org/groups/research-data-repository-interoperability-wg.html
"""

import re
from distutils.core import setup


DOCLINES         = __doc__.split("\n")
DESCRIPTION      = DOCLINES[0]
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])
VERSION          = "0.0"
AUTHOR           = "Rolf Krahl <rolf.krahl@helmholtz-berlin.de>"
URL              = ("https://github.com/RDAResearchDataRepositoryInteropWG/"
                    "icat-bagit-tool")
m = re.match(r"^(.*?)\s*<(.*)>$", AUTHOR)
(AUTHOR_NAME, AUTHOR_EMAIL) = m.groups() if m else (AUTHOR, None)


setup(
    name = "icat-bagit-tool",
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    author = AUTHOR_NAME,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = "Apache-2.0",
    requires = ["icat", "bagit", "lxml"],
    scripts = ["scripts/icat-bagit-export.py"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
)

