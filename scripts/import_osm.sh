#!/bin/bash

# This script downloads a bz2 compressed OSM datasets (url is argument #1)
# unpacks and imports into the "routing1" PostgreSQL Database.


# Abort script on error
set -e
set -u


# require osm file download url as argument
if [ $# -eq 0 ]; then
    echo "No osm download url supplied (eg. http://download.geofabrik.de/europe/andorra-latest.osm.bz2)"
    exit 1
fi

# Read PgSQL user and password from arguments
PG_USER=$2
PG_PW=$3
if [ -z "$PG_USER" ]; then
	echo "No user supplied."
	exit 1
fi
if [ "$PG_USER" != "postgres" ]; then
        echo "User must be 'postgres'."
        exit 1
fi
if [ -z "$PG_PW" ]; then
	echo "No password supplied."
	exit 1
fi


# Create (unique) temp dir to download and unpack OSM data
MYTIME=$(date +%s)
mkdir -p ibis/${MYTIME}/
cd ibis/${MYTIME}/

# Remove temp data on exit
trap "rm -r ibis/${MYTIME}/" EXIT


# Download OSM data
wget $1
echo "Download successfull"

# Unpack OSM data
bz2=$(find . -maxdepth 1 -name '*.osm.bz2' | tail -n 1)
osm=${bz2::-4}
echo "Unpacking $bz2 ..."
bunzip2 -dc ${bz2} > ${osm}
echo "Unpacking successfull"


# Create new Database routing1_new to import OSM data into:
su ${PG_USER} -c "psql -c \"DROP DATABASE IF EXISTS ibis_test;\""
su ${PG_USER} -c "createdb ibis_test"
su ${PG_USER} -c "psql -d ibis_test -c \"CREATE EXTENSION postgis; CREATE EXTENSION pgrouting;\""
echo "Created new and removed old database successfully"


# Import OSM data into PostgreSQL DB
/usr/share/bin/osm2pgrouting -file ${osm} -dbname ibis_test -host 127.0.0.1 \
-conf /usr/share/osm2pgrouting/mapconfig.xml -user ${PG_USER} -clean -passwd ${PG_PW} \
&& echo "Imported OSM data successfully"


ENDTIME=$(date +%s)
RUNSEC=$((ENDTIME-MYTIME))
RUNMIN=$((RUNSEC / 60))
echo "Laufzeit: $RUNSEC Sekunden ($RUNMIN Minuten)"

exit 0
