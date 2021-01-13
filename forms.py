from flask_wtf import FlaskForm
from flask import url_for
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email

class IncomeForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = StringField('Amount', validators = [DataRequired()])
    date = DateField('Date',  validators = [DataRequired()])


class SavingForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    tax = SelectField("Pre/Post Tax", choices = [("Pre-Tax"), ("Post-Tax")])
    amount = StringField('Amount', validators = [DataRequired()])
    date = DateField('Date', validators = [DataRequired()])


class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = StringField('Amount', validators = [DataRequired()])
    date = DateField('Date', validators = [DataRequired()])

class DateForm(FlaskForm):
  month = SelectField("Month", choices = [("01", "January"), ("02", "February"), ("03","March"), ("04", "April"), ("05", "May"), ("06", "June"), ("07", "July"), ("08", "August"), ("09", "September"), ("10",  "October"), ("11", "Novemeber"), ("12", "December")])
  year = SelectField("Year", choices = [("2017"),("2018"),("2019"), ("2020"),("2021"),("2022")])


class RegistrationForm(FlaskForm):
  username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
  email = StringField('Email', validators = [DataRequired(), Email()])
  password = PasswordField('Password', validators = [DataRequired()])
  confirmPassword = PasswordField('Confirm Password', validators = [DataRequired()])
  submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
  email = StringField('Email', validators = [DataRequired(), Email()])
  password = PasswordField('Password', validators = [DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')

class UpdateIncomeForm(FlaskForm):
  description = StringField('Description', validators=[DataRequired()])
  amount = StringField('Amount', validators = [DataRequired()])
  date = DateField('Date',  validators = [DataRequired()])

class UpdateExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = StringField('Amount', validators = [DataRequired()])
    date = DateField('Date', validators = [DataRequired()])

class UpdateSavingForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    tax = SelectField("Pre/Post Tax", choices = [("Pre-Tax"), ("Post-Tax")])
    amount = StringField('Amount', validators = [DataRequired()])
    date = DateField('Date', validators = [DataRequired()])
  




