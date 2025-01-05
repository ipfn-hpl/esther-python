#!/home/esther/.local/venvs/python-epics/bin/python3
#
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"idEstacao": 1210762,
"localEstacao": "Lisboa, Tapada da Ajuda",

"idEstacao": 7240919,
"localEstacao": "Lisboa, Amoreiras (Lic. Franc\u00eas)",

"idEstacao": 1200535,
"localEstacao": "Lisboa (Geof\u00edsico)",

"idEstacao": 1200579,
"localEstacao": "Lisboa (G.Coutinho)",

"""
import geojson
import urllib.request
from epics import caput  # , cainfo
# import pprint as pp

IPMA_URL = 'https://api.ipma.pt/open-data/observation/meteorology/stations/obs-surface.geojson'
file = 'obs-surface.geojson'
with open(file, 'r') as file:
    gj2 = geojson.load(file)

with urllib.request.urlopen(IPMA_URL) as url:
    gj = geojson.load(url)
    # data = json.load(url)
# Now, let's print the GeoJSON data to understand its structure
# pp.pprint(dict(gj))
features = gj['features']
printLoc = True
for feat in features:
    prop = feat['properties']
    if feat['properties']['idEstacao'] == 1200579:
        if printLoc:
            printLoc = False
            print(feat['properties']['localEstacao'])

        temp = prop['temperatura']
        print("time %s" % prop['time'], end='')
        print(", temperatura %.2f ºC" % temp, end='')
        press = prop['pressao']
        print(", pressao %.2f mBar" % prop['pressao'], end='')
        hum = prop['humidade']
        print(", humidade %.1f%%" % prop['humidade'])
        caput('Esther:gas:Pressure', press)
        caput('Esther:gas:Humidity', hum)
