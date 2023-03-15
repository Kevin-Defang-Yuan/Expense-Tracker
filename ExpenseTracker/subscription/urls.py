from django .urls import path
from .views import SubscriptionCreate, SubscriptionList, SubscriptionUpdate, SubscriptionDelete, SubscriptionTerminate



urlpatterns = [
    # Create subscriptions
    path('subscription-create/', SubscriptionCreate.as_view(), name="subscription-create"),

    # Subscription List
    path('subscription-list/', SubscriptionList.as_view(), name="subscription-list"),

    # Edit subscriptions
    path('subscription-update/<int:pk>/', SubscriptionUpdate.as_view(), name="subscription-update"),

    # Delete subscriptions
    path('subscription-delete/<int:pk>/', SubscriptionDelete.as_view(), name="subscription-delete"),

    # Cancel subscription
    path('subscription-terminate/<int:pk>/', SubscriptionTerminate.as_view(), name="subscription-terminate"),
]