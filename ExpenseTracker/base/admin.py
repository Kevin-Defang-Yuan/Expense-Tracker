from django.contrib import admin
from .models import Expense, Subscription, Category
# Register your models here.

admin.site.register(Expense)
admin.site.register(Subscription)
admin.site.register(Category)
