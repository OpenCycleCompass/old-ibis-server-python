#!/usr/bin/env python

import argparse
import subprocess
import os.path
import sys
import bz2

import requests

import ibisapi2.database.helper


def download_file(url, local_path):
    local_filename = ''.join([local_path, url.split('/')[-1]])
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


def uncompress_bz2(filename_bz2):
    filename_osm = filename_bz2[:-4]
    with open(filename_osm, 'wb') as file_osm, bz2.BZ2File(filename_bz2, 'rb') as file_bz2:
        for data in iter(lambda: file_bz2.read(100 * 1024), b''):
            file_osm.write(data)
    return filename_osm


def open_database_connection():
    pass


def main():
    parser = argparse.ArgumentParser()
    arg_grp_osm_data = parser.add_mutually_exclusive_group(required=True)
    arg_grp_osm_data.add_argument("-f", "--osm_file", help="OSM file (*.osm.bz2)", type=str)
    arg_grp_osm_data.add_argument("--osm_url", help="OSM download URL (*.osm.bz2)", type=str)

    parser.add_argument("-u", "--db_user", required=True, help="PgSQL database user", type=str)
    parser.add_argument("-p", "--db_password", required=True, help="PgSQL database password", type=str)
    parser.add_argument("-d", "--db_name", required=True, help="PgSQL database name", type=str)
    parser.add_argument("--db_host", required=False, help="PgSQL database host", type=str, default="127.0.0.1")
    parser.add_argument("--db_port", required=False, help="PgSQL database port", type=int, default=5432)

    parser.add_argument("--osm2pgr_bin", required=False, help="path to osm2pgrouting binary", default="osm2pgrouting")
    parser.add_argument("--osm2pgr_conf", required=False, help="path to osm2pgrouting mapconfig.xml file",
                        default="/usr/share/osm2pgrouting/mapconfig.xml")

    parser.add_argument("-v", "--verbose", required=False, action="count", default=0, help="increase output verbosity")

    parser.add_argument("-k", "--keep_download", required=False, action='store_true', default=False,
                        help="do not delete downloaded files after data import")

    arg_grp_import_data = parser.add_mutually_exclusive_group(required=True)
    arg_grp_import_data.add_argument("--data_file", help="iBis data (zipped sql dump)", type=str)
    arg_grp_import_data.add_argument("--no_data_import", action='store_true', default=False,
                                     help="do not import data from backup (just create empty tables)")

    args = parser.parse_args()

    # validate arguments
    # check if osm2pgrouting binary and config file exist
    if not os.path.isfile(args.osm2pgr_conf):
        print "osm2pgrouting config file (--osm2pgr_conf", args.osm2pgr_conf, ") does not exist."
        sys.exit(1)
    if not (os.path.exists(args.osm2pgr_bin) and os.access(args.osm2pgr_bin, os.X_OK)):
        print "osm2pgrouting binary file (--osm2pgr_bin", args.osm2pgr_bin, ") does not exist."
        sys.exit(1)

    # check if OSM data file exists or download file from OSM data url
    if args.osm_file is not None:
        if not os.path.isfile(args.osm_file):
            print "OSM data file (--osm_file", args.osm_file, ") does not exist."
            sys.exit(1)
        else:
            bz2_file = args.osm_file
    else:
        try:
            os.makedirs('tmp/ibis')  # exist_ok=True (python3 only)
        except OSError:
            pass
        bz2_file = download_file(args.osm_url, 'tmp/ibis/')

    # uncompress bz2 file
    osm_file = uncompress_bz2(bz2_file)

    # check for ibis data file
    if not args.no_data_import:
        if not os.path.isfile(args.data_file):
            print "iBis data file (--data_file", args.data_file, ") does not exist."
            sys.exit(1)
        else:
            data_file = args.data_file
    else:
        data_file = None

    # Open database connection
    engine = ibisapi2.database.helper.create_engine(args.db_user, args.db_password, args.db_name, host=args.db_host,
                                           port=args.db_port)

    # create PostGIS and pgRouting extensions in database:
    print "Creating PostGIS and pgRouting extension in PostgreSQL database"
    engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    engine.execute("CREATE EXTENSION IF NOT EXISTS pgrouting;")


    # import osm data
    print 'Importing OSM data ...'
    if subprocess.call([args.osm2pgr_bin,
                        '--conf', args.osm2pgr_conf,
                        '--file', osm_file,
                        '--host', args.db_host,
                        '--db_port', str(args.db_port),
                        '--user', args.db_user,
                        '--passwd', args.db_password,
                        '--dbname', args.db_name
                        ]) == 0:
        print '... Success!'
    else:
        print '... Error.'
        sys.exit(1)

    # create iBis database tables
    tables = ibisapi2.database.helper.create_tables()
    tables ['metadata'].create_all(engine)

    # copy osm way types from osm2pgrouting table to ibis table
    # TODO

    # optional import data from backup
    # [work in progress] TODO
    if data_file:
        print 'Creating iBis tables (import data from backup) ...'
        my_env = os.environ
        my_env['PGPASSWORD'] = args.db_password

        if subprocess.call(['psql',
                            '-h', args.db_host,
                            '-p', str(args.db_port),
                            '-U', args.db_user,
                            '-d', args.db_name,
                            '--file', data_file],
                           env=my_env) == 0:
            print '... Success!'
        else:
            print '... Error.'
            sys.exit(1)
    else:
        print 'iBis data import skipped.'

    # clean up downloaded file
    if not args.keep_download and args.osm_url is not None:
        print 'Removing OSM data file ...'
        try:
            os.remove(osm_file)
            print '... removed.'
        except OSError:
            print '... error.'
            pass


if __name__ == '__main__':
    main()
