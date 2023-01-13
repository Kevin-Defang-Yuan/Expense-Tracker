from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from .models import Expense, Category
from datetime import datetime, timedelta, time
import dateutil.relativedelta
from .forms import CreateExpenseForm, CreateCategoryForm
from subscription.models import Subscription
import calendar
from budget.models import MonthlyBudget, YearlyBudget
from .models import BLS_2021_DATA, HOUSEHOLD_SIZE

# from django import template
# register = template.Library()



# Branch
# config
LIM_NUM = 10
MONTHS_NAME = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
EXPENSE_PAGINATION = 15
AVG_DAYS_PER_MONTH = 30.437
AVG_DAYS_PER_YEAR = 365
MIN_DAYS_PASSED = 14


from django.contrib.auth.mixins import LoginRequiredMixin

class ExpenseList(LoginRequiredMixin, ListView):
    model = Expense
    context_object_name = 'expenses'
    paginate_by = EXPENSE_PAGINATION
    template_name = 'base/expense_list.html'


    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        year = int(self.request.GET['year']) if 'year' in self.request.GET else None
        month = int(self.request.GET['month']) if 'month' in self.request.GET else None
        day = int(self.request.GET['day']) if 'day' in self.request.GET else None

        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)
        if day:
            queryset = queryset.filter(date__day=day)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET['year']) if 'year' in self.request.GET else None
        month = int(self.request.GET['month']) if 'month' in self.request.GET else None
        day = int(self.request.GET['day']) if 'day' in self.request.GET else None

        if year: context['year'] = year
        if month: context['month'] = MONTHS_NAME[month-1]
        if day: context['day'] = day

        return context


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
            # If the subscription is indefinite and the start date is earlier than the selected_start_date
            if subscription.indefinite and subscription.start_date <= selected_start_date:
                active_subscriptions.append(subscription)
            
            # Otherwise if subscriptions is not indefinite, calculate like normally
            elif not subscription.indefinite:
                sub_end_date = subscription.get_end_date
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
            for expense in expenses:
                total += expense.cost
            category_labels.append(category.name)

            category_data.append(round(float(total)))
        return (category_labels, category_data)


