# coding: utf-8
"""
crontab -e
* */3 * * * python3 /home/services/spectrum_server/scripts/backup_restore.py >/dev/null 2>&1
"""

import datetime
import os
import re
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path

MAX_BACKUP_DAYS = 30
MAX_TODAY_BACKUP_NUM = 2
MAX_OTHER_DAY_BACKUP_NUM = 1

BACKUPS_DIR = '/home/ubuntu/pg_backups'

CONTAINER_BACKUPS_DIR = '/backups'


def get_date():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def get_file_date(filename):
    filedates = re.findall('^(\d{8}_\d{6})', filename)
    if filedates:
        return datetime.datetime.strptime(filedates[0], '%Y%m%d_%H%M%S')
    return None

def get_path_file_date(filepath):
    """
    sort function
    """
    return get_file_date(os.path.basename(filepath)) or '-'

def get_dated_name(date, name, prefix=''):

    return '{0}_{1}{2}'.format(
        date,
        prefix,
        name
    )

def print_files(backup_dir):

    files = os.listdir(backup_dir)
    files = [f for f in files if 'dump' in f]
    sorted_files = sorted([os.path.join(backup_dir, f) for f in files], key=os.path.getmtime)
    dumps = [f for f in sorted_files if f.endswith('.sql.gz') or f.endswith('.sqld') or f.endswith('.sqlc')]
    print('\nTotal {0} dumps'.format(len(dumps)))

    items = sorted(dumps, key=get_path_file_date, reverse=True)

    for i, item in enumerate(items, start=1):
        print(f'{i}) {item} {Path(item).stat().st_size}')

    return items


BACKUP_DATE = get_date()


def make_dump(backup_dir, dbhost, dbuser, dbpassword, dbname):

    print('PG dump...')

    name = os.path.join(backup_dir, get_dated_name(BACKUP_DATE, 'pg_dump.sql.gz'))

    command = 'docker exec -it server-postgres sh -c "pg_dump -U {dbuser} -h {dbhost} --create --clean --format=c {dbname} > {path}"'.format(
        dbuser=dbuser,
        dbpassword=dbpassword,
        dbhost=dbhost,
        path=name,
        dbname=dbname
    )

    print(command)

    os.system(command)


def load_dump(backup_dir, dbhost, dbuser, dbpassword, dbname):

    files = print_files(backup_dir)

    try:
        inp = int(input('backup id >'))
    except:
        pass
    else:

        name = files[inp - 1]

        name = name.replace(BACKUPS_DIR, CONTAINER_BACKUPS_DIR)

        command = 'docker exec -it server-postgres sh -c "pg_restore -U {dbuser} -h {dbhost} -d {dbname} --clean --format=c {path}"'.format(
            dbuser=dbuser,
            dbpassword=dbpassword,
            dbhost=dbhost,
            path=name,
            dbname=dbname
        )

        print(command)

        os.system(command)


def delete_old_backups():

    def _delete_item(item):
        msg = 'Deleting {0}'.format(os.path.join(backup_dir, item))
        print(msg)
        # print(f'rm {item}')
        os.remove(item)

    backup_dir = BACKUPS_DIR

    dumps = print_files(backup_dir)

    # order is crucial here so we'll delete old backups, not new
    items = sorted(dumps, key=get_path_file_date, reverse=True)

    counter = Counter()
    days_counter = 0

    for item in items:

        item_dt = get_path_file_date(item)

        max_days_dt = datetime.datetime.now() - timedelta(days=MAX_BACKUP_DAYS)

        if max_days_dt > item_dt:
            _delete_item(item)

        if item_dt.date() == datetime.datetime.now().date():
            if counter[item_dt.date()] >= MAX_TODAY_BACKUP_NUM:
                _delete_item(item)

        if item_dt.date() <= datetime.datetime.now().date() - timedelta(days=1):
            if counter[item_dt.date()] >= MAX_OTHER_DAY_BACKUP_NUM:
                _delete_item(item)

        counter[item_dt.date()] += 1


def main():

    op = sys.argv[1:]

    HOST, USER, PASSWORD, NAME = 'localhost', 'main', 's50XgW4', 'main'

    if 'restore' in op:

        load_dump(
            BACKUPS_DIR,
            HOST, USER, PASSWORD, NAME
        )

    else:

        make_dump(
            CONTAINER_BACKUPS_DIR,
            HOST, USER, PASSWORD, NAME
        )

        delete_old_backups()


if __name__ == "__main__":
    main()
