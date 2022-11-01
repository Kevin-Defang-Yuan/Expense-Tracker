from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .models import Expense

# We are using a class based view to handle logging in
from django.contrib.auth.views import LoginView

# Use these to handle registering
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# We need to restrict access for unauthenticated users
# This is easy to do with funciton based views using simple decorators or middleware
# But in this case, we will use mixins and add it to every single view that should be restricted
# The order of how we add it MATTERS!
from django.contrib.auth.mixins import LoginRequiredMixin

# I don't know what the default is
class CustomLoginView(LoginView):
    template_name = 'base/login.html'

    # This view already handles the fields for you
    fields = '__all__'

    # If a user is authenticated, they should be redirected back to dashboard
    redirect_authenticated_user = True

    # When users successfully login, we want to send them to dashboard. 
    def get_success_url(self):
        return reverse_lazy('dashboard')


# Registration
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Once form is submitted, we need ot make sure that user is logged in. 
        user = form.save() # Once the form is saved, the return value is going to be the user because we are working with the user create form
        if user is not None: 
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    # Prevents users from accessing register page after they are already authenticated
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('dashboard')
        return super(RegisterPage, self).get(*args, **kwargs)





# ORDER MATTERS, adding LoginRequiredMixin BEFORE ListView and all the other views as well. 
class Dashboard(LoginRequiredMixin, ListView):
    model = Expense

    # Overrides the default queryset name of 'object_list' into something that we choose.
    # This affects that the html file looks for
    context_object_name = 'expenses'

    # Default is expense_list.html
    template_name = 'base/dashboard.html'

    # manipulate the context before returning it
    def get_context_data(self, **kwargs):
        # context is a dictionary that contains the data
        # for instance, we can do context['color'] = 'red'
        # Here we grab the context
        context = super().get_context_data(**kwargs)

        # Then we filter out expenses pertaining to specific user
        context['expenses'] = context['expenses'].filter(user=self.request.user)

        # Next we calculate total expenses and save that into the context dictionary
        total_expense = 0
        for item in context['expenses']:
            total_expense += item.cost
        context['total_expense'] = total_expense

        # Logic for searching
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['expenses'] = context['expenses'].filter(category__startswith=search_input)

        # Pass the search_input back to context
        context['search_input'] = search_input

        # Here is some other code that the video showed to filter based on completed or not, i think? 
        # context['count'] = context['expenses'].filter(complete=False)
        return context

class ExpenseDetail(LoginRequiredMixin, DetailView):
    model = Expense
    context_object_name = 'expense'

    # Default is {expense}_detail.html
    template_name = 'base/expense.html'

# Default template is {expense}_form.html
class ExpenseCreate(LoginRequiredMixin, CreateView):
    model = Expense

    # Lists all the items in the field: fields = '__all__'
    # Can use this instead
    #   fields = ['category', 'cost']
    # Or alternatively, we can set our own ExpenseForm class
    #   form_class = ExpenseForm

    # However, since we don't want users to pick which user, we need to take out the user field and specify the fields manually
    fields = ['category', 'description', 'date', 'cost']

    # So if everything goes correctly, redirect user to the url named 'dashboard'
    success_url = reverse_lazy('dashboard')

    # We want the form to automatically know which user to submit the data
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExpenseCreate, self).form_valid(form)


# Default is {expense}_form.html
class ExpenseUpdate(LoginRequiredMixin, UpdateView):
    model = Expense
    fields = ['category', 'description', 'date', 'cost']
    success_url = reverse_lazy('dashboard')

# Default template is {expense}_confirm_delete.html
class ExpenseDelete(LoginRequiredMixin, DeleteView):
    model = Expense
    context_object_name = 'expense'
    success_url = reverse_lazy('dashboard')


