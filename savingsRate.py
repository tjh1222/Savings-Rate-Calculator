class Person:
  
  def __init__(self, name):

    self.name = name
    self.incomes = []
    self.expenses = []
    self.savings = []

  def addIncome(self, income):
    self.incomes.append(income)
  
  def addExpense(self, expense):
    self.expenses.append(expense)

  def addSavings(self, saving):
    self.savings.append(saving)


  def getIncome(self):
    total = 0
    for income in self.incomes:
      total += income.getAmount()
    
    return round(total, 2)

  def getExpense(self):
    total = 0
    for expense in self.expenses:
      total += expense.getAmount()
    
    return round(total, 2)

  def getSavings(self):
    total = 0
    for saving in self.savings:
      total += saving.getAmount()

  
    return round(total, 2)

  
  def adjustedIncome(self, income):
    income = income
    print(f"The income before adjustment is: {income}")
    for saving in self.savings:
      print(saving)
      if (saving.isTaxAdvantaged() == True):
        income += saving.getAmount()
        print(income)
    print(f"The adjusted Income is : {income}")

    return round(income, 2)

  def getSavingsRate(self, adjIncome, ExpenseItem):

    savingsRate = ((adjIncome - ExpenseItem) / (adjIncome)) * 100
    print(savingsRate)

    return round(savingsRate, 2)
  
  def getNetIncome(self, income, expense):
    afterTaxSaving = 0
    net = income - expense
    print(net)
    for saving in self.savings:
      if(saving.isTaxAdvantaged() == False):
        afterTaxSaving += saving.getAmount()
    print(net)
    print(afterTaxSaving)
    net = net - afterTaxSaving
    
    return round(net, 2)


  




class IncomeItem:
  
  def __init__(self, name, amount):
    self.name = name
    self.amount = float(amount)

  def getName(self):
    return self.name

  def getAmount(self):
    return self.amount


class ExpenseItem:

  def __init__(self, name, amount):
    self.name = name
    self.amount = float(amount)

  def getName(self):
    return self.name

  def getAmount(self):
    return self.amount
  

class SavingItem:

  #todo
  def __init__(self, name, amount, taxAdvantaged):
    self.name = name
    self.amount = float(amount)
    self.taxAdvantaged = taxAdvantaged

  def getName(self):
    return self.name

  def getAmount(self):
    return self.amount

  def isTaxAdvantaged(self):
    taxAdvantaged = False
    if (self.taxAdvantaged == "Pre-Tax"):
      taxAdvantaged = True

    print(taxAdvantaged)
    return taxAdvantaged





