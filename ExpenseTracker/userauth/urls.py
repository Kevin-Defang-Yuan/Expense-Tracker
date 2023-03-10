from django .urls import path
from .views import CustomLoginView, RegisterPage
from django.contrib.auth.views import LogoutView
from .forms import UserLoginForm

urlpatterns = [
    path('login/', CustomLoginView.as_view(authentication_form = UserLoginForm), name='login'),

    # Instead of customzing our logout view, we just use it directly here after importing it
    # Next page dicates that once we log out, the user is sent to the specified location
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    # as_view is used to determine if the request is get or post
]