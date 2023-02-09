from django.forms import ModelForm, NumberInput, Select
from .models import YearlyBudget, MonthlyBudget


class CreateYearlyBudgetForm(ModelForm):
    class Meta:
        model = YearlyBudget
        fields = ['budget', 'year']
        widgets = {
            'budget': NumberInput(attrs={'class': 'form-control', 'id': 'yearlybudget-budget-input'}),
            'year': Select(attrs={'class': 'form-control'}),
        }

class UpdateYearlyBudgetForm(ModelForm):
    class Meta:
        model = YearlyBudget
        fields = ['budget']
        widgets = {
            'budget': NumberInput(attrs={'class': 'form-control', 'id': 'yearlybudget-budget-input'}),
        }
    
    
    

class CreateMonthlyBudgetForm(ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ['budget', 'year', 'month']
        widgets = {
            'budget': NumberInput(attrs={'class': 'form-control', 'id': 'monthlybudget-budget-input'}),
            'year': Select(attrs={'class': 'form-control'}),
            'month': Select(attrs={'class': 'form-control'}),
        }
    
    
class UpdateMonthlyBudgetForm(ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ['budget']
        widgets = {
            'budget': NumberInput(attrs={'class': 'form-control', 'id': 'monthlybudget-budget-input'}),
        }
