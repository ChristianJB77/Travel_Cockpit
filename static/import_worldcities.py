# Libraries
import sqlite3
import csv
from sys import argv, exit

# User input incl. checker (python import.py worldcities.csv)
if len(argv) != 2:
    print("Uasge: python import_worldcities.py filename.csv")
    exit(1)

data = argv[1]

#Database init
conn = sqlite3.connect('travel_cockpit.db')
db = conn.cursor()

# Open csv file given by command line
with open(data, newline = '', encoding="utf8") as csv_file:
    geodata = csv.reader(csv_file)
    for data in geodata:
        if data[0] != 'city':
            # Insert csv entry into db
            db.execute("INSERT INTO geodata \
            (city, city_ascii, lat, lng, country, iso2, iso3, state, id_geo)\
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[10]))

            conn.commit()

conn.close()

#Copyright (c) 2008 MaxMind Inc.  All Rights Reserved.
#OPEN DATA LICENSE for MaxMind WorldCities and Postal Code Databases
#Copyright (c) 2008 MaxMind Inc.  All Rights Reserved.
