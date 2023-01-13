from django.forms import ModelForm, DateField, DecimalField, ModelChoiceField, TextInput, SelectDateWidget, CharField
from .models import Expense, Category
from django.core.exceptions import ValidationError
import datetime

EARLIEST_YEAR = 2000
LATEST_YEAR = 2099

class CreateExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'cost', 'category', 'description']
    date = DateField(widget=SelectDateWidget(years=range(EARLIEST_YEAR, LATEST_YEAR)))
    category = ModelChoiceField(queryset=Category.objects.all())
    description = TextInput()

    def clean_date(self):
        data = self.cleaned_data['date']
        if data > datetime.date.today():
            raise ValidationError(('Invalid date - future date'))
        return data
    
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
        print(self.fields['category'].queryset)
        #self.fields['category'].queryset = Category.objects.filter(id__in=Expense.objects.all().filter(user=user).values('category'))

class CreateCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']
    
    name = CharField(max_length=200)

