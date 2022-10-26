from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Expense

# Tutorial Mode
# Create your views here.

class Dashboard(ListView):
    model = Expense

    # Overrides the default queryset name of 'object_list' into something that we choose.
    # This affects that the html file looks for
    context_object_name = 'expenses'

    # Default is expense_list.html
    template_name = 'base/dashboard.html'

class ExpenseDetail(DetailView):
    model = Expense
    context_object_name = 'expense'

    # Default is {expense}_detail.html
    template_name = 'base/expense.html'

# Default template is {expense}_form.html
class ExpenseCreate(CreateView):
    model = Expense

    # Lists all the items in the field
    # Can use this instead
    #   fields = ['category', 'cost']
    # Or alternatively, we can set our own ExpenseForm class
    #   form_class = ExpenseForm
    fields = '__all__'

    # So if everything goes correctly, redirect user to the url named 'dashboard'
    success_url = reverse_lazy('dashboard')

# Default is {expense}_form.html
class ExpenseUpdate(UpdateView):
    model = Expense
    fields = '__all__'
    success_url = reverse_lazy('dashboard')

# Default template is {expense}_confirm_delete.html
class ExpenseDelete(DeleteView):
    model = Expense
    context_object_name = 'expense'
    success_url = reverse_lazy('dashboard')


