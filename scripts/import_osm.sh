#!/bin/bash

# This script downloads a bz2 compressed OSM datasets (url is argument #1)
# unpacks and imports into the "routing1" PostgreSQL Database.

# usage: ./import_osm.sh <osm-data-url> <pgsql-user> <pgsql-password> <osm2pgrouting-binary> <osm2pgrouting-conf> <db-name>

# Abort script on error
set -e
set -u


# usage help
if [ $# -ne 6 ]; then
    echo "usage: ./import_osm.sh <osm-data-url> <pgsql-user> <pgsql-password> <osm2pgrouting-binary> <osm2pgrouting-conf> <db-name>"
    exit 1
fi

OSM_URL=$1
# require osm file download url as argument
if [[ ! ${OSM_URL} =~ http.* ]]; then
    echo "Incorrect osm download url supplied (eg. http://download.geofabrik.de/europe/andorra-latest.osm.bz2)"
    exit 1
fi

# Read PgSQL user and password from arguments
PG_USER=$2
if [ -z "$PG_USER" ]; then
	echo "No user supplied."
	exit 1
fi

PG_PW=$3
if [ -z "$PG_PW" ]; then
	echo "No password supplied."
	exit 1
fi
export PGPASSWORD=${PG_PW}

OSM2PGR_BIN=$4
# check for osm2pgrouting binary
if [ ! -x "$OSM2PGR_BIN" ]; then
    echo "osm2pgrouting-binary ($OSM2PGR_BIN) must exist and executable permission must be granted"
    ls -ahl "$OSM2PGR_BIN"
    exit 1
fi

OSM2PGR_CONF=$5
# check for readable osm2pgrouting mapconfig.xml file
if [ ! -r "$OSM2PGR_CONF" ]; then
    echo "osm2pgrouting-conf xml file ($OSM2PGR_CONF) must exist"
    exit 1
fi

PG_DB=$6
# check for readable osm2pgrouting mapconfig.xml file
if [ -z "$PG_DB" ]; then
	echo "No database name supplied."
    exit 1
fi


# Create (unique) temp dir to download and unpack OSM data
MYTIME=$(date +%s)
mkdir -p ibis/${MYTIME}/
cd ibis/${MYTIME}/

# Remove temp data on exit
trap "cd ../../ && rm -r ibis/${MYTIME}/" EXIT


# Download OSM data
wget ${OSM_URL}
echo "Download successfull"

# Unpack OSM data
bz2=$(find . -maxdepth 1 -name '*.osm.bz2' | tail -n 1)
osm=${bz2::-4}
echo "Unpacking $bz2 ..."
bunzip2 -dc ${bz2} > ${osm}
echo "Unpacking successfull"


# Create new Database routing1_new to import OSM data into:
psql -U${PG_USER} -h127.0.0.1 -p5432 -c "DROP DATABASE IF EXISTS $PG_DB;"
createdb -U${PG_USER} -h127.0.0.1 -p5432 ${PG_DB}
psql -U${PG_USER} -h127.0.0.1 -p5432 -d ${PG_DB} -c "CREATE EXTENSION postgis; CREATE EXTENSION pgrouting;"
echo "Created new and removed old database successfully"


# Import OSM data into PostgreSQL DB
${OSM2PGR_BIN} --file ${osm} --conf ${OSM2PGR_CONF} \
--host 127.0.0.1 --db_port 5432 --dbname ${PG_DB} --user ${PG_USER} --passwd ${PG_PW}
echo "Imported OSM data successfully"


ENDTIME=$(date +%s)
RUNSEC=$((ENDTIME-MYTIME))
RUNMIN=$((RUNSEC / 60))
echo "Laufzeit: $RUNSEC Sekunden ($RUNMIN Minuten)"

exit 0
