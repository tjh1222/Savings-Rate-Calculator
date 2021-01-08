from flask import Flask, url_for, render_template, redirect, flash
from forms import IncomeForm, SavingForm, ExpenseForm, DateForm, RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, and_
from datetime import datetime, date


from savingsRate import Person, IncomeItem, ExpenseItem, SavingItem
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user
import calendar





import os


SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

DATABASE_PATH = 'sqlite:////' + os.path.join(os.getcwd(), "test.db")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_PATH
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(20), unique = True, nullable = False)
  email = db.Column(db.String(120), unique = True, nullable = False)
  password = db.Column(db.String(60), nullable = False)
  incomes = db.relationship('Income', backref = 'owner', lazy = True)
  expenses = db.relationship('Expense', backref = 'owner', lazy = True)
  savings = db.relationship('Saving', backref = 'owner', lazy = True)


  def __repr__(self):
    return f"User({self.username}, {self.email})"




class Income(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  description = db.Column(db.String, nullable = False)
  amount = db.Column(db.String, nullable = False)
  date = db.Column(db.Date, nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

  def __repr__(self):
    return f"Income({self.description}, {self.amount}, {self.date})"

class Saving(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  description = db.Column(db.String, nullable = False)
  tax = db.Column(db.String, nullable = False)
  amount = db.Column(db.String, nullable = False)
  date = db.Column(db.Date, nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)


  def __repr__(self):
    return f"Saving({self.description}, {self.tax}, {self.amount}, {self.date})"



class Expense(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  description = db.Column(db.String, nullable = False)
  amount = db.Column(db.String, nullable = False)
  date = db.Column(db.Date, nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

  def __repr__(self):
    return f"Expense({self.description}, {self.amount}, {self.date})"


@app.route('/trend')
def trend():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))
  
  return render_template('trend.html')
  



@app.route('/', methods = ['GET', 'POST'])

def index():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))

  p = Person(current_user.username)
  
  form = DateForm()
  month = datetime.now().month
  if int(month) < 10:
    month = "0" + str(month)
  year = datetime.now().year

  
  
  
  if form.validate_on_submit():

    month = form.month.data
    year = form.year.data

    fullDate = "%" + str(year) + "-" + str(month) + "%"
    print(fullDate)
    month = calendar.month_name[int(month)]
    incomes = Income.query.filter(and_(Income.date.like(fullDate), current_user.id == Income.user_id)).all()
    expenses = Expense.query.filter(and_(Expense.date.like(fullDate), current_user.id == Expense.user_id)).all()
    savings = Saving.query.filter(and_(Saving.date.like(fullDate), current_user.id == Saving.user_id)).all()
    for income in incomes:
      temp = IncomeItem(income.description, income.amount)
      p.addIncome(temp)
    for expense in expenses:
      temp = ExpenseItem(expense.description, expense.amount)
      p.addExpense(temp)
    for saving in savings:
      temp = SavingItem(saving.description, saving.amount, saving.tax)
      p.addSavings(temp)

    incomeTotal = p.getIncome()
    expenseTotal = p.getExpense()
    SavingsTotal = p.getSavings()
    savingsRate = 0
    if (incomeTotal > 0 ):
      savingsRate = p.getSavingsRate(p.adjustedIncome(p.getIncome()), p.getExpense())
    

    net = p.getNetIncome(incomeTotal, expenseTotal)

    return render_template("index.html", incomes = incomes, expenses = expenses, savings = savings, form = form, incomeTotal = incomeTotal, expenseTotal = expenseTotal, SavingsTotal = SavingsTotal, savingsRate = savingsRate, net = net, month = month, year = year)
    
  form.month.default = str(int(month))
  form.year.default = year
  form.process()

  fullDate = "%" + str(year) + "-" + str(month) + "%" 
  
  month = calendar.month_name[int(month)]
  print(fullDate)
  incomes = Income.query.filter(and_(Income.date.like(fullDate), current_user.id == Income.user_id)).all()
  expenses = Expense.query.filter(and_(Expense.date.like(fullDate), current_user.id == Expense.user_id)).all()
  savings = Saving.query.filter(and_(Saving.date.like(fullDate), current_user.id == Saving.user_id)).all()
  print("starting income")
  for income in incomes:
    temp = IncomeItem(income.description, income.amount)
    print(income)
    p.addIncome(temp)
  for expense in expenses:
    temp = ExpenseItem(expense.description, expense.amount)
    p.addExpense(temp)
  for saving in savings:
    temp = SavingItem(saving.description, saving.amount, saving.tax)
    p.addSavings(temp)
  incomeTotal = p.getIncome()
  expenseTotal = p.getExpense()
  net = p.getNetIncome(incomeTotal, expenseTotal)
  
  return render_template("index.html", incomes = incomes, expenses = expenses, savings = savings, form = form, net = net, month = month, year = year)


    


@app.route('/addIncome', methods = ['GET', 'POST'])
def income():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))

  form = IncomeForm()
  if form.validate_on_submit():
    print("income validated")
    description = form.description.data
    amount = form.amount.data
    date = form.date.data
    user_id = current_user.id
    temp = Income(description = description, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()


    return redirect(url_for('index'))


  return render_template("income.html", form = form)

@app.route('/deleteIncome/<income_id>', methods = ['POST'])

def deleteIncome(income_id):
  income = Income.query.get(income_id)
  db.session.delete(income)
  db.session.commit()
  flash('Income Item Deleted')
  return redirect(url_for('index'))


@app.route('/deleteExpense/<expense_id>', methods = ['POST'])

def deleteExpense(expense_id):
  expense = Expense.query.get(expense_id)
  db.session.delete(expense)
  db.session.commit()
  flash('Expense Item Deleted')
  return redirect(url_for('index'))

@app.route('/deleteSaving/<saving_id>', methods = ['POST'])

def deleteSaving(saving_id):
  saving = Saving.query.get(saving_id)
  db.session.delete(saving)
  db.session.commit()
  flash('Saving Item Deleted')
  return redirect(url_for('index'))


@app.route('/register', methods = ['GET', 'POST'])

def register():
  if current_user.is_authenticated:
      print(current_user)
      return redirect(url_for("index"))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username = form.username.data, email = form.email.data, password = hashed_password)
    db.session.add(user)
    db.session.commit()
    flash('Your account has been created! You are now able to log in')
    return redirect(url_for('login'))


  return render_template('registration.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  print("test")
  if current_user.is_authenticated:
      print(current_user)
      return redirect(url_for("index"))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email = form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
       login_user(user, remember = form.remember.data)
       return redirect(url_for('index'))
    else:
      print("login unsuccessful")
      flash("Login unsuccessful. Please Check Email and Password")
  print("not validated")
  return render_template('login.html', form = form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))



@app.route('/addSavings', methods = ['GET', 'POST'])
def saving():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))
  form = SavingForm()
  if form.validate_on_submit():

    description = form.description.data
    amount = form.amount.data
    date = form.date.data
    tax = form.tax.data
    user_id = current_user.id
    temp = Saving(description = description, tax = tax, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()
    return redirect(url_for('index'))
    
  print("validation failed")

  return render_template("saving.html", form = form)

@app.route('/addExpense', methods = ['GET', 'POST'])
def expense():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))
  form = ExpenseForm()
  if form.validate_on_submit():
    print("Expense added")
    description = form.description.data
    amount = form.amount.data
    date = form.date.data
    user_id = current_user.id
    temp = Expense(description = description, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()
    print("Expense committed")
    return redirect(url_for('index'))

  return render_template("expense.html", form = form)
    