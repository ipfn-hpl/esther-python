#!/usr/bin/env python3
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

        print("time %s" % prop['time'], end='')
        print(", temperatura %.2f ºC" % prop['temperatura'], end='')
        print(", pressao %.2f mBar" % prop['pressao'], end='')
        print(", humidade %.1f%%" % prop['humidade'])
