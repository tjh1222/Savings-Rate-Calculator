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



'''
  <------------------------------------------------->
                      Models

'''

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


'''
  <----------------------------------------------------->
                    Helper Functions
'''




def queryIncome(fullDate, user):
  incomes = Income.query.filter(and_(Income.date.like(fullDate), current_user.id == Income.user_id)).all()
  return incomes

def getIncomeTotal(incomes, user):
  for income in incomes:
    temp = IncomeItem(income.description, income.amount)
    user.addIncome(temp)
  return user.getIncome()

def queryExpenses(fullDate, user):
  expenses = Expense.query.filter(and_(Expense.date.like(fullDate), current_user.id == Expense.user_id)).all()
  return expenses

def getExpenseTotal(expenses, user):
  for expense in expenses:
      temp = ExpenseItem(expense.description, expense.amount)
      user.addExpense(temp)
  return user.getExpense()

def querySavings(fullDate, user):
  savings = Saving.query.filter(and_(Saving.date.like(fullDate), current_user.id == Saving.user_id)).all()
  return savings

def getSavingsTotal(savings, user):
  for saving in savings:
      temp = SavingItem(saving.description, saving.amount, saving.tax)
      user.addSavings(temp)
  return user.getSavings()


'''

<-------------------------------------------------->
                    Routes

'''


@app.route('/trend')
def trend():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))
  
  return render_template('trend.html')


@app.route('/<date>') 
@app.route('/', methods = ['GET', 'POST'], defaults = {'date': None})

def index(date):
  # redirects users that aren't authenticated to the login page
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))

  #creates instance of person class to hold all income, expenses, and savings value
  p = Person(current_user.username)
  
  #form instance that allows user to control the month and year they are viewing on their dashboard
  form = DateForm()

  


  #current month
  month = datetime.now().month
  #format handling for querying database
  if int(month) < 10:
    month = "0" + str(month)
  #current year
  year = datetime.now().year

  
  


  #checks if request satisifes validation and that it is a Post request
  if form.validate_on_submit():

    #calculate fullDate for querying the database
    month = form.month.data
    year = form.year.data
    fullDate = "%" + str(year) + "-" + str(month) + "%"
    #Converts month back to real name ex: January. Dynamically updates the heading on the index.html page
    month = calendar.month_name[int(month)]
    
    # query database. Retrieving current_user income data that matches current date
    incomes = queryIncome(fullDate, p)
    #calculates income total
    incomeTotal = getIncomeTotal(incomes, p)

    #retrieve all related expense data 
    expenses = queryExpenses(fullDate, p)
    #calculate expense total
    expenseTotal = getExpenseTotal(expenses, p)
    #retrieve all savings data
    savings = querySavings(fullDate, p)
    #calculate savings total
    SavingsTotal = getSavingsTotal(savings, p)
    
    #sets default saving to 0 and checks to see if income is non zero. Prevents divide by zero error
    savingsRate = 0
    if (incomeTotal > 0 ):
      savingsRate = p.getSavingsRate(p.adjustedIncome(p.getIncome()), p.getExpense())
    
    #calculates net income
    net = p.getNetIncome(incomeTotal, expenseTotal)

    return render_template("index.html", incomes = incomes, expenses = expenses, savings = savings, form = form, incomeTotal = incomeTotal, expenseTotal = expenseTotal, SavingsTotal = SavingsTotal, savingsRate = savingsRate, net = net, month = month, year = year)


  fullDate = "%" + str(year) + "-" + str(month) + "%"


  if date != None:
    fullDate = "%" + date[0:7] + "%"
    month = date[5:7]
    year = date[0:4]
    form.month.default = str(int(month))
    form.year.default = year
    form.process()
  else:
    #sets default values for the dateform. Automatically starts at current month and year
    form.month.default = str(int(month))
    form.year.default = year
    form.process()
  


  
  month = calendar.month_name[int(month)]
  


  #query db for income
  incomes = queryIncome(fullDate, p)
  incomeTotal = getIncomeTotal(incomes, p)
  #query db for expenses
  expenses = queryExpenses(fullDate, p)
  expenseTotal = getExpenseTotal(expenses, p)
  #query db for savings
  savings = querySavings(fullDate, p)
  SavingsTotal = getSavingsTotal(savings, p)
  #calculate net income
  net = p.getNetIncome(incomeTotal, expenseTotal)

  #error handling. Prevents division by zero error
  savingsRate = 0
  if (incomeTotal > 0 ):
    savingsRate = p.getSavingsRate(p.adjustedIncome(p.getIncome()), p.getExpense())
  
  return render_template("index.html", incomes = incomes, expenses = expenses, savings = savings, form = form, net = net, month = month, year = year, incomeTotal = incomeTotal, expenseTotal = expenseTotal, SavingsTotal = SavingsTotal, savingsRate = savingsRate)


    


