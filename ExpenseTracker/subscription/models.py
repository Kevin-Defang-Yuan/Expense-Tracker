from django.db import models
from base.models import Category, Expense
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil import relativedelta
from django.contrib.auth.models import User


"""
Subscription model
"""
class Subscription(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Name of Subscription"
    )
    
    cost = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Cost in USD"
    )

    start_date = models.DateField(
        verbose_name="Start Date of Recurring Expense"
    )

    # Determines if object is a subscription or a recurring expense
    indefinite = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Indefinite"
    )

    # Determines if the subscription has been cancelled or not
    terminated = models.BooleanField(
        null=True,
        blank=True,
        default=False
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

    cycle = models.CharField(
        max_length=20,
        choices=CYCLE_CHOICES, 
        default=MONTHLY,
        verbose_name="Interval of Recurring Expense"
    )
    # This means we can do something like 
    # thing.cycle = Things.WEEKLY

    # related_names have to be unique
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="all_subscriptions",    
    )

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        # output = str(self.category) + ' {' + str(self.cost) + '}' + ' {' + str(self.start_date) + '}' 
        return f'{self.name}, {self.category}, {self.cost}'
    
    # Override clean method so that either end_date is specified or quantity is specified
    # DON"T DELETE THIS! THIS IS VALUABLE 
    # https://stackoverflow.com/questions/12021911/either-or-fields-in-django-models
    # def clean(self):
    #     if self.end_date is None and self.quantity is None and self.indefinite is None:
    #         raise ValidationError(('Input either end_date, quantity, or check indefinite. Only one, not all three')) 
        
    #     if self.end_date and self.quantity:
    #         raise ValidationError(('Input either end_date or quantity')) 
        
    #     if self.end_date and self.indefinite:
    #         raise ValidationError(('An indefinite subscription should not have an end date')) 
        
    #     if self.quantity and self.indefinite:
    #         raise ValidationError(('An indefinite subscription should not have a known quantity')) 
    
    # Adds a get_end_date attribute, mostly for recurring expenses. 
    @property
    def get_end_date(self):
        if self.end_date:
            return self.end_date
        
        if self.indefinite:
            return None

        end_date = self.start_date
   
        for i in range(self.quantity - 1): # Here we subtract by 1 or else difference is too large
            end_date += self.progress_cycle()            
        return end_date
    
    # Determines if a subscription is currently active. 
    @property
    def is_active(self):
        # Return false if terminated
        if self.terminated:
            return False

        # Otherwise, resume calculations        
        today = datetime.today().date()
        sub_end_date = self.get_end_date
        sub_start_date = self.start_date
        # Check if sub start date is before today and
        #   if indefinite or sub_end-date is after today
        if today >= sub_start_date and (not sub_end_date or today <= sub_end_date):
            return True
        else:
            return False
    
    # Function that iterates a subscription cycle, used to calculate possible enddate. 
    def progress_cycle(self):
        if self.cycle == self.DAILY:
            return timedelta(days=1)
        if self.cycle == self.WEEKLY:
            return timedelta(days=7)
        if self.cycle == self.BIWEEKLY:
            return timedelta(days=14)
        if self.cycle == self.MONTHLY:
            return relativedelta.relativedelta(months=1)
        if self.cycle == self.QUARTERLY:
            return relativedelta.relativedelta(months=3)
        if self.cycle == self.SEMIANNUALLY:
            return relativedelta.relativedelta(months=6)
        if self.cycle == self.ANNUALLY:
            return relativedelta.relativedelta(months=12)
        print(self, self.cycle)
    
    # Function that gets all expenses instances of a subscription. Valuable when displaying all expenses that
    #   would get deleted as a result of deleting a subscription
    def get_existing_expense_instances(self):
        today = datetime.today().date()
        user = self.user
        category = self.category
        cost = self.cost
        description = self.name
        date = self.start_date

        ret = []
        # Find all expenses that matches the following attributes
        # This could be simplified later to just query based on subscription. 
        while((self.indefinite and date <= today) or (date <= today and date <= self.get_end_date)):
            expense = Expense(user=user, category=category, cost=cost, description=description, date=date, subscription=self)
            ret.append(expense)
            date += self.progress_cycle()
        return ret

    
    """
    Function for saving a subscription. 
    Once a subscription is saved, check if there are any old expense instances that should be created automatically. 
    """
    def save(self, *args, **kwargs):
        super(Subscription, self).save(*args, **kwargs)

        # Check if there are old expenses based on the subscription, delete them if they exist
        old_expense_instances = self.all_expenses.all()
        for expense in old_expense_instances:
            expense.delete()
        
        # Then repopulate new expenses
        existing_expense_instances = self.get_existing_expense_instances()
        for expense in existing_expense_instances:
            expense.save()

    """
    Determine if a subscription is active in a specific time range. 

    Args:
        selected_start_date (Date): a date
        selected_end_date (Date): a date
        day (Date): a date. This is only passed in if the range is a single day, because the calculation changes
            Otherwise, it is a time range and would use different calculation

    Returns:
        Bool 
    """
    def is_active_subscription_in_range(self, selected_start_date, selected_end_date, day):
        # Return subscriptions that are active and are relevant to time period
        if self.is_active:
            sub_end_date = self.get_end_date
            sub_start_date = self.start_date

            # If a single day, then sub needs to start before the day and end after
            if day:
                if selected_start_date >= sub_start_date and (not sub_end_date or sub_end_date >= selected_end_date):
                    return True
            # IF a range, then sub needs to be active before the range ends. 
            else:
                if sub_start_date <= selected_end_date and (not sub_end_date or sub_end_date >= selected_start_date):
                    return True
        
        return False
        



    """
    Determine if a subscription was active in a specific time range. 

    Args:
        selected_start_date (Date): a date
        selected_end_date (Date): a date
        day (Date): a date. This is only passed in if the range is a single day, because the calculation changes
            Otherwise, it is a time range and would use different calculation

    Returns:
        Bool 
    """
    def was_active_subscription_in_range(self, selected_start_date, selected_end_date, day):
        # Return subscriptions that are not active but are relevant to time period
        if not self.is_active:
            sub_end_date = self.get_end_date
            sub_start_date = self.start_date
            if day:
                if selected_start_date >= sub_start_date and (not sub_end_date or sub_end_date >= selected_end_date):
                    return True
            else:
                if sub_start_date <= selected_end_date and (not sub_end_date or sub_end_date >= selected_start_date):
                    return True
        return False
        


        

        