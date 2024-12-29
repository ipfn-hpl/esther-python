#!/home/esther/.local/venvs/python-epics/bin/python3
#
#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/8241099/executing-tasks-in-parallel-in-python


https://mysqlclient.readthedocs.io/user_guide.html

Detect Mode:
	This mode allows you to determine the IP addresses that are in the network in streaming mode. By default, the search takes 5 seconds.

"""

import argparse
import MySQLdb
import numpy as np
# Local module with DB configuration
import config

BOTTLES_CHANNELS = [
    {'name': 'PT101', 'pv': 'Esther:gas:PT101'},
    {'name': 'PT201', 'pv': 'Esther:gas:PT201'},
    {'name': 'PT301', 'pv': 'Esther:gas:PT301'},
    {'name': 'PT401', 'pv': 'Esther:gas:PT401'},
    {'name': 'PT501', 'pv': 'Esther:gas:PT501'},
    {'name': 'PT801', 'pv': 'Esther:gas:PT801'},
    ]

class EstherDB():
    """
    """
    def __init__(self):
        """
        Initializes the DB connection
        """
        self.db = MySQLdb.connect(
                host=config.host,
                user=config.username,
                password=config.password,
                database=config.database)

    def GetLastShot(self, series='S'):
        c = self.db.cursor()
        query = (
                "SELECT id, shot FROM reports "
                "WHERE esther_series_name = %s "
                "ORDER BY id DESC LIMIT 1")
        c.execute(query, series)
        return c.fetchone()

    def InsertShot(self, series, shot, ce, re):
        c = self.db.cursor()
        query = (
                "INSERT INTO reports "
                "(id, esther_series_name, shot, chief_engineer_id, researcher_id) "
                "VALUES (NULL, %s, %s, %s, %s)")
        try:
            c.execute(query, (series, shot, ce, re,))
            # MySQLdb._exceptions.IntegrityError
        except MySQLdb._exceptions.IntegrityError:
            print('1062, Duplicate entry ')
            #  print("1062, Duplicate entry 'S-101' for key 'esther_series_name'")
            # print(c.statement)
            # print(query)
            raise ValueError

        self.db.commit()
        return self.GetLastShot(series)
        # return Id, shot

    def GetBottlePressures(self, shot_id):
        c = self.db.cursor()
        pvals = []
        PHS = ['CC_Start', 'CC_End']
        for p in PHS:
            bvals = []
            for b in BOTTLES_CHANNELS:
                query = ("SELECT float_val FROM sample "
                        "WHERE reports_id = %s "
                        "AND short_name = %s "
                        "AND pulse_phase = %s")
                c.execute(query, (shot_id, b['name'], 'CC_Start'))
                fv = c.fetchone()
                bvals.append(fv)
            # print(c._last_executed)
            pvals.append(bvals)
        # return np.array(pvals)
        cols = []
        for b in BOTTLES_CHANNELS:
            cols.append(b['name'])
        # bData = {'columns': cols, 'data': np.array(pvals)}
        bData = {'columns': cols, 'data': pvals}
        return bData  # np.array(pvals)

    def SaveBottlePressures(self, shot_id, phase):
        from epics import caget  # , caput  # , cainfo
        c = self.db.cursor()
        for b in BOTTLES_CHANNELS:
            pval = caget(b['pv'])
            query = ("INSERT INTO sample "
                    "(time_date, reports_id, short_name, pulse_phase, float_val) "
                    "VALUES (current_timestamp(), %s, %s, %s, %s)")
            try:
                c.execute(query, (shot_id, b['name'], phase, pval))
            except MySQLdb._exceptions.IntegrityError:
                # Interpolate the values into the query
                # i_query = c.mogrify(query, (shot_id, b, phase,))
                print('(1062, Duplicate entry ')
                # Print the actual query executed
                print(c._last_executed)
                # raise ValueError
        self.db.commit()


"""

db = MySQLdb.connect(host=config.host,
                     user=config.username,
                     password=config.password,
                     database=config.database)

def get_last_shot(db):
    c = db.cursor()
    query = ("SELECT id, shot FROM reports "
             "ORDER BY id DESC LIMIT 1")
    c.execute(query)
    return c.fetchone()


def bottle_pressures(db, shot_id, phase):
    c = db.cursor()
    bottles_channels = [
            {'name': 'PT101', 'pv': 'Esther:gas:PT101'},
            {'name': 'PT201', 'pv': 'Esther:gas:PT201'},
            {'name': 'PT301', 'pv': 'Esther:gas:PT301'},
            {'name': 'PT401', 'pv': 'Esther:gas:PT401'},
            ]
    for b in bottles_channels:

        pval = caget(b['pv'])
        query = ("INSERT INTO sample "
                 "(time_date, reports_id, short_name, pulse_phase, float_val) "
                 "VALUES (current_timestamp(), %s, %s, %s, %s)")
        try:
            c.execute(query, (shot_id, b['name'], phase, pval))
            db.commit()
        except MySQLdb._exceptions.IntegrityError:
            # Interpolate the values into the query
            # i_query = c.mogrify(query, (shot_id, b, phase,))
            print('(1062, Duplicate entry ')
            # Print the actual query executed
            print(c._last_executed)


    # c.executemany(
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Function to manipulated Esther Reports')
    parser.add_argument('-n', '--newReport',
                        action='store_true', help='Insert new Report')
    parser.add_argument('-t', '--test',
                        action='store_true', help='Insert test')

    dB = EstherDB()
    # Id, shot = dB.GetLastShot()
    result = dB.GetLastShot(series='S')
    print(result)
    # print(f"Id {Id}, {shot}")
    args = parser.parse_args()
    if (args.newReport):
        Id, shot = dB.InsertShot('S', shot + 1, 3, 1)
        print(f"Inserted {Id}, {shot}")
        dB.SaveBottlePressures(Id, 'CC_Start')
        dB.SaveBottlePressures(Id, 'End')
        # insert_report(db, 'S', 101, 3, 1)
        exit()
    if (args.test):
        result = dB.GetLastShot(series='E')
        if result is not None:
            print(result)
        # bottle_pressures(db, 303, 'CC_Start')
        exit()

    # args = parse_args()
# vim: syntax=python ts=4 sw=4 sts=4 sr et
