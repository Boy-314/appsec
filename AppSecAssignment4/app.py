from redis import Redis
from flask import Flask, render_template, url_for, flash, redirect, request, session, escape
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, UniqueConstraint, ForeignKey, func, update
from sqlalchemy.sql import select
from flask_wtf.csrf import CSRFProtect
import os
import subprocess
from datetime import datetime

engine = create_engine('sqlite:///backend.db', echo = True)
meta = MetaData()
users = Table(
    'users', meta,
    Column('usrnm', String, unique = True, primary_key = True),
    Column('psswrd', String),
    Column('twfctr', String),
)
spellchecks = Table(
    'spellchecks', meta,
    Column('id', Integer, primary_key = True),
    Column('users_usrnm', None, ForeignKey('users.usrnm')),
    Column('sc_text', String),
    Column('sc_output', String),
)
logs = Table(
    'logs', meta,
    Column('id', Integer, primary_key = True),
    Column('users_usrnm', None, ForeignKey('users.usrnm')),
    Column('login', String),
    Column('logout', String),
)

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
app.config['SECRET_KEY'] = os.urandom(16)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

meta.create_all(engine)
conn = engine.connect()
conn.execute(users.delete())
conn.execute(spellchecks.delete())
conn.execute(logs.delete())
pword = bcrypt.generate_password_hash("Administrator@1").decode("utf-8")
insert_admin_account = users.insert().values(usrnm = "admin", psswrd = pword, twfctr = "12345678901")
conn.execute(insert_admin_account)
conn.close()

registered_users = {}
log_id = -1

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = escape(request.form["username"])
        password = escape(request.form["password"])
        twofactor = escape(request.form["twofactor"])
        select_all_usernames = select([users.c.usrnm])
        connregister = engine.connect()
        database_all_usernames = connregister.execute(select_all_usernames)
        name_taken = False
        for i in database_all_usernames:
            # print(i['usrnm'])
            if i['usrnm'] == username:
                name_taken = True
        if not username:
            flash("username blank, registration failure")
        elif name_taken == True:
            flash("username taken, registration failure")
        elif not password:
            flash("password blank, registration failure")
        elif not twofactor:
            flash("2fa blank, registration failure")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            #registered_users[username] = [hashed_password, twofactor]
            flash("success, registration complete")
            ins = users.insert().values(usrnm = username, psswrd = hashed_password, twfctr = twofactor)
            result = connregister.execute(ins)
            connregister.close()
            return render_template("register.html")
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = escape(request.form["username"])
        password = escape(request.form["password"])
        twofactor = escape(request.form["twofactor"])
        select_username = select([users.c.usrnm]).where(users.c.usrnm == username)
        connlogin = engine.connect()
        select_username_result = connlogin.execute(select_username)
        get_username = select_username_result.fetchone()
        try:
            database_username = get_username['usrnm']
        except:
            flash("unregistered user")
            connlogin.close()
            return render_template("login.html")
        #if username in registered_users:
        if username == database_username:
            select_password = select([users.c.psswrd]).where(users.c.usrnm == username)
            select_password_result = connlogin.execute(select_password)
            get_password = select_password_result.fetchone()
            database_password = get_password['psswrd']
            #if bcrypt.check_password_hash(registered_users[username][0], password):
            if bcrypt.check_password_hash(database_password,password):
                select_twofactor = select([users.c.twfctr]).where(users.c.twfctr == twofactor)
                select_twofactor_ruselt = connlogin.execute(select_twofactor)
                get_twofactor = select_twofactor_ruselt.fetchone()
                try:
                    database_twofactor = get_twofactor['twfctr']
                except:
                    flash("two factor failure")
                    connlogin.close()
                    return render_template("login.html")
                if twofactor == database_twofactor:
                    flash("login success")
                    session["username"] = username
                    login_time = datetime.now()
                    ins = logs.insert().values(users_usrnm=username, login=login_time, logout="N/A")
                    result = connlogin.execute(ins)
                    log_id = result.inserted_primary_key
                    connlogin.close()
                    return redirect(url_for("login"))
                else:
                    flash("two factor failure")
                    connlogin.close()
                    return render_template("login.html")
            else:
                flash("invalid password")
                connlogin.close()
                return render_template("login.html")
        else:
            flash("invalid username")
            connlogin.close()
            return render_template("login.html")
    return render_template("login.html")

@app.route("/spell_check", methods=["POST", "GET"])
def spell_check():
    if "username" in session:
        username = session["username"]
        flash(f"logged in as {username}")
        if request.method == "POST":
            text = escape(request.form["spellcheck"])
            input_file = open("text.txt","w")
            input_file.write(text)
            input_file.close()
            output_file = open("misspelled.txt","w")
            subprocess.call(["./spell_check","text.txt","wordlist.txt"], stdout=output_file)
            output_file.close()
            output_file = open("misspelled.txt","r")
            misspelled = output_file.read()
            output_file.close()
            ins = spellchecks.insert().values(users_usrnm=username, sc_text=text, sc_output=misspelled)
            connspellcheck = engine.connect()
            connspellcheck.execute(ins)
            connspellcheck.close()
            return render_template("misspelled.html", text=text, misspelled=misspelled)
        return render_template("spell_check.html")
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

