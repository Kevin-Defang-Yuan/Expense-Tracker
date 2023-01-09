from django.contrib import admin
from .models import MonthlyBudget, YearlyBudget
# Register your models here.

admin.site.register(MonthlyBudget)
admin.site.register(YearlyBudget)
