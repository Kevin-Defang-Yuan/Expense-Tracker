from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Expense(models.Model):
    # One user can have many Expenses
    # on_delete=CASCADE means that when we delete the user, the expenses are also deleted
    # null=True means that we can have empty field (debugging)
    # blank=True we can submit empty forms (debugging)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    date = models.DateField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        output = str(self.category) + ' {' + str(self.cost) + '}' + ' {' + str(self.date) + '}' 
        return output

    # order the expenses by date, this orders the query set
    class Meta:
        ordering = ['date']