from flask import Flask, render_template, url_for, flash, redirect, request, session, escape
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, UniqueConstraint, ForeignKey, func
from sqlalchemy.sql import select
import os
import subprocess

engine = create_engine('sqlite:///backend.db', echo = True)
meta = MetaData()
users = Table(
    'users', meta,
    Column('usrnm', String, unique = True, primary_key = True),
    Column('psswrd', String),
    Column('twfctr', String),
    Column('logins', String),
    Column('logouts', String),
)
spellchecks = Table(
    'spellchecks', meta,
    Column('id', Integer, primary_key = True),
    Column('users_usrnm', None, ForeignKey('users.usrnm')),
    Column('sc_text', String),
)
meta.create_all(engine)
conn = engine.connect()
conn.execute(users.delete())
conn.execute(spellchecks.delete())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
bcrypt = Bcrypt(app)

registered_users = {}

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
        conn = engine.connect()
        database_all_usernames = conn.execute(select_all_usernames)
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
            conn = engine.connect()
            result = conn.execute(ins)
            return render_template("register.html")
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = escape(request.form["username"])
        password = escape(request.form["password"])
        twofactor = escape(request.form["twofactor"])
        select_username = select([users.c.usrnm]).where(users.c.usrnm == username)
        conn = engine.connect()
        select_username_result = conn.execute(select_username)
        get_username = select_username_result.fetchone()
        try:
            database_username = get_username['usrnm']
        except:
            flash("unregistered user")
            return render_template("login.html")
        #if username in registered_users:
        if username == database_username:
            select_password = select([users.c.psswrd]).where(users.c.usrnm == username)
            select_password_result = conn.execute(select_password)
            get_password = select_password_result.fetchone()
            database_password = get_password['psswrd']
            #if bcrypt.check_password_hash(registered_users[username][0], password):
            if bcrypt.check_password_hash(database_password,password):
                select_twofactor = select([users.c.twfctr]).where(users.c.twfctr == twofactor)
                select_twofactor_ruselt = conn.execute(select_twofactor)
                get_twofactor = select_twofactor_ruselt.fetchone()
                database_twofactor = get_twofactor['twfctr']
                if twofactor == database_twofactor:
                    flash("login success")
                    session["username"] = username
                    return redirect(url_for("home"))
                else:
                    flash("two factor failure")
                    return render_template("login.html")
            else:
                flash("invalid password")
                return render_template("login.html")
        else:
            flash("invalid username")
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
            ins = spellchecks.insert().values(users_usrnm=username, sc_text=text)
            conn = engine.connect()
            result = conn.execute(ins)
            return render_template("misspelled.html", text=text, misspelled=misspelled)
        return render_template("spell_check.html")
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

@app.route("/history")
def history():
    if "username" in session:
        username = session["username"]
        flash(f"logged in as {username}")
        select_queryID = select([spellchecks.c.id]).where(spellchecks.c.users_usrnm == username)
        select_querytext = select([spellchecks.c.sc_text]).where(spellchecks.c.users_usrnm == username)
        select_numqueries = select([func.count()]).where(spellchecks.c.users_usrnm == username)
        conn = engine.connect()
        select_queryID_result = conn.execute(select_queryID)
        select_querytext_result = conn.execute(select_querytext)
        select_numqueries_result = conn.execute(select_numqueries)
        get_queryIDs = select_queryID_result.fetchall()
        get_querytexts = select_querytext_result.fetchall()
        get_numqueries = select_numqueries_result.fetchone()
        query_IDs = []
        query_texts = []
        for row in get_queryIDs:
            query_IDs.append("query"+str(row['id']))
            # print("appending query_id")
        for row in get_querytexts:
            query_texts.append(row['sc_text'])
            # print("appending query_text")
        return render_template("history.html", querycount=get_numqueries[0], querynums = query_IDs, querytexts = query_texts)
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
