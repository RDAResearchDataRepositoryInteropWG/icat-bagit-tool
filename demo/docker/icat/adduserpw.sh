#! /bin/sh

mysql icat_authn_db <<'EOSQL'
--
-- Add some test users accounts to ICAT authn_db data base.
--
-- Add the following users:
-- Username   Password
--  acord     pwacord
--  ahau      pwahau
--  jbotu     pwjbotu
--  jdoe      pwjdoe
--  nbour     pwnbour
--  rbeck     pwrbeck
--

INSERT INTO PASSWD VALUES ('acord','$1$daH.TMIy$u0kmYEBMJg.7PA7krbdfy.');
INSERT INTO PASSWD VALUES ('ahau','$1$8CMvhCoB$WqTli5/RcnXt5jP467T1F.');
INSERT INTO PASSWD VALUES ('jbotu','$1$QOqUIJ0D$XHFzQvZ4N0fnauYfUOUql0');
INSERT INTO PASSWD VALUES ('jdoe','$1$dCGGhOgM$ENvQDPWssD1GPpqssJ8tT1');
INSERT INTO PASSWD VALUES ('nbour','$1$gPZfenMz$8oYJFbLcm9DtvyW69TCVt0');
INSERT INTO PASSWD VALUES ('rbeck','$1$NCp15tz9$F9UDYylaThj0.u4J8MupY1');
EOSQL
