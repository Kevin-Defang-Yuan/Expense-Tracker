# Generated by Django 4.1.1 on 2023-02-06 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_alter_subscription_cycle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='terminated',
        ),
    ]