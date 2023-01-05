from django.contrib import admin
from .models import Expense, Subscription, Category, MonthlyBudget, YearlyBudget
# Register your models here.

admin.site.register(Expense)
admin.site.register(Subscription)
admin.site.register(Category)
admin.site.register(MonthlyBudget)
admin.site.register(YearlyBudget)