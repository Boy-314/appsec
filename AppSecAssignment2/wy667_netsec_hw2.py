from flask import Flask, flash, redirect, url_for, request, redirect, render_template, session, abort
from forms import RegistrationForm, LoginForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ed2c7a61471782f39ffd7064cb8bb874'

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/your/webroot/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash('Account created for {}.'.format(form.username.data), 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title = 'Register', form = form)

@app.route('/your/webroot/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.username.data == 'testusername' and form.password.data == 'testpassword':
			flash('logged in successfully', 'success')
			return redirect(url_for('home'))
		else:
			flash('log in failure', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@app.route('/your/webroot/spell_check/')
def spell_check():
	return 'spell_check'

if __name__ == '__main__':
	app.secret_key = os.urandom(256)
	app.run(debug = True)
