from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from .models import Expense, Category
from datetime import datetime, timedelta, time
from .forms import CreateExpenseForm
from .models import Subscription
import calendar

from django import template
register = template.Library()



# Branch
# year
LIM_NUM = 100
MONTHS_NAME = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

from django.contrib.auth.mixins import LoginRequiredMixin

class PanelView(LoginRequiredMixin, TemplateView):
    model = Expense

    def query_limited_expenses(self, year=None, month=None, day=None):
        expense_list = self.get_expenses_by_time_range(year=year, month=month, day=day)
        return expense_list.order_by('date')[:LIM_NUM]
    
    def get_expenses_by_time_range(self, year=None, month=None, day=None):
        expense_list = Expense.objects.all().filter(user=self.request.user)
        if year:
            expense_list = expense_list.filter(date__year=year)
        if month:
            expense_list = expense_list.filter(date__month=month)
        if day:
            expense_list = expense_list.filter(date__day=day)
        return expense_list
    
    def get_expenditure_by_time_range(self, year=None, month=None, day=None):
        expense_list = self.get_expenses_by_time_range(year=year, month=month, day=day)
        total = 0
        for expense in expense_list:
            total += expense.cost
        return total
    
    def get_subscriptions_by_time_range(self, year=None, month=None, day=None):
        subscriptions = Subscription.objects.filter(user=self.request.user)

        # start by assuming year
        selected_start_date = datetime(int(year), 1, 1).date()
        selected_end_date = datetime(int(year), 12, 31).date()

        if month:
            selected_start_date = datetime(int(year), int(month), 1).date()
            selected_end_date = datetime(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).date()
        
        if day:
            selected_start_date = datetime(int(year), int(month), int(day)).date()
            selected_end_date = datetime(int(year), int(month), int(day)).date()

        # selected_date = datetime(int(year), int(month), int(day)).date()
        active_subscriptions = []
        for subscription in subscriptions:
            sub_end_date = subscription.get_end_date()
            sub_start_date = subscription.start_date
            if day:
                if selected_start_date >= sub_start_date and selected_end_date <= sub_end_date:
                    active_subscriptions.append(subscription)
            else:
                if sub_end_date >= selected_start_date and sub_start_date <= selected_end_date:
                    active_subscriptions.append(subscription)

            

            
        return active_subscriptions
    
    def get_total_expenditure(self):
        expenses = Expense.objects.filter(user=self.request.user)
        total = 0
        for expense in expenses:
            total += expense.cost
        return total
    
    def get_categories_expenditure_by_time_range(self, year=None, month=None, day=None):
        categories = Category.objects.filter(user=self.request.user)
        category_labels = []
        category_data = []
        for category in categories:
            expenses = category.all_expenses.filter(user=self.request.user)
            
            if year:
                expenses = expenses.filter(date__year=year)
            if month:
                expenses = expenses.filter(date__month=month)
            if day:
                expenses = expenses.filter(date__day=day)
            total = 0
            print("EXPENSES")
            print(expenses)
            print("ENDDDD")
            for expense in expenses:
                total += expense.cost
            category_labels.append(category.name)

            category_data.append(round(float(total)))
        return (category_labels, category_data)


class YearlyPanel(PanelView):
    model = Expense
    template_name = 'base/yearly_panel.html'

