from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
# from dateutil.relativedelta import relativedelta

# Create your models here.

class Category(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Name of Category"
    )

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Payment(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    description = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Description: Optional"
        )
    cost = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Cost in USD"
    )

    class Meta:
        abstract = True

class Expense(Payment):
    date = models.DateField(
        verbose_name="Date of Expense"
    )
    # https://stackoverflow.com/questions/17328910/django-what-is-reverse-relationship
    # https://stackoverflow.com/questions/2642613/what-is-related-name-used-for
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="all_expenses",    
    )

    def __str__(self):
        output = str(self.category) + ' {' + str(self.cost) + '}' + ' {' + str(self.date) + '}' 
        return output

    class Meta:
        ordering = ['date']
    
class Subscription(Payment):
    start_date = models.DateField(
        verbose_name="Start Date of Recurring Expense"
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Final Date of Recurring Expense"
    )
    quantity = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Expected Times to Pay Recurring Expense"
    )

    DAILY = 365
    WEEKLY = 52
    BIWEEKLY = 26
    MONTHLY = 12
    QUARTERLY = 4
    SEMIANNUALLY = 2
    ANNUALLY = 1

    CYCLE_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (SEMIANNUALLY, 'Semiannually'),
        (ANNUALLY, 'Annually')
    )

    cycle = models.IntegerField(
        choices=CYCLE_CHOICES, 
        default=MONTHLY,
        verbose_name="Interval of Recurring Expense"
    )
    # This means we can do something like 
    # thing.cycle = Things.WEEKLY

    # related_names have to be unique
    category = models.ForeignKey(
        Category, 
        on_delete=models.RESTRICT, 
        related_name="all_subscriptions",    
    )

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        output = str(self.category) + ' {' + str(self.cost) + '}' + ' {' + str(self.start_date) + '}' 
        return output
    
    # Override clean method so that either end_date is specified or quantity is specified
    # https://stackoverflow.com/questions/12021911/either-or-fields-in-django-models
    def clean(self):
        if self.end_date is None and self.quantity is None:
            raise ValidationError(_('Input either end_date or quantity')) 
        
        if self.end_date and self.quantity:
            raise ValidationError(_('Input either end_date or quantity')) 
    
    def get_end_date(self):
        if self.end_date:
            return self.end_date

        end_date = self.start_date
        if self.cycle == 365:
            for i in range(self.quantity - 1): # Here we subtract by 1 or else difference is too large
                end_date += datetime.timedelta(days=1)


        return end_date

        

        


# FIRST IDEA
# Users will only have access to an "Edit Button"
# The Edit Buttons sends them to a Normal View, which checks if year (or month) exists
# Done using the BudgetYearly.objects.filter(order_date__year = 2000)
# If year doesn't exist, create new object and save and then redirect to edit page. 
# If year exists, redirect to edit page.

# SECOND IDEA
# Template should have an ADD if Budget doesn't exist
# And EDIT if Budget does exist

class Budget(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    goal = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Budget Goal"
    )

    class Meta:
        abstract = True

class YearlyBudget(Budget):
    # Non editable data
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.date.year 

class MonthlyBudget(Budget):
    # Non editable data
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.date.year + ": " + self.date.month 


# https://www.statista.com/statistics/183657/average-size-of-a-family-in-the-us/#:~:text=As%20of%202021%2C%20the%20U.S.,18%20living%20in%20the%20household
HOUSEHOLD_SIZE = 3.13

# https://www.bls.gov/news.release/cesan.nr0.htm
# Represents a single consumer unit per year
BLS_2021_DATA = {
    'Food': 8289,
    'Alcohol and tobacco': 895,
    'Housing and utilities': 22624,
    'Apparel and services': 1754,
    'Transportation': 10961,
    'Healthcare': 5452,
    'Entertainment': 3568,
    'Personal care': 771,
    'Reading': 114,
    'Education': 1226,
    'Miscellaneous': 986,
    'Cash contributions': 2415,
    'Personal insurance and pensions': 7873      
}



@receiver(post_save, sender=User)
def init_new_user(instance, created, raw, **kwargs):
    if created and not raw:
        Category.objects.create(user=instance, name='Food')
        Category.objects.create(user=instance, name='Alcohol and tobacco')
        Category.objects.create(user=instance, name='Housing and utilities')
        Category.objects.create(user=instance, name='Apparel and services')
        Category.objects.create(user=instance, name='Transportation')
        Category.objects.create(user=instance, name='Healthcare')
        Category.objects.create(user=instance, name='Entertainment')
        Category.objects.create(user=instance, name='Personal care')
        Category.objects.create(user=instance, name='Reading')
        Category.objects.create(user=instance, name='Education')
        Category.objects.create(user=instance, name='Miscellaneous')
        Category.objects.create(user=instance, name='Cash contributions')
        Category.objects.create(user=instance, name='Personal insurance and pensions')
