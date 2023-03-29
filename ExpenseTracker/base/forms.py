from django.forms import ModelForm, DateField, DecimalField, ModelChoiceField, TextInput, SelectDateWidget, CharField, DateInput
from django.forms import Select, NumberInput, Textarea
from .models import Expense, Category
from django.core.exceptions import ValidationError
import datetime
from colorfield.widgets import ColorWidget

EARLIEST_YEAR = 2000
LATEST_YEAR = 2099


# Here we create a date input class so that it creates an HTML input date element
class DateInput(DateInput):
    input_type = 'date'


"""
The form for creating an expense. This is needed in order to add styling to the widgets
"""
class CreateExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'cost', 'category', 'description']
        widgets = {
            'date': DateInput(attrs={'id': 'expense-date-picker', 'class': 'form-control'}),
            'cost': NumberInput(attrs={'class': 'form-control', 'id': 'expense-cost-input'}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 40, 'id': 'description-input'}),
            
        }
    
    date = DateInput()
    # For some reason, I need to put the widget here. It doesn't work when I add it to the widgets above
    category = ModelChoiceField(queryset=Category.objects.all(), widget=Select(attrs={'class': 'form-control'}))
    description = Textarea()


    # Function that doesn't allow future dates. I'll turn it off for now
    # def clean_date(self):
    #     data = self.cleaned_data['date']
    #     if data > datetime.date.today():
    #         raise ValidationError(('Invalid date - future date'))
    #     return data
    
    # Basic validation
    def clean_cost(self):
        data = self.cleaned_data['cost']
        if data < 0:
            raise ValidationError(('Invalid cost - Cannot use negative numbers'))
        
        if data == 0:
            raise ValidationError(('Invalid cost - Cannot use zero'))
        return data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateExpenseForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)

"""
Form for creating a category
"""
class CreateCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'id': 'category-name-input'}),
            'color': TextInput(attrs={'type': 'color', 'id': 'color-picker'})
        }
    