@app.route("/history", methods=["POST", "GET"])
def history():
    if "username" in session:
        username = session["username"]
        flash(f"logged in as {username}")
        select_queryID = select([spellchecks.c.id]).where(spellchecks.c.users_usrnm == username)
        select_querytext = select([spellchecks.c.sc_text]).where(spellchecks.c.users_usrnm == username)
        select_numqueries = select([func.count()]).where(spellchecks.c.users_usrnm == username)
        connhistory = engine.connect()
        query_IDs = []
        query_texts = []
        if request.method == "POST":
            adminrequest_user = escape(request.form["userquery"])
            select_queryID = select([spellchecks.c.id]).where(spellchecks.c.users_usrnm == adminrequest_user)
            select_querytext = select([spellchecks.c.sc_text]).where(spellchecks.c.users_usrnm == adminrequest_user)
            select_numqueries = select([func.count()]).where(spellchecks.c.users_usrnm == adminrequest_user)
            select_queryID_result = connhistory.execute(select_queryID)
            select_querytext_result = connhistory.execute(select_querytext)
            select_numqueries_result = connhistory.execute(select_numqueries)
            get_queryIDs = select_queryID_result.fetchall()
            get_querytexts = select_querytext_result.fetchall()
            get_numqueries = select_numqueries_result.fetchone()
            for row in get_queryIDs:
                query_IDs.append("query"+str(row['id']))
                # print("appending query_id")
            for row in get_querytexts:
                query_texts.append(row['sc_text'])
                # print("appending query_text")
            connhistory.close()
            return render_template("history.html", loggedin = adminrequest_user, querycount=get_numqueries[0], querynums = query_IDs, querytexts = query_texts)
        else:
            select_queryID_result = connhistory.execute(select_queryID)
            select_querytext_result = connhistory.execute(select_querytext)
            select_numqueries_result = connhistory.execute(select_numqueries)
            get_queryIDs = select_queryID_result.fetchall()
            get_querytexts = select_querytext_result.fetchall()
            get_numqueries = select_numqueries_result.fetchone()
            for row in get_queryIDs:
                query_IDs.append("query"+str(row['id']))
                # print("appending query_id")
            for row in get_querytexts:
                query_texts.append(row['sc_text'])
                # print("appending query_text")
            connhistory.close()
            return render_template("history.html", loggedin = username, querycount=get_numqueries[0], querynums = query_IDs, querytexts = query_texts)
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

@app.route("/history/<id>")
def query(id):
    if "username" in session:
        username = session["username"]
        idnum = id[5:]
        connquery = engine.connect()
        select_username = select([spellchecks.c.users_usrnm]).where(spellchecks.c.id == idnum)
        select_querytext = select([spellchecks.c.sc_text]).where(spellchecks.c.id == idnum)
        select_outputtext = select([spellchecks.c.sc_output]).where(spellchecks.c.id == idnum)
        query_user_result = connquery.execute(select_username)
        querytext_result = connquery.execute(select_querytext)
        query_outputtext_result = connquery.execute(select_outputtext)
        get_query_user = query_user_result.fetchone()
        get_querytext = querytext_result.fetchone()
        get_outputtext = query_outputtext_result.fetchone()
        query_user = get_query_user["users_usrnm"]
        query_text = get_querytext["sc_text"]
        output_text = get_outputtext["sc_output"]
        if username == "admin" or query_user == username:
            connquery.close()
            return render_template("query.html", queryid=idnum, loggedin=query_user, querytext=query_text, output=output_text)
        else:
            flash("you are not authorized to see this page")
            connquery.close()
            return redirect(url_for("login"))
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

@app.route("/login_history", methods=["POST", "GET"])
def login_history():
    if "username" in session:
        username = session["username"]
        if username == "admin":
            if request.method == "POST":
                requested_user = escape(request.form["loginhistory"])
                select_all_logs_for_user = select([logs]).where(logs.c.users_usrnm == requested_user)
                connloginhistory = engine.connect()
                result = connloginhistory.execute(select_all_logs_for_user)
                get_logs = result.fetchall()
                user_logs = []
                for row in get_logs:
                    user_logs.append(row)
                if len(user_logs) < 1:
                    flash("user not found")
                    connloginhistory.close()
                    return redirect(url_for("home"))
                else:
                    num_user_logs = len(user_logs)
                    log_ID_nums = []
                    login_times = []
                    logout_times = []
                    for row in get_logs:
                        log_ID_nums.append(row['id'])
                        login_times.append(row['login'])
                        logout_times.append(row['logout'])
                    connloginhistory.close()
                    return render_template("showlogs.html", userlogs = num_user_logs, logIDnums = log_ID_nums, logintimes = login_times, logouttimes = logout_times)
            return render_template("login_history.html")
        else:
            flash("you are not authorized to see this page")
            return redirect(url_for("login"))
    else:
        flash("you are not authorized to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        logout_time = datetime.now()
        update_log = update(logs).where(logs.c.users_usrnm == username).values(logout=logout_time)
        connlogout = engine.connect()
        connlogout.execute(update_log)
        session.clear()
        flash("logged out")
        connlogout.close()
        return redirect(url_for("login"))
    else:
        flash("login first before logging out you dummy")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
