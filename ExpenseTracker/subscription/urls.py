from django .urls import path
from .views import SubscriptionCreate, SubscriptionList



urlpatterns = [
    path('subscription-create/', SubscriptionCreate.as_view(), name="subscription-create"),
    path('subscription-list/', SubscriptionList.as_view(), name="subscription-list"),
]