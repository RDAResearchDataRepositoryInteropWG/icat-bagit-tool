icat-bagit-tool - Export data from ICAT into BagIt packages
===========================================================

This tool implements the export scientific data from an `ICAT`_ into a
BagIt package as defined by the `RDA Research Data Repository
Interoperability WG`__.

.. __: `RDA-rdrinterop`_


System requirements
-------------------

Python:

+ Python 2.7, or 3.2 and newer.

Required Library packages:

+ `python-icat`_

+ `bagit`_

+ `lxml`_


Installation
------------

python-icat uses the distutils Python standard library package and
follows its conventions of packaging source distributions.  See the
documentation on `Installing Python Modules`_ for details or to
customize the install process.

1. Download the sources, unpack, and change into the source directory.

2. Build::

     $ python setup.py build

3. Test (optional, see below)::

     $ python setup.py test

4. Install::

     $ python setup.py install

The last step might require admin privileges in order to write into
the site-packages directory of your Python installation.


Bugs and limitations
--------------------

+ For the time being, only the export part is implemented.  The tool
  does not support the import of BagIt packages into ICAT.


Copyright and License
---------------------

Copyright 2018
Helmholtz-Zentrum Berlin für Materialien und Energie GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.  You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.


.. _ICAT: https://www.icatproject.org/
.. _RDA-rdrinterop: https://rd-alliance.org/groups/research-data-repository-interoperability-wg.html
.. _python-icat: https://icatproject.org/user-documentation/python-icat/
.. _bagit: https://pypi.python.org/pypi/bagit/
.. _lxml: http://lxml.de/
.. _Installing Python Modules: https://docs.python.org/2.7/install/
