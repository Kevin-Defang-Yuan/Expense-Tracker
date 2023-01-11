from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    # https://stackoverflow.com/questions/59541954/how-to-start-a-background-thread-when-django-server-is-up
    # Here we want to calculate all the subscriptions once the server starts running
    # def ready():
    #     from .models import Subscription

