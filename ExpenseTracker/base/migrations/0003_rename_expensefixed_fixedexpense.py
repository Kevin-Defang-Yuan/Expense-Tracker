# Generated by Django 4.1.1 on 2022-12-01 04:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0002_category_user_budgetyearly_budgetmonthly'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExpenseFixed',
            new_name='FixedExpense',
        ),
    ]
