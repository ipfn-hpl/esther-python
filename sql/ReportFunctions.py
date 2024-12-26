#!/home/esther/.local/venvs/python-epics/bin/python3
#
#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/8241099/executing-tasks-in-parallel-in-python



Detect Mode:
	This mode allows you to determine the IP addresses that are in the network in streaming mode. By default, the search takes 5 seconds.

"""

import argparse
import MySQLdb
# Local module with DB configuration
import config



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

    def GetLastShot(self):
        c = self.db.cursor()
        query = (
                "SELECT id, shot FROM reports "
                "ORDER BY id DESC LIMIT 1")
        c.execute(query)
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
        Id, shot = self.GetLastShot()
        return Id, shot

    def BottlePressures(self, shot_id, phase):
        from epics import caget  # , caput  # , cainfo
        c = self.db.cursor()
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
            except MySQLdb._exceptions.IntegrityError:
                # Interpolate the values into the query
                # i_query = c.mogrify(query, (shot_id, b, phase,))
                print('(1062, Duplicate entry ')
                # Print the actual query executed
                print(c._last_executed)
                raise ValueError
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


def insert_report(db, series, shot, ce, re):
    c = db.cursor()
    query = ("INSERT INTO reports "
             "(id, esther_series_name, shot, chief_engineer_id, researcher_id) "
             "VALUES (NULL, %s, %s, %s, %s)")
    try:
        c.execute(query, (series, shot, ce, re,))
        db.commit()
    except MySQLdb._exceptions.IntegrityError:
        #  print("1062, Duplicate entry 'S-101' for key 'esther_series_name'")
        print(c.statement)
        print(query)
        exit(-1)

    Id, shot = get_last_shot(db)
    return Id, shot
    print(f"Id {Id}, {shot}")
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
    Id, shot = dB.GetLastShot()
    print(f"Id {Id}, {shot}")
    args = parser.parse_args()
    if (args.newReport):
        Id, shot = dB.InsertShot('S', shot + 1, 3, 1)
        print(f"Inserted {Id}, {shot}")
        dB.BottlePressures(Id, 'CC_Start')
        dB.BottlePressures(Id, 'End')
        # insert_report(db, 'S', 101, 3, 1)
        exit()
    if (args.test):
        #bottle_pressures(db, 303, 'CC_Start')
        exit()

    # args = parse_args()
# vim: syntax=python ts=4 sw=4 sts=4 sr et
