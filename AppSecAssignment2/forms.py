from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    two_factor = PasswordField('2FA', validators = [DataRequired()])
    register = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    password = PasswordField('Password', validators = [DataRequired()])
    two_factor = PasswordField('2FA', validators = [DataRequired()])
    login = SubmitField('Login')
