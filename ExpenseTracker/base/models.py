from django.db import models
from django.contrib.auth.models import User


from django.db.models.signals import post_save
from django.dispatch import receiver
from colorfield.fields import ColorField
import seaborn as sns
import colorcet as cc

"""
Category Class
    user (User): user
    name (Char): name of category
"""
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

    color = ColorField(default='#FF0000')

  
    FOOD = 'Food'
    ALCOHOL_TOBACCO = 'Alcohol and tobacco'
    HOUSING_UTILITIES = 'Housing and utilities'
    APPAREL_SERVICES = 'Apparel and services'
    TRANSPORTATION = 'Transportation'
    HEALTHCARE = 'Healthcare'
    ENTERTAINMENT = 'Entertainment'
    PERSONAL_CARE = 'Personal care'
    READING = 'Reading'
    EDUCATION = 'Education'
    MISCELLANEOUS = 'Miscellaneous'
    CASH_CONTRIBUTIONS = 'Cash contributions'
    PERSONAL_INSURANCE_AND_PENSIONS = 'Personal insurance and pensions'


    BASE_CATEGORY_CHOICES = (
        (FOOD, 'Food'),
        (ALCOHOL_TOBACCO, 'Alcohol and tobacco'),
        (HOUSING_UTILITIES, 'Housing and utilities'),
        (APPAREL_SERVICES, 'Apparel and services'),
        (TRANSPORTATION, 'Transportation'),
        (HEALTHCARE, 'Healthcare'),
        (ENTERTAINMENT, 'Entertainment'),
        (PERSONAL_CARE, 'Personal care'),
        (READING, 'Reading'),
        (EDUCATION, 'Education'),
        (MISCELLANEOUS, 'Miscellaneous'),
        (CASH_CONTRIBUTIONS, 'Cash contributions'),
        (PERSONAL_INSURANCE_AND_PENSIONS, 'Personal insurance and pensions')
    )

    relation = models.CharField(
        max_length=40,
        choices=BASE_CATEGORY_CHOICES,
        default=None,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total(self):
        expenses = self.all_expenses.all()
        total = 0
        for expense in expenses:
            total += expense.cost
        return total


"""
Payment Class
    user (User): user
    description (Text): an optional description of expense
    cost (Decimal): the cost
"""
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
        verbose_name="Description: Optional",
        max_length=300
        )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Cost in USD"
    )

    class Meta:
        abstract = True

"""
Expense Class
    date (Date): date incurred
    category (Category): category
    subscription (Subscription): related subscription (if there is one)
    user (User): user
    description (Text): an optional description of expense
    cost (Decimal): the cost
"""
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

    subscription = models.ForeignKey(
        # This is to avoid circular import problem
        # https://stackoverflow.com/questions/4379042/django-circular-model-import-issue
        'subscription.Subscription',
        on_delete=models.CASCADE,
        related_name='all_expenses',
        null=True,
        blank=True
    )
    def __str__(self):
        output = str(self.category) + ' {' + str(self.cost) + '}' + ' {' + str(self.date) + '}' 
        return output

    class Meta:
        ordering = ['date']
    


        





# https://www.statista.com/statistics/183657/average-size-of-a-family-in-the-us/#:~:text=As%20of%202021%2C%20the%20U.S.,18%20living%20in%20the%20household
HOUSEHOLD_SIZE = 3.13

# https://www.bls.gov/news.release/cesan.nr0.htm
# Represents a single consumer unit per year
BLS_2021_DATA = {
    'Housing and utilities': 22624,
    'Transportation': 10961,
    'Food': 8289,
    'Personal insurance and pensions': 7873,
    'Healthcare': 5452,
    'Entertainment': 3568,
    'Cash contributions': 2415,
    'Apparel and services': 1754,
    'Education': 1226,
    'Miscellaneous': 986,
    'Alcohol and tobacco': 895,
    'Personal care': 771,
    'Reading': 114,
       
}



BLS_CATEGORY_CHOICES = [
    Category.HOUSING_UTILITIES,
    Category.TRANSPORTATION,
    Category.FOOD,
    Category.PERSONAL_INSURANCE_AND_PENSIONS,
    Category.HEALTHCARE,
    Category.ENTERTAINMENT,
    Category.CASH_CONTRIBUTIONS,
    Category.APPAREL_SERVICES,
    Category.EDUCATION,
    Category.MISCELLANEOUS,
    Category.ALCOHOL_TOBACCO,
    Category.PERSONAL_CARE,
    Category.READING,
]

LIVING_CATEGORIES = [
    Category.HOUSING_UTILITIES,
    Category.TRANSPORTATION,
    Category.FOOD,
    Category.PERSONAL_INSURANCE_AND_PENSIONS,
    
]

QUALITY_CATEGORIES = [
    Category.HEALTHCARE,
    Category.ENTERTAINMENT,
    Category.CASH_CONTRIBUTIONS,
    Category.APPAREL_SERVICES,
    Category.EDUCATION
]

ACCESSORY_CATEGORIES = [
    Category.MISCELLANEOUS,
    Category.ALCOHOL_TOBACCO,
    Category.PERSONAL_CARE,
    Category.READING
]


"""
Function that runs when a users first creates an account
Automatically creates the default categories for the user
"""
@receiver(post_save, sender=User)
def init_new_user(instance, created, raw, **kwargs):
    glasbey_colors = sns.color_palette(cc.glasbey, n_colors=len(BLS_2021_DATA)).as_hex() 
    color_index = 0
    if created and not raw:
        for key, value in BLS_2021_DATA.items():
            Category.objects.create(user=instance, name=key, color=glasbey_colors[color_index], relation=BLS_CATEGORY_CHOICES[color_index])
            color_index += 1
