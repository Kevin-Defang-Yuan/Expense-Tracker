from django.shortcuts import render

# We are using a class based view to handle logging in
from django.contrib.auth.views import LoginView

# Use these to handle registering
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

# Create your views here.
# I don't know what the default is
class CustomLoginView(LoginView):
    template_name = 'userauth/login.html'

    # This view already handles the fields for you
    fields = '__all__'

    # If a user is authenticated, they should be redirected back to dashboard
    redirect_authenticated_user = True

    # When users successfully login, we want to send them to dashboard. 
    def get_success_url(self):
        return reverse_lazy('daily-panel')


# Registration
class RegisterPage(FormView):
    template_name = 'userauth/register.html'
    form_class = UserCreationForm
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
            return redirect('today-panel')
        return super(RegisterPage, self).get(*args, **kwargs)