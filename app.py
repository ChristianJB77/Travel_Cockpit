#Libraries
import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#My functions
from helpers import login_required, apology
from input_classifier import check, loc_class
from link_maker import links
from weather_widget_maker import weather_widget
from covid_widget_maker import covid_widget
from info_widget_maker import info_widget
from holiday_widget_maker import holiday
#Specific addtional imports
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///travel_cockpit.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else: #POST
        #username input check, must be text
        username = request.form.get("username")
        if not username:
            return render_template("register.html",
                                    number = 1, message='Provide Username')
        #unique user name check
        rows = db.execute("SELECT username FROM users WHERE username = :username",
                            username=username)
        if len(rows) != 0:
            return render_template("register.html", number=1,
                                    message='Username is not available')
        #password and re-type check
        password = request.form.get("password")
        if not password:
            return render_template("register.html", number=1,
                                    message='Provide Password')
        confirmation = request.form.get("confirmation")
        if confirmation != password:
            return render_template("register.html", number=1,
                                    message='Re-type Password correctly')

        #hash password
        hash = generate_password_hash(password, method='pbkdf2:sha256',
                                        salt_length=8)
        #INSERT into db table users
        db.execute("INSERT INTO users (username, hash) VALUES (:name, :hash);",
                                        name=username, hash=hash)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        flash("You were successfully registered! Welcome :)")
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in with account"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", number=1,
                                    message="Sorry, USERNAME is missing!")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", number=1,
                                    message="Sorry, PASSWORD is missing!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", number=1,
                                message="Username Password combination WRONG!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        #Flash welcome user
        welcome = "Welcome " + request.form.get("username").lower().capitalize() + "!"
        flash(welcome)

        #Get current month for go warm
        current_month = datetime.datetime.now().month
        month_de = db.execute("SELECT name_de FROM months \
                    WHERE number=:current", current=current_month)[0]['name_de']
        go_warm = "https://www.reise-klima.de/urlaub/" + month_de

        return render_template("index.html", go_warm=go_warm)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change of user's password by user"""
    if request.method == "GET":
        return render_template("change_password.html")

    else: #Get
        id = session["user_id"]
        #Current password input check, input not empty
        current_password = request.form.get("current_password")
        if not current_password:
            return render_template("change_password.html", number = 1,
                                    message="Provide CURRENT Password!")
        #Check if current password is correct
        hash_dict = db.execute("SELECT hash FROM users WHERE id=:id", id=id)
        hash = hash_dict[0]["hash"]
        if not check_password_hash(hash, current_password):
            return render_template("change_password.html", number = 1,
                                    message= "Current Password is WRONG!")
        #Check if new password is not empty
        new_password = request.form.get("new_password")
        if not new_password:
            return render_template("change_password.html", number = 1,
                                    message="Provide NEW Password!")
        #Check if new confirmation is not empty and equal to new passowrd
        new_confirmation = request.form.get("new_confirmation")
        if new_confirmation != new_password:
            return render_template("change_password.html", number = 1,
                                    message="Re-type NEW Password CORRECTLY!")
        #Update users db with new Password
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256',
                                        salt_length=8)
        db.execute("UPDATE users SET hash=:new_hash WHERE id=:id",
                    id=id, new_hash=new_hash)

        flash("Password successfully changed")
        return redirect("/")



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        #Get current month for go warm on
        current_month = datetime.datetime.now().month
        month_de = db.execute("SELECT name_de FROM months \
                    WHERE number=:current", current=current_month)[0]['name_de']
        go_warm = "https://www.reise-klima.de/urlaub/" + month_de
        return render_template("index.html", go_warm=go_warm)

    else: #POST
        id = session["user_id"]
        #User input check, must be text
        #Formatting and classification with check function
        destination = request.form.get("destination")
        dest = check(destination)
        if not dest:
            return render_template("index.html", number=1,
                                    message="Please provide TRAVEL DESTINATION")

        #Get language switch value (English or German)
        switch = request.form.get("language")
        #Get location classes dictionary
        loc_classes = loc_class(dest)
        #Post default language to dropdwon on my dashboard
        if loc_classes['language'] == 'german':
            options = ["German", "English"]
        else:
            options = ["English", "German"]

        #Get button links dictionary
        links_dic = links(dest, loc_classes, switch)

        #weather widget
        weather = weather_widget(loc_classes, switch)

        #covid19 widget
        covid = covid_widget(loc_classes, switch)

        #info box widget
        info = info_widget(loc_classes, switch, weather)

        #national holidays widget
        holidays = holiday(loc_classes, switch)

        #Get current time
        time = datetime.datetime.now()

        #Destination for search history
        loc = loc_classes["loc_type"]
        if loc == "country":
            history = loc_classes["country_en"]
        elif loc == "big_city":
            history = loc_classes["city"]
        else:
            history = loc_classes["location"]

        #Insert into search history database
        db.execute("INSERT INTO search_history_user (user_id, destination, timestamp) \
                    VALUES (:user_id, :destination, :timestamp)",
                    user_id=id, destination=history, timestamp=time)


        return render_template("my_dashboard.html", switch=switch,
                                loc_classes=loc_classes, links_dic=links_dic,
                                options=options, weather=weather, covid=covid,
                                info=info, holidays=holidays)


@app.route("/my_dashboard")
@login_required
def my_dashboard():
    return render_template("my_dashboard.html")

@app.route("/history")
@login_required
def history():
    """Show user's search history"""
    id = session["user_id"]
    #Load search history
    rows = db.execute("SELECT destination, COUNT(id) \
                        FROM search_history_user \
                        WHERE user_id=:uid GROUP BY destination \
                        ORDER BY COUNT(id) DESC", uid=id)
    return render_template("history.html", rows=rows)

@app.route("/vision")
def vision():
    return render_template("vision.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
