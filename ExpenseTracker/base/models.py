from django.db import models
from django.contrib.auth.models import User


from django.db.models.signals import post_save
from django.dispatch import receiver

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

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

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


"""
Function that runs when a users first creates an account
Automatically creates the default categories for the user
"""
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
