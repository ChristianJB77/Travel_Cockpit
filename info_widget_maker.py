import os
import requests
import urllib.parse
from cs50 import SQL

import locale #Number 1000 comma separator

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///travel_cockpit.db")


def fx_rate(iso):
    """FX-rate"""
    try:
        info_fx = {}
        #FX-rate API -> Get JSON (https://exchangeratesapi.io/)
        currency = db.execute("SELECT iso4217_currency_aplhabetic_code \
                FROM data_hub_countries \
                WHERE LOWER(iso3166_1_alpha_2)=:iso",
                iso=iso)[0]["iso4217_currency_aplhabetic_code"]

        cur_name = db.execute("SELECT ISO4217_currency_name \
                FROM data_hub_countries \
                WHERE LOWER(iso3166_1_alpha_2)=:iso",
                iso=iso)[0]["ISO4217_currency_name"]

        #Exchange rate API url
        url = "https://api.exchangeratesapi.io/latest?symbols=USD," + currency
        #If requested country is using Euro, get only USD
        if currency == "EUR":
            url = "https://api.exchangeratesapi.io/latest?symbols=USD"

        cur_list = requests.get(url).json()

        if currency == "EUR":
            info_fx["eur_usd"] = round(cur_list["rates"]["USD"], 2)
            info_fx["100_usd"] = round(100 / cur_list["rates"]["USD"], 2)
            info_fx["cur_name"] = "Euro"
        else:
            info_fx["cur_eur"] = round(cur_list["rates"][currency], 2)
            info_fx["cur_usd"] = round(info_fx["cur_eur"] / cur_list["rates"]["USD"], 2)
            info_fx["eur_usd"] = round(cur_list["rates"]["USD"], 2)
            info_fx["cur_name"] = cur_name
            #Get feeling for local expenses, idea 100 bucks of local currency in EUR
            feeling = round(100 / cur_list["rates"][currency], 2)
            #If 100 bucks in local currency are smaller than 10 EUR, then scale up
            factor = 100
            while feeling < 10:
                feeling *= 10
                factor *= 10

            #1000 , splitter for readability
            locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
            factor_read = f'{factor:n}'

            info_fx["feeling_cur"] = round(feeling, 1)
            info_fx["feeling_factor"] = factor_read

        return info_fx

    except:
        print("######## ERROR FX-rate #########")
        info_fx = {}
        return info_fx


def info_widget(loc_classes, switch, weather):
    """Info box widget with relevant country data"""

    try:
        if loc_classes["country_iso"]:
            info = {}
            iso = loc_classes["country_iso"]

            """FX-rate function"""
            info = fx_rate(iso)

            """Language differing titles/phrases"""
            #German
            if switch == "German" or loc_classes['language'] == 'german':
                info["country"] = loc_classes["country_de"].title()
                info["title_euro"] = "Wechselkurse Euroländer"
                info["title"] = "Wechselkurse"
            #English:
            else:
                info["country"] = loc_classes["country_en"].title()
                info["title_euro"] = "FX box Euro countries"
                info["title"] = "FX box"


            """GDP and population"""
            #World Band database needs iso3 country code
            iso_3 = db.execute("SELECT iso316_1_alpha_3 FROM data_hub_countries \
                                WHERE LOWER(iso3166_1_alpha_2)=:iso",
                                iso=iso)[0]["iso316_1_alpha_3"]
            #Country population in millions
            pop = db.execute("SELECT * FROM world_bank WHERE (CountryCode=:iso \
                                AND (SeriesCode='SP.POP.TOTL'))",
                                iso=iso_3)[0]["2019"]
            pop = round(int(pop) / (1000 * 1000), 1)
            info["pop"] = pop
            #GDP per capita
            gdp = db.execute("SELECT * FROM world_bank WHERE (CountryCode=:iso \
                                AND (SeriesCode='NY.GDP.PCAP.CD'))",
                                iso=iso_3)[0]["2019"]
            #Convert from USD to EUR
            gdp_raw = 0.0
            gdp_cur = 0
            #Try/except loop, if fx-rate not available at API
            try:
                gdp_raw = round(float(gdp) / info["eur_usd"])
                gdp_cur = "Euro"

            except:
                gdp_raw = round(float(gdp))
                gdp_cur = "USD"

            #1000 , splitter for readability
            locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
            gdp = f'{gdp_raw:n}'
            info["gdp"] = gdp
            info["gdp_cur"] = gdp_cur

            """Capital, Internet domain, Country phone code"""
            #Capital
            capital = db.execute("SELECT capital FROM data_hub_countries \
                                    WHERE LOWER(iso3166_1_alpha_2)=:iso",
                                    iso=iso)[0]["capital"]
            info["capital"] = capital
            #Internet domain
            internet = db.execute("SELECT tld FROM data_hub_countries \
                                    WHERE LOWER(iso3166_1_alpha_2)=:iso",
                                    iso=iso)[0]["tld"]
            info["internet"] = internet
            #country phone code
            phone = db.execute("SELECT dial FROM data_hub_countries \
                                    WHERE LOWER(iso3166_1_alpha_2)=:iso",
                                    iso=iso)[0]["dial"]
            info["phone"] = "+" +  phone


            """GMT time zone"""
            #Get time zone delta from weather dictionary
            time_zone = weather[0]["hour_offset"]
            zone = 0

            #Exception/error errorhandler
            if iso == "cn":
                gmt = "+8"

            else:
                if (int(time_zone) - time_zone) == 0:
                    zone = round(time_zone)
                    if zone > 0:
                        gmt = "+" + str(zone)
                    else:
                        gmt = str(zone)
                else:
                    zone = time_zone
                    if zone > 0:
                        gmt = "+" + str(zone)
                    else:
                        gmt = str(zone)

            info["time_zone"] = gmt


        print("############", info)
        return info

    except:
        print("######## ERROR #########")
        return None
