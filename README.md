# Travel Cockpit
CS50 final project -> All that we ask is that you build something of interest to you, that you solve an actual problem, that you impact your community, or that you change the world. Strive to create something that outlives this course.

## Purpose
As passionate travelers my wife and me were continuously looking for a central
Travel Cockpit to get all essential information necessary to plan a trip in one
tool or view. To avoid the tedious googling for each source and forgetting
always at least one important info.
Then especially in COVID-19 times it was waste of time to prepare long time
planned trips.
As nothing similar is existing, I have developed a Travel Cockpit, which makes
a spontaneous trip planning easy and efficient.

## Concept
User can search for his desired travel destination or get a suggestion of currently
warm places on the planet. The destination can be a country, city or for a good
luck search any place/region.
Based on the user's search a desktop consisting of tailored widgets and button
links appears. As the main target is to inform the user with all essential travel
information in one view or one click away.

This Web (HTML) based dashboard, which works on a Smart TV, Desktop and mobile
device focuses the European and especially German traveler. Therefore the dashboard
search function works in German and English with language specific travel links.

### Functionality
Flask web server with HTML/CSS frontend, SQL database and custom Python functions.

#### Frontend
- HTML pages with Bootstrap powered styling and own customization in CSS.
- Conditional logic for a smart and flexible HTML to adapt on existing content
with Jinja.
- Icons from Font Awesome.
- Background pictures from private picture collection.

#### Backend
Python Flask web server handles:
- All html routes
- Conditional logic
- Custom Python functions:
    - User management in combination with SQL database
    - User input debugging and formatting
    - Search algorithm in German/English, iso2 or iso3 country code
    - One click links to external pages with direct entrance
    - API backed live widgets
    - SQL database backed widgets
    - User search history stored in SQL database

- SQL database connection to store user data, search algorithm and data library
