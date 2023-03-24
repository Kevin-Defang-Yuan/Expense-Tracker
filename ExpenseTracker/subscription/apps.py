from django.apps import AppConfig
from datetime import datetime, timedelta
from dateutil import relativedelta
import os

"""
Some class to check for subscription updates once the development server is activated
"""
class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'

    # https://stackoverflow.com/questions/59541954/how-to-start-a-background-thread-when-django-server-is-up
    # Here we want to calculate all the subscriptions once the server starts running
    # def ready(self):
    #     # Here we added code to prevent ready from running twice (for some random reason)
    #     # https://stackoverflow.com/questions/33814615/how-to-avoid-appconfig-ready-method-running-twice-in-django
    #     if os.environ.get('RUN_MAIN'):

    #         from .models import Subscription
    #         from base.models import Expense

    #         # Here we want to perform calculations for ALL users and initialize expenses that are created today based on a sub
    #         subscriptions = Subscription.objects.all() 
    #         for subscription in subscriptions:
    #             if subscription.is_active:
    #                 existing_expense_instances = subscription.get_existing_expense_instances()
    #                 for expense in existing_expense_instances:
    #                     existing_expense = Expense.objects.filter(subscription=expense.subscription, date=expense.date, user=expense.user).first()
    #                     if not existing_expense:
    #                         expense.save()