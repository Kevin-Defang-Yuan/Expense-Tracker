# Generated by Django 4.1.1 on 2023-01-12 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_remove_yearlybudget_user_alter_expense_category_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
