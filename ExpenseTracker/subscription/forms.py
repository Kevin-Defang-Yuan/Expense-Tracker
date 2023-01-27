from django.forms import ModelForm
from django.forms import DateField, DecimalField, SelectDateWidget, CharField, BooleanField, IntegerField, CheckboxInput, Select
from .models import Subscription
from base.models import Category
from base.forms import EARLIEST_YEAR, LATEST_YEAR
class CreateSubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'cost', 'category', 'cycle', 'start_date', 'end_date', 'quantity', 'indefinite']
    
    name = CharField(
        max_length=200,

    )
    
    cost = DecimalField(
        max_digits=8, 
        decimal_places=2,

    )

    start_date = DateField(widget=SelectDateWidget(years=range(EARLIEST_YEAR, LATEST_YEAR)))

    indefinite = BooleanField(widget=CheckboxInput, required=False)

    end_date = DateField(widget=SelectDateWidget(years=range(EARLIEST_YEAR, LATEST_YEAR)), required=False)
    quantity = IntegerField(required=False)

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

    cycle = CharField(widget=Select(choices=CYCLE_CHOICES))


    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)