# Generated by Django 4.1.1 on 2022-12-01 04:46

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0003_rename_expensefixed_fixedexpense'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BudgetMonthly',
            new_name='MonthlyBudget',
        ),
        migrations.RenameModel(
            old_name='ExpenseRecurring',
            new_name='RecurringExpense',
        ),
        migrations.RenameModel(
            old_name='BudgetYearly',
            new_name='YearlyBudget',
        ),
    ]
