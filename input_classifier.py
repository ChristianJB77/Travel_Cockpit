import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///travel_cockpit.db")

def check(destination):
    """Check and format user input"""
    #Format user input
    try:
        dest = destination.replace("-", " ").lower()
        dest = dest.replace("_", " ")
        dest = dest.replace(",", "")
        return dest

    except (KeyError, TypeError, ValueError):
        return None

def loc_class(dest):
    """Classify location (country/city/other), trnalsate to GER and ENG"""
    dest = dest.lower()
    dest_no_space = dest.replace(" ", "")
    dest_up = dest.upper()
    dest_dic = {}

    ###Country check
    #Country check English or ISO
    if db.execute("SELECT * FROM data_hub_countries \
                    WHERE (LOWER(country_name) =:dest \
                    OR LOWER(official_name_english)=:dest \
                    OR LOWER(iso316_1_alpha_3)=:dest\
                    OR LOWER(iso3166_1_alpha_2)=:dest\
                    OR LOWER(iso4217_currency_country_name)=:dest)", dest=dest):
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = db.execute("SELECT iso3166_1_alpha_2 FROM data_hub_countries \
                    WHERE (LOWER(country_name)=:dest \
                    OR LOWER(official_name_english) =:dest \
                    OR LOWER(iso316_1_alpha_3)=:dest \
                    OR LOWER(iso3166_1_alpha_2)=:dest \
                    OR LOWER(iso4217_currency_country_name)=:dest)",
                    dest=dest)[0]['iso3166_1_alpha_2'].lower()
        dest_dic['country_iso'] = country_iso
        #Translate to English and German
        dest_dic['country_de'] = db.execute("SELECT de FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['de'].lower()
        dest_dic['country_en'] = db.execute("SELECT en FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['en'].lower()
        #Language tag
        dest_dic['language'] = "english"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_en'].title()

        return dest_dic

    #Country check GERMAN
    elif db.execute("SELECT * FROM countries_translate \
                    WHERE LOWER(de)=(:dest)", dest=dest):
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = db.execute("SELECT code FROM countries_translate \
                        WHERE LOWER(de)=:dest", dest=dest)[0]['code'].lower()
        dest_dic['country_iso'] = country_iso
        #Translate to English and German
        dest_dic['country_de'] = db.execute("SELECT de FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['de'].lower()
        dest_dic['country_en'] = db.execute("SELECT en FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['en'].lower()

        dest_dic['language'] = "german"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic

    #Replace space in German and try again
    elif db.execute("SELECT * FROM countries_translate \
                    WHERE LOWER(de)=:dest", dest=dest_no_space):
        dest = dest_no_space
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = db.execute("SELECT code FROM countries_translate \
                        WHERE LOWER(de)=:dest", dest=dest)[0]['code'].lower()
        dest_dic['country_iso'] = country_iso
        #Translate to English and German
        dest_dic['country_de'] = db.execute("SELECT de FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['de'].lower()
        dest_dic['country_en'] = db.execute("SELECT en FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['en'].lower()

        dest_dic['language'] = "german"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic

    #All to upper case debugging for special character ä, ö, ü
    elif db.execute("SELECT * FROM countries_translate \
                    WHERE UPPER(de)=:dest", dest=dest_up):
        dest = dest_up
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = db.execute("SELECT code FROM countries_translate \
                        WHERE UPPER(de)=:dest", dest=dest)[0]['code'].lower()
        dest_dic['country_iso'] = country_iso
        #Translate to English and German
        dest_dic['country_de'] = db.execute("SELECT de FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['de'].lower()
        dest_dic['country_en'] = db.execute("SELECT en FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['en'].lower()

        dest_dic['language'] = "german"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic


    ###City check
    #Big city check
    elif db.execute("SELECT * FROM geodata WHERE (LOWER(city)=:dest \
                    OR LOWER(city_ascii)=:dest)", dest=dest):
        #Location type for link functions
        dest_dic['loc_type'] = "big_city"
        #Get city name
        city = db.execute("SELECT city_ascii FROM geodata \
                    WHERE (LOWER(city)=:dest OR \
                    LOWER(city_ascii)=:dest)", dest=dest)[0]['city_ascii'].lower()
        dest_dic['city'] = city
        #Get ISO alpha2 code
        country_iso = db.execute("SELECT iso2 FROM geodata WHERE \
                        LOWER(city_ascii)=:dest", dest=city)[0]['iso2'].lower()
        dest_dic['country_iso']  = country_iso
        #Get country of city in English and German
        dest_dic['country_de'] = db.execute("SELECT de FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['de'].lower()
        dest_dic['country_en'] = db.execute("SELECT en FROM countries_translate WHERE \
                    LOWER(code)=:iso", iso=country_iso)[0]['en'].lower()

        dest_dic['language'] = "unclear"
        #Print out for html title
        dest_dic['print'] = dest_dic['city'].title()
        return dest_dic


    ###Good luck, country and city unknown
    else:
        dest_dic['loc_type'] = "good_luck"
        dest_dic['location'] = dest
        dest_dic['language'] = "unclear"
        #Print out for html title
        dest_dic['print'] = "Good Luck Mode for: " + dest_dic['location'].title()
        return dest_dic