class YearlyPanel(PanelView):
    model = Expense
    template_name = 'base/yearly_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = datetime.today()
        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year

        context['year'] = year
        context['limited_expenses'] = self.query_limited_expenses(year=year)
        context['year_expenditure'] = self.get_expenditure_by_time_range(year=year)

        yearlybudget = YearlyBudget.objects.filter(user=self.request.user).filter(year=year).first()
        if yearlybudget:
            context['yearlybudget'] = yearlybudget.budget
            context['yearlybudget_object'] = yearlybudget
            context['surpass'] = True if yearlybudget.budget < context['year_expenditure'] else False

        categories_data = self.get_categories_expenditure_by_time_range(year=year)
        context['labels'] = categories_data[0]
        context['data'] = categories_data[1]

        context['active_subscriptions'] = self.get_subscriptions_by_time_range(year=year)

        context['expenditure_per_year'] = self.get_avg_expenditure_per_year()

        bar_graph = self.get_expenditure_by_year_per_month(year=year)
        context['bar_graph_labels'] = bar_graph[0]
        context['bar_graph_data'] = bar_graph[1]

        return context
    
    def get_expenditure_by_year_per_month(self, year):
        expenses = Expense.objects.filter(user=self.request.user).filter(date__year=year)
        month_list = [i for i in range(1, 12+1)]
        month_expenses = []
        for num in month_list:
            expenses_of_month = expenses.filter(date__month=num)
            total = 0
            for expense in expenses_of_month:
                total += expense.cost
            month_expenses.append(round(float(total)))
        return (month_list, month_expenses)
    
    def get_avg_expenditure_per_year(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None
        earliest_date = earliest_expense.date

        # We query all expenses except those in current month
        # The approach here is a bit backhanded, essentially we calculate previous month, get last day of previous month, and then grab all expenses using that date
        today = datetime.today().date()
        delta = today - earliest_date
        days_passed = delta.days + 1 # Add extra day for difference


        if days_passed < MIN_DAYS_PASSED:
            return None # Give message that returns WE NEED MORE DAYS
        

        expenditure_per_day = total / days_passed
        expenditure_per_year = float(expenditure_per_day) * AVG_DAYS_PER_YEAR
        return round(expenditure_per_year, 2)

class MonthlyPanel(PanelView):
    model = Expense
    template_name = 'base/monthly_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today()
        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year
        month = int(self.request.GET['month']) if 'month' in self.request.GET else today.month
        context['year'] = year
        context['month'] = month
        context['month_name'] = MONTHS_NAME[month-1]

        context['limited_expenses'] = self.query_limited_expenses(year=year, month=month)
        context['month_expenditure'] = self.get_expenditure_by_time_range(year=year, month=month)

        monthlybudget = MonthlyBudget.objects.filter(user=self.request.user).filter(year=year).filter(month=month).first()
        if monthlybudget:
            context['monthlybudget'] = monthlybudget.budget
            context['monthlybudget_object'] = monthlybudget
            context['surpass'] = True if monthlybudget.budget < context['month_expenditure'] else False

        categories_data = self.get_categories_expenditure_by_time_range(year=year, month=month)
        context['labels'] = categories_data[0]
        context['data'] = categories_data[1]

        context['expenditure_per_month'] = self.get_avg_expenditure_per_month()

        context['active_subscriptions'] = self.get_subscriptions_by_time_range(year=year, month=month)
        bar_graph = self.get_expenditure_by_month_per_day(year=year, month=month)
        context['bar_graph_labels'] = bar_graph[0]
        context['bar_graph_data'] = bar_graph[1]

        # subs = Subscription.objects.all()
        # for sub in subs:
        #     print(f'Start: {sub.start_date}, quantity: {sub.quantity}, cycle: {sub.cycle}, End: {sub.get_end_date()}')

    
        return context
    
    def get_avg_expenditure_per_month(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None
        earliest_date = earliest_expense.date

        # We query all expenses except those in current month
        # The approach here is a bit backhanded, essentially we calculate previous month, get last day of previous month, and then grab all expenses using that date
        today = datetime.today().date()
        delta = today - earliest_date
        days_passed = delta.days + 1 # Add extra day for difference

        print("Days passed, ", days_passed)
        if days_passed < MIN_DAYS_PASSED:
            return None # Give message that returns WE NEED MORE DAYS
        

        expenditure_per_day = total / days_passed
        expenditure_per_month = float(expenditure_per_day) * AVG_DAYS_PER_MONTH
        return round(expenditure_per_month, 2)
    
    def get_expenditure_by_month_per_day(self, year, month):
        expenses = Expense.objects.filter(user=self.request.user)
        expenses = expenses.filter(date__year=year).filter(date__month=month)

        days = calendar.monthrange(year, month)[1]
        day_list = [i for i in range(1, days+1)]
        day_expenses = []
        for num in day_list:
            expenses_of_day = expenses.filter(date__day=num)
            total = 0
            for expense in expenses_of_day:
                total += expense.cost
            day_expenses.append(round(float(total)))
        return (day_list, day_expenses)







class DailyPanel(PanelView):
    model = Expense
    template_name = 'base/daily_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # subscriptions = Subscription.objects.all()[0]
        
        # Determine Day (from GET params or assume Today Otherwise)
        today = datetime.today()
        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year
        month = int(self.request.GET['month']) if 'month' in self.request.GET else today.month
        day = int(self.request.GET['day']) if 'day' in self.request.GET else today.day
        context['limited_expenses'] = self.query_limited_expenses(year=year, month=month, day=day)
        context['year'] = year
        context['month'] = month
        context['month_name'] = MONTHS_NAME[month-1]
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
        context['data'] = categories_data[1]
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

    
  
    
    def get_this_day_expenditure(self, year, month, day):
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
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_create.html'

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
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_update.html'

# Default template is {expense}_confirm_delete.html
class ExpenseDelete(LoginRequiredMixin, DeleteView):
    model = Expense
    context_object_name = 'expense'
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_delete.html'


class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'base/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class CategoryCreate(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CreateCategoryForm
    template_name = 'base/category_create.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CategoryCreate, self).form_valid(form)

class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    success_url = reverse_lazy('category-list')
    template_name = 'base/category_update.html'
    context_object_name = 'category'

class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')
    template_name = 'base/category_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('pk')
        expenses_under_category = Expense.objects.filter(user=self.request.user).filter(category=category_id)
        context['expenses_under_category'] = expenses_under_category
        return context


