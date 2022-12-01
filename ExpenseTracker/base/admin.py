from django.contrib import admin
from .models import FixedExpense, RecurringExpense, Category, MonthlyBudget, YearlyBudget
# Register your models here.

admin.site.register(FixedExpense)
admin.site.register(RecurringExpense)
admin.site.register(Category)
admin.site.register(MonthlyBudget)
admin.site.register(YearlyBudget)