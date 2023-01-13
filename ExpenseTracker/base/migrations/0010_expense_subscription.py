# Generated by Django 4.1.1 on 2023-01-13 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_alter_subscription_indefinite'),
        ('base', '0009_delete_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='all_expenses', to='subscription.subscription'),
        ),
    ]
