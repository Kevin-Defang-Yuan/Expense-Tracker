from django .urls import path
from .views import SubscriptionCreate, SubscriptionList, SubscriptionUpdate, SubscriptionDelete



urlpatterns = [
    path('subscription-create/', SubscriptionCreate.as_view(), name="subscription-create"),
    path('subscription-list/', SubscriptionList.as_view(), name="subscription-list"),
    path('subscription-update/<int:pk>/', SubscriptionUpdate.as_view(), name="subscription-update"),
    path('subscription-delete/<int:pk>/', SubscriptionDelete.as_view(), name="subscription-delete"),
]