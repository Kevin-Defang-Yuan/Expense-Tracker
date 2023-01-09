from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.
# FIRST IDEA
# Users will only have access to an "Edit Button"
# The Edit Buttons sends them to a Normal View, which checks if year (or month) exists
# Done using the BudgetYearly.objects.filter(order_date__year = 2000)
# If year doesn't exist, create new object and save and then redirect to edit page. 
# If year exists, redirect to edit page.

# SECOND IDEA
# Template should have an ADD if Budget doesn't exist
# And EDIT if Budget does exist

EARLIEST_YEAR = 1950
YEARS_AFTER_CURRENT = 5

class Budget(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    budget = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Spending budget"
    )

    class Meta:
        abstract = True
        

class YearlyBudget(Budget):
    # Non editable data
    YEAR_CHOICES = [(y,y) for y in range(1950, datetime.date.today().year + YEARS_AFTER_CURRENT + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES)

    class Meta:
        ordering = ['year']

    def __str__(self):
        return f'{self.year}: {self.budget}'

class MonthlyBudget(Budget):
    # Non editable data
    YEAR_CHOICES = [(y,y) for y in range(1950, datetime.date.today().year + YEARS_AFTER_CURRENT + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES)

    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12
    MONTH_CHOICES = (
        (JAN, 'January'),
        (FEB, 'February'),
        (MAR, 'March'),
        (APR, 'April'),
        (MAY, 'May'),
        (JUN, 'June'),
        (JUL, 'July'),
        (AUG, 'August'),
        (SEP, 'September'),
        (OCT, 'October'),
        (NOV, 'November'),
        (DEC, 'December')
    )

    month = models.IntegerField(choices=MONTH_CHOICES)

    def __str__(self):
            return f'{self.month}, {self.year}: {self.budget}'
    