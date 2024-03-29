from django.db import models
from django.contrib.auth.models import User
import datetime

EARLIEST_YEAR = 1950

# How many years users can create an expense in the future
YEARS_AFTER_CURRENT = 5

"""
Budget Class
    user (User): user
    budget (Decimal): amount
    track (Bool): should the budget also show an indicator for progress? 
"""
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

    track = models.BooleanField(
        default=True
    )

    class Meta:
        abstract = True
        
"""
YearlyBudget Class
    user (User): user
    budget (Decimal): amount
    track (Bool): should the budget also show an indicator for progress? 
    year (Int): year
"""
class YearlyBudget(Budget):
    # Non editable data
    YEAR_CHOICES = [(y,y) for y in range(1950, datetime.date.today().year + YEARS_AFTER_CURRENT)]
    year = models.IntegerField(choices=YEAR_CHOICES)

    class Meta:
        ordering = ['year']

    def __str__(self):
        return f'{self.year}: {self.budget}'

"""
MonthlyBudget Class
    user (User): user
    budget (Decimal): amount
    track (Bool): should the budget also show an indicator for progress? 
    year (Int): year
    month (Int): month
"""
class MonthlyBudget(Budget):
    # Non editable data
    YEAR_CHOICES = [(y,y) for y in range(1950, datetime.date.today().year + YEARS_AFTER_CURRENT)]
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
    