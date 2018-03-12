icat-bagit-tool Demonstration
=============================

This directory provides a Docker environment to demonstrate the export
of data from ICAT into BagIt packages using icat-bagit-tool.


Content
-------

`docker`
  Input files for three docker images, `local/icat-mariadb`,
  `local/icat-icat`, and `local/icat-client`, see Section `Docker
  Images`_ below.

`testcontent`
  Example content to populate the ICAT with some data.

`icat-*.sh`
  Shell scripts to run the demo, see Section `Run the Demo`_ below.


Docker Images
-------------

Three docker images are created for the demo:

`local/icat-mariadb`
  data base backend for ICAT.

`local/icat-icat`
  the ICAT, listening on port 8181 in the internal docker network for
  HTTPS connections.

`local/icat-client`
  the client that connects to the ICAT and performs the export.  The
  client has icat-bagit-tool installed.

These docker images are based on images from docker hub.

A dedicated docker bridge network with the name `icat-test.local` is
setup for the test.


Run the Demo
------------

Note: the demo needs to build docker images and run docker
containers.  In general that means it needs root privileges to be
allowed to talk to the docker demon.

The demo is run step by step by the following shell scripts:

0. Prerequisite: make sure the docker demon is running.

1. Build::

     $ sudo ./icat-build.sh

   This builds the three docker images described above.

2. Run::

     $ sudo ./icat-run.sh

   Setup a local docker bridge network named `icat-test.local` and
   runs two containers, `mysql` and `icat`.

   Note that starting the `icat` container may take a significant
   amount of time, because it configures a Payara application server
   and deploys several ICAT components at this server during startup.
   You may want to watch the log with::

     $ sudo docker logs -f icat

   The startup is finished when the line "GlassFish is running." is
   shown.

3. Ingest::

     $ sudo ./icat-ingest.sh

   Populate the ICAT with example content.  This runs a client
   container to connect ICAT.

4. Export::

     $ sudo ./icat-export.sh

   This runs the icat-bagit-tool in a client container.  It creates a
   directory `export/180815-EF` with the exported bagit package.

5. Clean up::

     $ sudo ./icat-clean.sh

   This kills the `mysql` and `icat` container and tears down the
   local network created in step 2.

The script `icat-client.sh` runs an interactive shell in a client
container.  This may be useful to investigate the ICAT and for
debugging.
