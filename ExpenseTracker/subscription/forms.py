from django.forms import ModelForm, RadioSelect
from django.forms import DateField, DecimalField, SelectDateWidget, CharField, BooleanField, IntegerField, CheckboxInput, Select, ChoiceField
from django.forms import TextInput, NumberInput, DateInput, ModelChoiceField
from .models import Subscription
from base.models import Category
from base.forms import EARLIEST_YEAR, LATEST_YEAR


# Here we create a date input class so that it creates an HTML input date element
class DateInput(DateInput):
    input_type = 'date'

"""
Create Subscription Form with Bootstrap styling
"""
class CreateSubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'cost', 'category', 'cycle', 'start_date']
        widgets = {
            'name': TextInput(attrs={'id': 'subscription-name-input', 'class': 'form-control'}),
            'cost': NumberInput(attrs={'id': 'subscription-cost-input', 'class': 'form-control'}),
            'start_date': DateInput(attrs={'id': 'subscription-date-picker', 'class': 'form-control'}),
            
        }
    
    # Max length is 200 characters
    name = TextInput()
    category = ModelChoiceField(queryset=Category.objects.all(), widget=Select(attrs={'class': 'form-control'}))
    cost = NumberInput()

    start_date = DateInput()

    # Hidden fields, may be incorporated at a later date
    # indefinite = BooleanField(widget=CheckboxInput, required=False)
    # end_date = DateField(widget=SelectDateWidget(years=range(EARLIEST_YEAR, LATEST_YEAR)), required=False)
    # quantity = IntegerField(required=False)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Biweekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUALLY = 'Semiannually'
    ANNUALLY = 'Annually'


    CYCLE_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (SEMIANNUALLY, 'Semiannually'),
        (ANNUALLY, 'Annually')
    )

    cycle = CharField(widget=Select(choices=CYCLE_CHOICES, attrs={'class': 'form-control'}))
    
    # Use request to determine the category queryset. 
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)

"""
Form for terminating a subscription
"""
class TerminateSubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['terminated']

    CHOICES = [
        (True, 'Yes'),
        (False, 'No')
    ]
    terminated = ChoiceField(
        widget=RadioSelect(attrs={'id': 'radio-select'}),
        choices=CHOICES
    )