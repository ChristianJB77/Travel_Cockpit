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
        if data[0] != 'country_name':
            # Insert csv entry into db
            db.execute("INSERT INTO  data_hub_countries\
            (country_name, official_name_english, iso3166_1_alpha_2, iso316_1_alpha_3,\
            m49, itu, marc, wmo, ds, dial, fifa, fips, gaul, ioc, iso4217_currency_aplhabetic_code,\
            iso4217_currency_country_name, iso4217_curreny_minor_unit, ISO4217_currency_name,\
            iso4217_currency_numeric_code, is_independent, capital, continent, tld, languages,\
            geo_name_id, edgar)\
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data))

            conn.commit()

conn.close()



#From data hub
#https://datahub.io/JohnSnowLabs/iso-3166-country-codes-itu-dialing-codes-iso-4217-currency-codes#python
