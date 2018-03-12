FROM rkrahl/icat:4.9.1

USER root

RUN zypper --non-interactive install \
        mariadb-client

COPY mysql.cnf $GLASSFISH_HOME/.my.cnf
COPY icat.zip /tmp
RUN chown glassfish:glassfish $GLASSFISH_HOME/.my.cnf /tmp/icat.zip && \
    chmod go-rwx $GLASSFISH_HOME/.my.cnf

USER glassfish

RUN unzip -q -d /opt/payara41/etc /tmp/icat.zip && \
    chmod -R go-rwx /opt/payara41/etc/icat && \
    rm -f /tmp/icat.zip

COPY adduserpw.sh /etc/glassfish.d/20-adduserpw.sh

ENV GF_DOMAIN_LIBS /usr/share/java/mysql-connector-java.jar
