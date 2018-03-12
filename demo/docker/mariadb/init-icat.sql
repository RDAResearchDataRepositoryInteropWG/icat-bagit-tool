CREATE USER 'icat'@'%' IDENTIFIED BY 'toC6hahQu8yeh6oh';
CREATE DATABASE `icat`;
CREATE DATABASE `icat_authn_db`;
CREATE DATABASE `topcat`;
GRANT ALL ON icat.* TO 'icat'@'%';
GRANT ALL ON icat_authn_db.* TO 'icat'@'%';
GRANT ALL ON topcat.* TO 'icat'@'%';
