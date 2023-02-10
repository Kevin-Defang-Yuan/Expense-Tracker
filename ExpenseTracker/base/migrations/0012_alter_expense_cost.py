# Generated by Django 4.1.1 on 2023-02-10 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_alter_expense_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='cost',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Cost in USD'),
        ),
    ]
