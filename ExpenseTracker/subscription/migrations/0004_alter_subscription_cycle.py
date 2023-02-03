# Generated by Django 4.1.1 on 2023-01-21 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_alter_subscription_indefinite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='cycle',
            field=models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Biweekly', 'Biweekly'), ('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Semiannually', 'Semiannually'), ('Annually', 'Annually')], default='Monthly', max_length=20, verbose_name='Interval of Recurring Expense'),
        ),
    ]