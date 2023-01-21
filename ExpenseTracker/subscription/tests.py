from django.test import TestCase
from .models import Subscription, Category
from django.contrib.auth.models import User
import datetime



# Create your tests here.
class SubscriptionTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='12345')
        category = Category.objects.create(name='Testing', user=user)
        Subscription.objects.create(user=user, name='Spotify', cost='5.00', start_date=datetime.date(2023, 1, 1), end_date=datetime.date(2023, 1, 3), cycle = 365, category=category)
        Subscription.objects.create(user=user, name='Netflix', cost='9.00', start_date=datetime.date(2022, 12, 16), end_date=datetime.date(2023, 1, 20), cycle = 52, category=category)
        Subscription.objects.create(user=user, name='Hulu', cost='9.00', start_date=datetime.date(2022, 12, 16), end_date=datetime.date(2023, 1, 20), cycle = 26, category=category)
        
    
    def test_get_existing_expense_instance(self):
        spotify = Subscription.objects.get(name='Spotify')
        spotify_expenses = spotify.get_existing_expense_instances()
        self.assertEqual(len(spotify_expenses), 3)

        netflix = Subscription.objects.get(name='Netflix')
        netflix_expenses = netflix.get_existing_expense_instances()
        self.assertEqual(len(netflix_expenses), 6)

        hulu = Subscription.objects.get(name='Hulu')
        hulu_expenses = hulu.get_existing_expense_instances()
        self.assertEqual(len(hulu_expenses), 3)

