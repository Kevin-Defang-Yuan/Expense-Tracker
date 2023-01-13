from django.apps import AppConfig
from datetime import datetime, timedelta
from dateutil import relativedelta
import os


class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'

    # https://stackoverflow.com/questions/59541954/how-to-start-a-background-thread-when-django-server-is-up
    # Here we want to calculate all the subscriptions once the server starts running
    def ready(self):
        # Here we added code to prevent ready from running twice (for some random reason)
        # https://stackoverflow.com/questions/33814615/how-to-avoid-appconfig-ready-method-running-twice-in-django
        if os.environ.get('RUN_MAIN'):

            from .models import Subscription
            from base.models import Expense

            # Here we want to perform calculations for ALL users
            subscriptions = Subscription.objects.all() 
            for subscription in subscriptions:
                if subscription.is_active:
                    today = datetime.today().date()
                    user = subscription.user
                    category = subscription.category
                    cost = subscription.cost
                    description = subscription.name

                    date = subscription.start_date
                    while((subscription.indefinite and date <= today) or (date <= today and date <= subscription.get_end_date)):
                        if date == today:
                            existing_expense = Expense.objects.filter(subscription=subscription, date=date, user=user).first()
                            if not existing_expense:
                                expense = Expense(user=user, category=category, cost=cost, description=description, date=date, subscription=subscription)
                                expense.save()
                        if subscription.cycle == 365:
                            date += timedelta(days=1)
                        if subscription.cycle == 52:
                            date += timedelta(days=7)
                        if subscription.cycle == 26:
                            date += timedelta(days=14)
                        if subscription.cycle == 12:
                            date += relativedelta.relativedelta(months=1)
                        if subscription.cycle == 4:
                            date += relativedelta.relativedelta(months=3)
                        if subscription.cycle == 2:
                            date += relativedelta.relativedelta(months=6)
                        if subscription.cycle == 1:
                            date += relativedelta.relativedelta(months=12)
