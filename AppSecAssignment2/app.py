from flask import Flask, render_template, url_for, flash, redirect, request, session, escape
from flask_bcrypt import Bcrypt
import os
import subprocess

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
        if not username:
            flash("username blank, registration failure")
        elif username in registered_users:
            flash("username taken, registration failure")
        elif not password:
            flash("password blank, registration failure")
        elif not twofactor:
            flash("2fa blank, registration failure")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            registered_users[username] = [hashed_password, twofactor]
            flash("success, registration complete")
            return render_template("register.html")
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = escape(request.form["username"])
        password = escape(request.form["password"])
        twofactor = escape(request.form["twofactor"])
        if username in registered_users:
            if bcrypt.check_password_hash(registered_users[username][0], password):
                if twofactor == registered_users[username][1]:
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
            return render_template("misspelled.html", text=text, misspelled=misspelled)
        return render_template("spell_check.html")
    else:
        flash("login to see this page")
        return redirect(url_for("login"))
    flash("something broke")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
