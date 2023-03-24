from django.shortcuts import render

# We are using a class based view to handle logging in
from django.contrib.auth.views import LoginView

# Use these to handle registering
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

from subscription.models import Subscription
from base.models import Expense

"""
LoginView
"""
class CustomLoginView(LoginView):
    template_name = 'userauth/login.html'

    # This view already handles the fields for you
    fields = '__all__'

    # If a user is authenticated, they should be redirected back to daily panel
    redirect_authenticated_user = True

    # When users successfully login, we want to send them to daily panel. 
    def get_success_url(self):

        # Here we want to perform calculations for authenticated user and initialize expenses that are created today based on a sub
        subscriptions = Subscription.objects.all().filter(user=self.request.user)
        for subscription in subscriptions:
            if subscription.is_active:
                existing_expense_instances = subscription.get_existing_expense_instances()
                for expense in existing_expense_instances:
                    existing_expense = Expense.objects.filter(subscription=expense.subscription, date=expense.date, user=self.request.user).first()
                    if not existing_expense:
                        expense.save()

        return reverse_lazy('daily-panel')


"""
Register View
"""
class RegisterPage(FormView):
    template_name = 'userauth/register.html'
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('daily-panel')

    def form_valid(self, form):
        # Once form is submitted, we need ot make sure that user is logged in. 
        user = form.save() # Once the form is saved, the return value is going to be the user because we are working with the user create form
        if user is not None: 
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    # Prevents users from accessing register page after they are already authenticated
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('daily-panel')
        return super(RegisterPage, self).get(*args, **kwargs)