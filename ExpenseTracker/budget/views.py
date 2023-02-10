from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MonthlyBudget, YearlyBudget
from .forms import CreateYearlyBudgetForm, CreateMonthlyBudgetForm, UpdateYearlyBudgetForm, UpdateMonthlyBudgetForm
from datetime import date
from django.urls import reverse_lazy
from django.contrib import messages
# Create your views here.

class YearlyBudgetList(LoginRequiredMixin, ListView):
    model = YearlyBudget
    template_name = 'budget/yearlybudget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class YearlyBudgetCreate(LoginRequiredMixin, CreateView):
    model = YearlyBudget
    template_name = 'budget/yearlybudget_create.html'
    success_url = reverse_lazy('yearlybudget-list')
    form_class = CreateYearlyBudgetForm

    def form_valid(self, form):
        year = form.instance.year
        yearlybudget = YearlyBudget.objects.filter(user=self.request.user).filter(year=year)
        if yearlybudget:
            yearlybudget.delete()
        form.instance.user = self.request.user
        return super(YearlyBudgetCreate, self).form_valid(form)
    
    def get_initial(self):
        year = None
        month = None
        if 'year' in self.request.GET:
            year = self.request.GET['year']    
        # Otherwise, we just populate with today
        else:
            today = date.today()
            year = today.year
        return {
            'year': year,
        }

     # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully created!')
        return self.request.session['previous_page']
    
class YearlyBudgetUpdate(LoginRequiredMixin, UpdateView):
    model = YearlyBudget
    success_url = reverse_lazy('yearlybudget-list')
    form_class = UpdateYearlyBudgetForm
    template_name = 'budget/yearlybudget_update.html'
    context_object_name = 'budget'

     # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully edited!')
        return self.request.session['previous_page']

class YearlyBudgetDelete(LoginRequiredMixin, DeleteView):
    model = YearlyBudget
    success_url = reverse_lazy('yearlybudget-list')
    template_name = 'budget/yearlybudget_delete.html'
    context_object_name = 'budget'

    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully deleted!')
        return self.request.session['previous_page']

class MonthlyBudgetList(LoginRequiredMixin, ListView):
    model = MonthlyBudget
    template_name = 'budget/monthlybudget_list.html'
    context_object_name = 'budgets'

    # We want to display the month name, not the month number
    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        for budget in qs:
            budget.month_name = MonthlyBudget.MONTH_CHOICES[budget.month-1][1]
        return qs
    


class MonthlyBudgetCreate(LoginRequiredMixin, CreateView):
    model = MonthlyBudget
    template_name = 'budget/monthlybudget_create.html'
    success_url = reverse_lazy('monthlybudget-list')
    form_class = CreateMonthlyBudgetForm

    def form_valid(self, form):
        year = form.instance.year
        month = form.instance.month
        monthlybudget = MonthlyBudget.objects.filter(user=self.request.user).filter(year=year).filter(month=month)
        if monthlybudget:
            monthlybudget.delete()
        form.instance.user = self.request.user
        return super(MonthlyBudgetCreate, self).form_valid(form)
    
    def get_initial(self):
        year = None
        month = None
        if 'year' in self.request.GET and 'month' in self.request.GET:
            year = self.request.GET['year']
            month = self.request.GET['month']        
        # Otherwise, we just populate with today
        else:
            today = date.today()
            month = today.month
            year = today.year
        return {
            'year': year,
            'month': month
        }

     # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully created!')
        return self.request.session['previous_page']
    
    
class MonthlyBudgetUpdate(LoginRequiredMixin, UpdateView):
    model = MonthlyBudget
    success_url = reverse_lazy('monthlybudget-list')
    form_class = UpdateMonthlyBudgetForm
    template_name = 'budget/monthlybudget_update.html'
    context_object_name = 'budget'

    def get_initial(self):
        if 'year' in self.request.GET and 'month' in self.request.GET:
            year = self.request.GET['year']
            month = self.request.GET['month']
            return {
                'year': year,
                'month': month
            }
     # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully edited!')
        return self.request.session['previous_page']

class MonthlyBudgetDelete(LoginRequiredMixin, DeleteView):
    model = MonthlyBudget
    success_url = reverse_lazy('monthlybudget-list')
    template_name = 'budget/monthlybudget_delete.html'
    context_object_name = 'budget'

    # We want to display the month name, not the month number
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month_name'] = MonthlyBudget.MONTH_CHOICES[self.get_object().month-1][1]
        return context
    
    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Budget successfully deleted!')
        return self.request.session['previous_page']

    