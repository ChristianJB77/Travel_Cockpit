import os
import requests
import urllib.parse
from cs50 import SQL

from datetime import datetime
import statistics


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///travel_cockpit.db")

def covid_widget(loc_classes, switch):
    """Covid19 Graph Widget (https://covid19api.com/)"""

    try:
        if loc_classes["country_iso"] and not loc_classes["country_iso"] == "us":
            #Available countries -> ISO2 to html slug converter
                #https://api.covid19api.com/countries
            slug = db.execute("SELECT slug FROM covid_countries \
                                WHERE LOWER(iso2)=:iso",
                                iso=loc_classes["country_iso"])[0]["slug"].lower()

            #Get COVID19 API data
            url = "https://api.covid19api.com/dayone/country/" + slug
            covid_list = requests.get(url).json()

            #Each list item = 1 day, calculate new cases/detas per day of aggregated data
            covid = {}
            covid_case_total = []
            covid_case_day = []
            covid_death_total = []
            covid_death_day = []
            covid_dates = []

            if covid_list:
                #Inital start -> Daily and total cases are equal
                covid_case_day.append(covid_list[0]["Confirmed"])
                covid_case_total.append(covid_list[0]["Confirmed"])
                covid_death_day.append(covid_list[0]["Deaths"])
                covid_death_total.append(covid_list[0]["Deaths"])
                #Get datetime labels
                today = covid_list[0]["Date"][:10]
                today = datetime.strptime(today, '%Y-%m-%d')
                covid_dates.append(today.strftime('%d.%m.%y'))

                for i in range(1, len(covid_list)):
                    if covid_list[i]["Province"] == "":
                        #Calculate daily new cases by delta of day before
                        case_today = covid_list[i]["Confirmed"] - covid_case_total[-1]
                        covid_case_day.append(case_today)
                        covid_case_total.append(covid_list[i]["Confirmed"])

                        death_today = covid_list[i]["Deaths"] - covid_death_total[-1]
                        covid_death_day.append(death_today)
                        covid_death_total.append(covid_list[i]["Deaths"])
                        #Get datetime labels
                        today = covid_list[i]["Date"][:10]
                        today = datetime.strptime(today, '%Y-%m-%d')
                        covid_dates.append(today.strftime('%d.%m.%y'))

                #Smoothen curve, especially often missing weekend data
                cov_case_mean = []
                for i in range(len(covid_case_day)):
                    if i < 13:
                        cov_case_mean.append(covid_case_day[i])
                    else:
                        cov_case_mean.append(statistics.mean(covid_case_day[(i - 13):i]))

                cov_death_mean = []
                for i in range(len(covid_death_day)):
                    if i < 13:
                        cov_death_mean.append(covid_death_day[i])
                    else:
                        cov_death_mean.append(statistics.mean(covid_death_day[(i - 13):i]))


                covid["cases"] = cov_case_mean
                covid["deaths"] = cov_death_mean
                covid["dates"] = covid_dates


                return covid


    except:
        return None