@app.route('/addIncome', methods = ['GET', 'POST'])
def income():
  if current_user.is_authenticated == False:
    return redirect(url_for('login'))

  form = IncomeForm()
  if form.validate_on_submit():
    description = form.description.data
    amount = form.amount.data
    try:
      amount = round(float(amount), 2)
      amount = f"{amount:.2f}"
    except ValueError:
      flash("You entered an Invalid amount. Must be a number.")
      return redirect(url_for('income'))
    date = form.date.data
    user_id = current_user.id
    temp = Income(description = description, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()


    return redirect(url_for('index', date = date))


  return render_template("income.html", form = form)

@app.route('/deleteIncome/<income_id>', methods = ['POST'])

def deleteIncome(income_id):
  income = Income.query.get(income_id)
  date = income.date
  db.session.delete(income)
  db.session.commit()
  flash('Income Item Deleted')
  return redirect(url_for('index', date = date))


@app.route('/deleteExpense/<expense_id>', methods = ['POST'])

def deleteExpense(expense_id):
  expense = Expense.query.get(expense_id)
  date = expense.date
  db.session.delete(expense)
  db.session.commit()
  flash('Expense Item Deleted')
  return redirect(url_for('index', date = date))

@app.route('/deleteSaving/<saving_id>', methods = ['POST'])

def deleteSaving(saving_id):
  saving = Saving.query.get(saving_id)
  date = saving.date
  db.session.delete(saving)
  db.session.commit()
  flash('Saving Item Deleted')
  return redirect(url_for('index', date = date))


@app.route('/register', methods = ['GET', 'POST'])

def register():

  if current_user.is_authenticated:
      return redirect(url_for("index"))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    try:
      user = User(username = form.username.data, email = form.email.data, password = hashed_password)
      db.session.add(user)
      db.session.commit()
      flash('Your account has been created! You are now able to log in')
      return redirect(url_for('login'))
    except:
      flash('The username or email you entered already exists.')
    return redirect(url_for('register'))


  return render_template('registration.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  error = None
  if current_user.is_authenticated:
      return redirect(url_for("index"))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email = form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
       login_user(user, remember = form.remember.data)
       return redirect(url_for('index'))
    else:
      flash("Login unsuccessful. Please Check Email and Password")
      error = "Invalid Credentials"
  
  return render_template('login.html', form = form, error = error)

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
    try:
      amount = round(float(amount), 2)
      amount = f"{amount:.2f}"
    except ValueError:
      flash("You entered an Invalid amount. Must be a number.")
      return redirect(url_for('saving'))
    date = form.date.data
    tax = form.tax.data
    user_id = current_user.id
    temp = Saving(description = description, tax = tax, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()
    return redirect(url_for('index', date = date))
    
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
    try:
      amount = round(float(amount), 2)
      amount = f"{amount:.2f}"
    except ValueError:
      flash("You entered an Invalid amount. Must be a number.")
      return redirect(url_for('expense'))
    date = form.date.data
    user_id = current_user.id
    temp = Expense(description = description, amount = amount, date = date, user_id = user_id)
    db.session.add(temp)
    db.session.commit()
    print("Expense committed")
    return redirect(url_for('index', date = date))

  return render_template("expense.html", form = form)
    