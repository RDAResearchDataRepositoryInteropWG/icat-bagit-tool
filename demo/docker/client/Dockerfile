FROM rkrahl/opensuse:42.3

COPY icat-bagit-tool-1.1-1.noarch.rpm /usr/src/packages/RPMS/noarch/

RUN zypper --non-interactive addrepo http://download.opensuse.org/repositories/home:/Rotkraut:/Data/openSUSE_Leap_42.3/home:Rotkraut:Data.repo && \
    zypper --non-interactive modifyrepo --refresh home_Rotkraut_Data && \
    zypper --non-interactive --gpg-auto-import-keys refresh home_Rotkraut_Data && \
    zypper --non-interactive addrepo /usr/src/packages/RPMS/ local && \
    zypper --non-interactive modifyrepo --refresh --no-gpgcheck local && \
    zypper --non-interactive install \
        icat-bagit-tool \
        less \
        mariadb-client

RUN useradd -m user && \
    mkdir -p /home/user/.config/icat /home/user/bin
COPY mysql.cnf /home/user/.my.cnf
COPY icat.cfg /home/user/.config/icat/icat.cfg
COPY icatsh /home/user/bin/icatsh
COPY bashrc /home/user/.bashrc
RUN chown -R user:users /home/user && \
    chmod u=r,go-rwx /home/user/.my.cnf && \
    chmod go-rwx /home/user/.config

USER user
WORKDIR /home/user

ENV TERM xterm

CMD ["/bin/bash"]
