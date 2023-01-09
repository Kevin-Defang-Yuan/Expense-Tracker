from django.forms import ModelForm
from .models import YearlyBudget, MonthlyBudget

class CreateYearlyBudgetForm(ModelForm):
    class Meta:
        model = YearlyBudget
        fields = ['budget', 'year']

class CreateMonthlyBudgetForm(ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ['budget', 'year', 'month']
    
    