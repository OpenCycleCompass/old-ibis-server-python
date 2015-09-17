#!/usr/bin/env python

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--osm_url", required=True, help="OSM download URL (*.osm.bz2)", type=str)
    parser.add_argument("-p", "--user", required=True, help="PostgreSQL database password", type=str)
    parser.add_argument("-u", "--password", required=True, help="PostgreSQL database user", type=str,
                        choices=["postgres"])
    args = parser.parse_args()

    print 'Importing OSM data ...'
    if subprocess.call(['scripts/import_osm.sh', args.osm_url, args.user, args.password]) == 0:
        print '... Success!'
    else:
        print '... Failed.'
        return 1

    print 'Creating iBis tables ...'
    # TODO
    print '... Success!'


if __name__ == '__main__':
    main()
