from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MonthlyBudget, YearlyBudget
from .forms import CreateYearlyBudgetForm, CreateMonthlyBudgetForm
from django.urls import reverse_lazy
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
        yearlybudget = YearlyBudget.objects.filter(year=year)
        if yearlybudget:
            yearlybudget.delete()
        form.instance.user = self.request.user
        return super(YearlyBudgetCreate, self).form_valid(form)
    
class YearlyBudgetUpdate(LoginRequiredMixin, UpdateView):
    model = YearlyBudget
    success_url = reverse_lazy('yearlybudget-list')
    fields = ['budget']
    template_name = 'budget/yearlybudget_update.html'
    context_object_name = 'budget'

class YearlyBudgetDelete(LoginRequiredMixin, DeleteView):
    model = YearlyBudget
    success_url = reverse_lazy('yearlybudget-list')
    template_name = 'budget/yearlybudget_delete.html'
    context_object_name = 'budget'

class MonthlyBudgetList(LoginRequiredMixin, ListView):
    model = MonthlyBudget
    template_name = 'budget/monthlybudget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class MonthlyBudgetCreate(LoginRequiredMixin, CreateView):
    model = MonthlyBudget
    template_name = 'budget/monthlybudget_create.html'
    success_url = reverse_lazy('monthlybudget-list')
    form_class = CreateMonthlyBudgetForm

    def form_valid(self, form):
        year = form.instance.year
        month = form.instance.month
        monthlybudget = MonthlyBudget.objects.filter(year=year).filter(month=month)
        if monthlybudget:
            monthlybudget.delete()
        form.instance.user = self.request.user
        return super(MonthlyBudgetCreate, self).form_valid(form)
    
class MonthlyBudgetUpdate(LoginRequiredMixin, UpdateView):
    model = MonthlyBudget
    success_url = reverse_lazy('monthlybudget-list')
    fields = ['budget']
    template_name = 'budget/monthlybudget_update.html'
    context_object_name = 'budget'

class MonthlyBudgetDelete(LoginRequiredMixin, DeleteView):
    model = MonthlyBudget
    success_url = reverse_lazy('monthlybudget-list')
    template_name = 'budget/monthlybudget_delete.html'
    context_object_name = 'budget'