class MonthlyPanel(PanelView):
    model = Expense
    template_name = 'base/monthly_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today()

        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year
        month = int(self.request.GET['month']) if 'month' in self.request.GET else today.month
        context['year'] = year
        context['month'] = MONTHS_NAME[month-1]

        context['limited_expenses'] = self.query_limited_expenses(year=year, month=month)
        context['month_expenditure'] = self.get_expenditure_by_time_range(year=year, month=month)

        categories_data = self.get_categories_expenditure_by_time_range(year=year, month=month)
        context['labels'] = categories_data[0]
        context['data'] = categories_data[1]

        context['expenditure_per_month'] = self.get_expenditure_per_month()

        context['active_subscriptions'] = self.get_subscriptions_by_time_range(year=year, month=month)
    
        return context
    
    def get_expenditure_per_month(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None
        
        earliest_date = earliest_expense.date
        today = datetime.today().date()
        print("early month", earliest_date.month)
        print("late month", today.month)
        months_passed = (today.year - earliest_date.year) * 12 + today.month - earliest_date.month
        return round(total / months_passed, 2)




class DailyPanel(PanelView):
    model = Expense
    template_name = 'base/daily_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subscriptions = Subscription.objects.all()[0]
        

        # Determine Day (from GET params or assume Today Otherwise)
        today = datetime.today()
        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year
        month = int(self.request.GET['month']) if 'month' in self.request.GET else today.month
        day = int(self.request.GET['day']) if 'day' in self.request.GET else today.day
        context['limited_expenses'] = self.query_limited_expenses(year=year, month=month, day=day)
        context['year'] = year
        context['month'] = MONTHS_NAME[month-1]
        context['day'] = day

        
        # Expenditure Totals
        context['day_expenditure'] = self.get_expenditure_by_time_range(year=year, month=month, day=day)
        context['this_month_total'] = self.get_this_month_expenditure()
        context['this_year_total'] = self.get_this_year_expenditure()

        # Expenditure Per Day
        context['expenditure_per_day'] = self.get_expenditure_per_day()

        # Subscriptions
        context['active_subscriptions'] = self.get_subscriptions_by_time_range(year=year, month=month, day=day)

        categories_data = self.get_categories_expenditure_by_time_range(year=year, month=month, day=day)
        context['labels'] = categories_data[0]
        print(context['labels'])
        context['data'] = categories_data[1]
        print(categories_data[1])

        print(self.get_expenditure_per_day())
        return context
    
    def get_expenditure_per_day(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None

        earliest_date = earliest_expense.date
        today = datetime.today().date()
        delta = today - earliest_date
        days_passed = delta.days + 1 # Add extra day for difference
        return round(total / days_passed, 2)

    
    # def get_categories_expenditure(self):
    #     categories = Category.objects.filter(user=self.request.user)
    #     category_labels = []
    #     category_data = []
    #     for category in categories:
    #         expenses = category.all_expenses.all()
    #         total = 0
    #         for expense in expenses:
    #             total += expense.cost
    #         category_labels.append(category.name)

    #         category_data.append(round(float(total)))
    #     return (category_labels, category_data)
    
    # def query_limited_expenses_entries(self):
    #     return Expense.objects.all().filter(user=self.request.user).order_by('-date')[:LIM_NUM]
    
    def get_this_day_expenditure(self, year, month, day):
        # today = datetime.today()
        # tomorrow = today + timedelta(1)
        # today_start = datetime.combine(today, time())
        # today_end = datetime.combine(tomorrow, time())
        #this_day_expenses = Expense.objects.all().filter(user=self.request.user).filter(date__lte=today_start, date__gte=today_end)
        expense_list = Expense.objects.all().filter(user=self.request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day)
        total = 0
        for expense in expense_list:
            total += expense.cost
        return total
    
    def get_this_month_expenditure(self):
        today = datetime.today()
        this_month = today.month
        this_year = today.year
        this_month_expenses = Expense.objects.all().filter(user=self.request.user).filter(date__year=this_year, date__month=this_month)
        total = 0
        for expense in this_month_expenses:
            total += expense.cost
        return total
    
    def get_this_year_expenditure(self):
        today = datetime.today()
        this_year = today.year
        this_year_expenses = Expense.objects.all().filter(user=self.request.user).filter(date__year=this_year)
        total = 0
        for expense in this_year_expenses:
            total += expense.cost
        return total
        




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
    form_class = CreateExpenseForm

    # Lists all the items in the field: fields = '__all__'
    # Can use this instead
    #   fields = ['category', 'cost']
    # Or alternatively, we can set our own ExpenseForm class
    #   form_class = ExpenseForm

    # So if everything goes correctly, redirect user to the url named 'dashboard'
    success_url = reverse_lazy('today-panel')

    # We want the form to automatically know which user to submit the data
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExpenseCreate, self).form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(ExpenseCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


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



