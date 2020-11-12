# Libraries
import sqlite3
import csv
from sys import argv, exit

# User input incl. checker (python import.py worldcities.csv)
if len(argv) != 2:
    print("Uasge: python import_population.py filename.csv")
    exit(1)

data = argv[1]

#Database init
conn = sqlite3.connect('travel_cockpit.db')
db = conn.cursor()

# Open csv file given by command line
with open(data, newline = '', encoding="utf8") as csv_file:
    geodata = csv.reader(csv_file)
    for data in geodata:
        if data[0] != 'country':
            # Insert csv entry into db
            db.execute("INSERT INTO population \
            (country, city, accentCity, region, population, latitude, longitude)\
            VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data[0], data[1], data[2], data[3], data[4], data[5], data[6]))

            conn.commit()

conn.close()

#Free database from:
#OPEN DATA LICENSE for MaxMind WorldCities and Postal Code Databases
#Copyright (c) 2008 MaxMind Inc.  All Rights Reserved.
