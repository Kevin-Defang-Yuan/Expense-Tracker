from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from .models import Expense, Category
from datetime import datetime, timedelta, time, date
import dateutil.relativedelta
from .forms import CreateExpenseForm, CreateCategoryForm
from subscription.models import Subscription
import calendar
from budget.models import MonthlyBudget, YearlyBudget
from .models import BLS_2021_DATA, HOUSEHOLD_SIZE
from .forms import EARLIEST_YEAR, LATEST_YEAR
from django_filters.views import FilterView
from .filters import ExpenseFilter
import re
from calendar import monthrange, isleap
from django.contrib import messages
import seaborn as sns
import colorcet as cc


LIM_NUM = 6
MONTHS_NAME = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
EXPENSE_PAGINATION = 10
AVG_DAYS_PER_MONTH = 30.437
AVG_DAYS_PER_YEAR = 365
MIN_DAYS_PASSED = 14
DAYS_BUFFER = 4
WARNING_THRESHOLD = 1.1
BAD_THRESHOLD = 1.3


from django.contrib.auth.mixins import LoginRequiredMixin

"""
View for expenses as a list (filtered by time parameters and other user input). Uses FilterView. 
"""
class ExpenseList(LoginRequiredMixin, FilterView):
    model = Expense
    context_object_name = 'expenses'
    paginate_by = EXPENSE_PAGINATION
    template_name = 'base/expense_list.html'
    filterset_class = ExpenseFilter

    """
    Returns a filtered list of expenses (based on time parameters) and order by date descending. 
    """
    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        year = int(self.request.GET['year']) if 'year' in self.request.GET and self.request.GET['year'] else None
        month = int(self.request.GET['month']) if 'month' in self.request.GET and self.request.GET['month'] else None
        day = int(self.request.GET['day']) if 'day' in self.request.GET and self.request.GET['day'] else None

        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)
        if day:
            queryset = queryset.filter(date__day=day)
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET['year']) if 'year' in self.request.GET and self.request.GET['year'] else None
        month = int(self.request.GET['month']) if 'month' in self.request.GET and self.request.GET['month'] else None
        day = int(self.request.GET['day']) if 'day' in self.request.GET and self.request.GET['day'] else None

        if year: context['year'] = year
        if month: context['month'], context['month_num'] = MONTHS_NAME[month-1], month
        if day: context['day'] = day

        context['filterset'] = self.filterset

        return context




    




  
"""
Base class for DailyView, MonthlyView, and YearlyView
Contains some functions that all three views utilize
"""
class PanelView(LoginRequiredMixin, TemplateView):
    model = Expense

    """
    Filters only the first X number of expenses for the expense table. 

    Args: 
        year (Int), month (Int), day (Int)
    
    Returns:
        expense_list: A list of expenses belonging to the date params truncated to LIM_NUM expenses
    """
    def query_limited_expenses(self, year=None, month=None, day=None):
        expense_list = self.get_expenses_by_time_range(year=year, month=month, day=day)
        return expense_list.order_by('-date')[:LIM_NUM]
    
    """
    Returns a filtered list of expenses based on time parameters. 

    Args: 
        year (Int), month (Int), day (Int)
    
    Returns:
        expense_list: A list of expenses belong to the date params

    """
    def get_expenses_by_time_range(self, year=None, month=None, day=None):
        expense_list = Expense.objects.all().filter(user=self.request.user)
        if year:
            expense_list = expense_list.filter(date__year=year)
        if month:
            expense_list = expense_list.filter(date__month=month)
        if day:
            expense_list = expense_list.filter(date__day=day)
        return expense_list
    

    """
    Calculates total expenditure based on time parameters

    Args: 
        year (Int), month (Int), day (Int)
    
    Returns:
        total: the total expenditure
    """
    def get_expenditure_by_time_range(self, year=None, month=None, day=None):
        expense_list = self.get_expenses_by_time_range(year=year, month=month, day=day)
        total = 0
        for expense in expense_list:
            total += expense.cost
        return total
    
    """
    Returns a tuple of active subscriptions and was active subscriptions based on time parameters. 

    Args: 
        year (Int), month (Int), day (Int)
    
    Returns:
        tuple: active_subscriptions as first index and was_active_subscriptions as second index
    """
    def get_subscriptions_by_time_range(self, year=None, month=None, day=None):
        subscriptions = Subscription.objects.filter(user=self.request.user)

        # Determine start and end dates to filer for subscriptions
        # start by assuming year
        selected_start_date = datetime(int(year), 1, 1).date()
        selected_end_date = datetime(int(year), 12, 31).date()

        if month:
            selected_start_date = datetime(int(year), int(month), 1).date()
            selected_end_date = datetime(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).date()
        
        if day:
            selected_start_date = datetime(int(year), int(month), int(day)).date()
            selected_end_date = datetime(int(year), int(month), int(day)).date()

        # Here we want to aggregate two lists:
        # One list for active subscriptions
        # One list for subscriptions that are not active but were active in that time period
        active_subscriptions = []
        was_active_subscriptions = []
        for subscription in subscriptions:
            if subscription.was_active_subscription_in_range(selected_start_date, selected_end_date, day):
                was_active_subscriptions.append(subscription)
            if subscription.is_active_subscription_in_range(selected_start_date, selected_end_date, day):
                active_subscriptions.append(subscription)
            

        # Return both lists as a tuple            
        return (active_subscriptions, was_active_subscriptions)
    
    """
    Returns total user expenditure. Useful for calculating some aggregating user statistics

    Args:

    Returns:
        total: total expenditure
    """
    def get_total_expenditure(self):
        expenses = Expense.objects.filter(user=self.request.user)
        total = 0
        for expense in expenses:
            total += expense.cost
        return total
    

    """
    Returns a tuple (labels, data values) that consists of spending based on categories and filtered by time parameters. 

    Args: 
        year (Int), month (Int), day (Int)
    
    Returns:
        tuple: category_label as first index and category_data as second index
    """
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
    

    """
    Returns the appropriate budget indicator based on user's current month spending rate compared to remaining month spending rate to reach budget
    
    Args:
        monthlybudget (MonthlyBudget): the monthlybudget for the month
        month_expenditure (float): the total user spent for the month
        month (int): month
        year (int): year
    
    Returns
        str: 'COMPLETE_UNDER' for a previous month where user was under budget
                or 'COMPLETE_OVER' for a previous month where the user was over budget
                or 'CURRENT_GOOD' for the current month where the user is on pace to meeting budget
                or 'CURRENT_WARNING' for the current month where is user is slightly off pace to meeting budget
                or 'CURRNT_BAD' for the current month where the user is very off pace to meeting budget
                or 'CURRNT_OVER' for the current month if the user if over the budget
                or 'NO_BUDGET' if the user does not have a budget for the month
                or 'FUTURE_UNKNOWN' if the user created a budget for a month in the future
    """
    def get_monthly_budget_indicator(self, monthlybudget, month_expenditure, month, year):
        today = datetime.today()

        # If no budget
        if not monthlybudget:
            return 'NO_BUDGET'
        # Calculations for CURRENT (meaning the month is the current month)
        elif month == today.month and year == today.year:
            # Get current monthly spending rate. If total days passed less than a week, assume a week, which is forgiving threshold
            current_monthly_spending_rate = month_expenditure / today.day if today.day > DAYS_BUFFER else month_expenditure / DAYS_BUFFER
            
            # Get remaining monthly spending rate
            remaining_days = monthrange(today.year, today.month)[1] - today.day
            remaining_budget = float(monthlybudget.budget) - month_expenditure

            # If we surpass, then set to CURRENT_OVER
            if remaining_budget < 0:
                return 'CURRENT_OVER'
            
            # Calculations for remaining spending rate. Buffered if there is limited user data.
            remaining_monthly_spending_rate = remaining_budget / remaining_days if today.day > DAYS_BUFFER else remaining_budget / (remaining_days - DAYS_BUFFER)

            if current_monthly_spending_rate <= (remaining_monthly_spending_rate * WARNING_THRESHOLD):
                return 'CURRENT_GOOD'
            elif current_monthly_spending_rate <= (remaining_monthly_spending_rate * BAD_THRESHOLD):
                return 'CURRENT_WARNING'
            else:
                return 'CURRENT_BAD'

        # Calculations for COMPLETE (meaning month has already passed) or FUTURE_UNKNOWN
        else:

            # Check if future
            if year > today.year or (month > today.month and year >= today.year):
                return 'FUTURE_UNKNOWN'
            else:
                surpass = True if float(monthlybudget.budget) < month_expenditure else False
                return 'COMPLETE_OVER' if surpass else 'COMPLETE_UNDER'
    
    """
    Returns the appropriate budget indicator based on user's current year spending rate compared to remaining year spending rate to reach budget
    
    Args: 
        yearlybudget (YearlyBudget): the yearlybudget
        year_expenditure (float): the total spent for the year
        year (int): year
    
    Returns
        str: 'COMPLETE_UNDER' for a previous month where user was under budget
                or 'COMPLETE_OVER' for a previous month where the user was over budget
                or 'CURRENT_GOOD' for the current month where the user is on pace to meeting budget
                or 'CURRENT_WARNING' for the current month where is user is slightly off pace to meeting budget
                or 'CURRNT_BAD' for the current month where the user is very off pace to meeting budget
                or 'CURRNT_OVER' for the current month if the user if over the budget
                or 'NO_BUDGET' if the user does not have a budget for the month
                or 'FUTURE_UNKNOWN' if the user created a budget for a month in the future
    
    """
    def get_yearly_budget_indicator(self, yearlybudget, year_expenditure, year):
        today = date.today()

        # If no budget
        if not yearlybudget:
            return 'NO_BUDGET'
        # Calculations for CURRENT (meaning the year is the current year)
        elif year == today.year:
            # Caluclate how many days has passed since Jan 1st
            days_passed = (today - date(year, 1, 1)).days
            # Get current yearly spending rate. If total days passed less than a week, assume a week, which is forgiving threshold
            current_yearly_spending_rate = year_expenditure / days_passed if days_passed > DAYS_BUFFER else year_expenditure / DAYS_BUFFER
            
            # Get remaining yearly spending rate
            remaining_days = (365 + calendar.isleap(year)) - days_passed
            remaining_budget = float(yearlybudget.budget) - year_expenditure
            
            # If we surpass, then set to CURRENT_OVER
            if remaining_budget < 0:
                return 'CURRENT_OVER'

            # Calculations of remaining spending rate. Buffered if there is little data. 
            remaining_yearly_spending_rate = remaining_budget / remaining_days if days_passed > DAYS_BUFFER else remaining_budget / (remaining_days - DAYS_BUFFER)

            if current_yearly_spending_rate <= (remaining_yearly_spending_rate * WARNING_THRESHOLD):
                return 'CURRENT_GOOD'
            elif current_yearly_spending_rate <= (remaining_yearly_spending_rate * BAD_THRESHOLD):
                return 'CURRENT_WARNING'
            else:
                return 'CURRENT_BAD'

        # Calculations for COMPLETE (meaning month has already passed) or FUTURE_UNKNOWN
        else:

            # if in future
            if year > today.year:
                return 'FUTURE_UNKNOWN'
            else:
                surpass = True if float(yearlybudget.budget) < year_expenditure else False
                return 'COMPLETE_OVER' if surpass else 'COMPLETE_UNDER'

"""
View for a yearly summary of expenditure
"""
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

        # Arrow Nav for monthly view
        # Context for view for the previous month
        context['prev_date_year'] = year - 1

        # Context for view for the next month
        context['next_date_year'] = year + 1

        # Pass in year range for the year select form
        context['year_range'] = [i for i in range(EARLIEST_YEAR, LATEST_YEAR)]

        # Only pass in context for yearlybudget information if there is a yearlybudget
        yearlybudget = YearlyBudget.objects.filter(user=self.request.user).filter(year=year).first()
        if yearlybudget:
            context['yearlybudget'] = yearlybudget.budget
            context['yearlybudget_object'] = yearlybudget
            context['surpass'] = True if yearlybudget.budget < context['year_expenditure'] else False
            context['progress_width'] = int(context['year_expenditure'] / context['yearlybudget'] * 100)

        # Pie Chart Stuff
        categories_data = self.get_categories_expenditure_by_time_range(year=year)
        categories_data_sum = sum(categories_data[1])
        if categories_data_sum == 0:
            context['labels'] = ['None']
            context['data'] = [1]
            context['background_colors'] = ['LightGray']
        else:
            context['labels'] = categories_data[0]
            context['data'] = categories_data[1]
            # Use of glasbey to generate distinct colors
            context['background_colors'] = sns.color_palette(cc.glasbey, n_colors=len(context['labels'])).as_hex() 


        context['active_subscriptions'], context['was_active_subscriptions'] = self.get_subscriptions_by_time_range(year=year)

        context['expenditure_per_year'] = self.get_avg_expenditure_per_year()

        # Bar Graph Stuff
        bar_graph = self.get_expenditure_by_year_per_month(year=year)
        context['bar_graph_labels'] = bar_graph[0]
        context['bar_graph_data'] = bar_graph[1]

        context['yearly_budget_indicator'] = self.get_yearly_budget_indicator(yearlybudget, float(self.get_expenditure_by_time_range(year=year)), year)

        return context
    
    """
    Returns a tuple for spending per month across a year for bar graph

    Args:
        year (int): year
    
    Returns:
        tuple: a list of months in integer form as the first index
                and a list comprised of expenditure for each month
    """
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
    
    """
    Returns the average expenditure per year for a user. 
    An approximation based on calculating average expenditure per day, and then multiplying by average days per year. 

    Args:

    Returns:
        expenditure_per_year (float): average yearly spending
    """
    def get_avg_expenditure_per_year(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None
        earliest_date = earliest_expense.date

        today = datetime.today().date()
        delta = today - earliest_date
        days_passed = delta.days + 1 # Add extra day for difference


        if days_passed < MIN_DAYS_PASSED:
            return None # Give message that returns WE NEED MORE DAYS
        
        expenditure_per_day = total / days_passed
        expenditure_per_year = float(expenditure_per_day) * AVG_DAYS_PER_YEAR
        return round(expenditure_per_year, 2)

"""
View for summary statistics of a particular month
"""
class MonthlyPanel(PanelView):
    model = Expense
    template_name = 'base/monthly_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today()
        year = int(self.request.GET['year']) if 'year' in self.request.GET else today.year
        month = int(self.request.GET['month']) if 'month' in self.request.GET else today.month

        # If users submit a GET request to change the date: yyyy-mm
        if 'date' in self.request.GET: 
            date_params = [int(x) for x in self.request.GET['date'].split('-')]
            year = date_params[0]
            month = date_params[1]

        context['year'] = year
        context['month'] = month
        context['month_name'] = MONTHS_NAME[month-1]

        # Arrow Nav for monthly view
        # Context for view for the previous month
        context['prev_date_month'] = month - 1 if month != 1 else 12
        context['prev_date_year'] = year if month != 1 else year - 1

        # context for view for the next month
        context['next_date_month'] = month + 1 if month != 12 else 1
        context['next_date_year'] = year if month != 12 else year + 1


        # Pass in year range for the year select form
        context['year_range'] = [i for i in range(EARLIEST_YEAR, LATEST_YEAR)]

        # Here I create a dictionary associating month number with month name for the month select form
        month_numbers = [i for i in range(1, 13)] 
        context['month_range'] = dict(zip(MONTHS_NAME, month_numbers))

        context['limited_expenses'] = self.query_limited_expenses(year=year, month=month)
        context['month_expenditure'] = float(self.get_expenditure_by_time_range(year=year, month=month))

        monthlybudget = MonthlyBudget.objects.filter(user=self.request.user).filter(year=year).filter(month=month).first()
        if monthlybudget:
            context['monthlybudget'] = float(monthlybudget.budget)
            context['monthlybudget_object'] = monthlybudget
            context['surpass'] = True if monthlybudget.budget < context['month_expenditure'] else False
            #For progress bar
            context['progress_width'] = int(context['month_expenditure'] / context['monthlybudget'] * 100)

        # Pie chart stuff
        categories_data = self.get_categories_expenditure_by_time_range(year=year, month=month)
        categories_data_sum = sum(categories_data[1])
        if categories_data_sum == 0:
            context['labels'] = ['None']
            context['data'] = [1]
            context['background_colors'] = ['LightGray']
        else:
            context['labels'] = categories_data[0]
            context['data'] = categories_data[1]
            context['background_colors'] = sns.color_palette(cc.glasbey, n_colors=len(context['labels'])).as_hex() 

        context['expenditure_per_month'] = self.get_avg_expenditure_per_month()

        context['active_subscriptions'], context['was_active_subscriptions'] = self.get_subscriptions_by_time_range(year=year, month=month)
        
        # Bar graph stuff
        bar_graph = self.get_expenditure_by_month_per_day(year=year, month=month)
        context['bar_graph_labels'] = bar_graph[0]
        context['bar_graph_data'] = bar_graph[1]

        context['monthly_budget_indicator'] = self.get_monthly_budget_indicator(monthlybudget, float(self.get_expenditure_by_time_range(year=year, month=month)), month, year)

        return context
    
    """
    Returns the average expenditure per month for a user
    Approximated by multiplying average expenditure per day by average days per month

    Args:

    Returns:
        expenditure_per_month (float): average spending per month
    """
    def get_avg_expenditure_per_month(self):
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        if not earliest_expense:
            return None
        earliest_date = earliest_expense.date

        today = datetime.today().date()
        delta = today - earliest_date
        days_passed = delta.days + 1 # Add extra day for difference

        if days_passed < MIN_DAYS_PASSED:
            return None # Give message that returns WE NEED MORE DAYS

        expenditure_per_day = total / days_passed
        expenditure_per_month = float(expenditure_per_day) * AVG_DAYS_PER_MONTH
        return round(expenditure_per_month, 2)
    
    """
    Returns data (as a tuple) for the bar graph that displays spending per day for a month

    Args:
        year (int): year
        month (int): month
    
    Returns:
        tuple: day_list as an integer representation of the days of the month
                and day_expenses as the spending for each day of that month
    """
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



"""
View for summary statistics for a single day
"""
class DailyPanel(PanelView):
    model = Expense
    template_name = 'base/daily_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine Day (from GET params or assume Today Otherwise)
        today = datetime.today()
        year = today.year
        month = today.month
        day = today.day

        # If users submit a GET to change the date: yyyy-mm-dd
        if 'date' in self.request.GET: 
            date_params = [int(x) for x in self.request.GET['date'].split('-')]
            year = date_params[0]
            month = date_params[1]
            day = date_params[2]


        # Arrow nav buttons
        display_date = datetime(year, month, day)
        tomorrow = display_date + timedelta(days=1)
        yesterday = display_date - timedelta(days=1)
        context['tmr_date'] = str(tomorrow.year) + '-' + str(tomorrow.month) + '-' + str(tomorrow.day)
        context['yst_date'] = str(yesterday.year) + '-' + str(yesterday.month) + '-' + str(yesterday.day)



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

        # Calculate Percent Diff
        percent_diff = None if (not context['expenditure_per_day'] or context['expenditure_per_day'] == 0) else context['day_expenditure'] / context['expenditure_per_day']
        if percent_diff and percent_diff > 1:
            context['red_percent_diff'] = int((percent_diff - 1)*100)
        if percent_diff and percent_diff <= 1:
            context['green_percent_diff'] = int((1 - percent_diff)*100)

        # Subscriptions
        context['active_subscriptions'], context['was_active_subscriptions'] = self.get_subscriptions_by_time_range(year=year, month=month, day=day)

        categories_data = self.get_categories_expenditure_by_time_range(year=year, month=month, day=day)
        context['labels'] = categories_data[0]
        context['data'] = categories_data[1]

        # Budget Indicator code (May be implemented in a future date)
        # If not today, then don't pass in the indicator
        # monthlybudget = MonthlyBudget.objects.filter(user=self.request.user).filter(year=year).filter(month=month).first()
        # context['monthly_budget_indicator'] = self.get_monthly_budget_indicator(monthlybudget, float(self.get_expenditure_by_time_range(year=year, month=month)), month, year)
        # if year != today.year or month != today.month or day != today.day:
        #     context['monthly_budget_indicator'] = 'NO_INDICATOR'

        # yearlybudget = YearlyBudget.objects.filter(user=self.request.user).filter(year=year).first()
        # context['yearly_budget_indicator'] = self.get_yearly_budget_indicator(yearlybudget, float(self.get_expenditure_by_time_range(year=year)), year)
        # if year != today.year or month != today.month or day != today.day:
        #     context['yearly_budget_indicator'] = 'NO_INDICATOR'
        
        return context
    
    """
    Get the average spending per day for a user (not incluidng the present day) 

    Args:

    Returns:
        float: average expenditure per day 
    """
    def get_expenditure_per_day(self):
        today = datetime.today().date()
        total = self.get_total_expenditure()
        expenses = Expense.objects.filter(user=self.request.user)
        earliest_expense = None if not expenses else expenses.order_by('date')[0]

        # Subtract today's expenditure
        today_expenditure = self.get_expenditure_by_time_range(year=today.year, month=today.month, day=today.day)
        previous_expenditure = total - today_expenditure

        # If there is no previous expenditure, return None
        if previous_expenditure <= 0:
            return None

        if not earliest_expense:
            return None

        earliest_date = earliest_expense.date
        
        delta = today - earliest_date
        days_passed = delta.days # We don't add one anymore because we don't include current day
        return round(previous_expenditure / days_passed, 2)

    
    
    """
    Get the expenditure for current day

    Args: 
        year (Int), month (Int), day (Int)

    Returns:
        total (float): total expenditure for a specific day
    """
    def get_this_day_expenditure(self, year, month, day):
        expense_list = Expense.objects.all().filter(user=self.request.user).filter(date__year=year).filter(date__month=month).filter(date__day=day)
        total = 0
        for expense in expense_list:
            total += expense.cost
        return total
    
    """
    Get the expenditure for current month

    Args:

    Returns: 
        total (float): total spent in the current month
    """
    def get_this_month_expenditure(self):
        today = datetime.today()
        this_month = today.month
        this_year = today.year
        this_month_expenses = Expense.objects.all().filter(user=self.request.user).filter(date__year=this_year, date__month=this_month)
        total = 0
        for expense in this_month_expenses:
            total += expense.cost
        return total
    
    """
    Get the expenditure for current year

    Args:

    Returns:
        total (float): total spent in the current year
    """
    def get_this_year_expenditure(self):
        today = datetime.today()
        this_year = today.year
        this_year_expenses = Expense.objects.all().filter(user=self.request.user).filter(date__year=this_year)
        total = 0
        for expense in this_year_expenses:
            total += expense.cost
        return total
        

class OverviewPanel(PanelView):
    model = Expense
    template_name = 'base/overview_panel.html'

    



"""
View for Expense detail. Not being used currently.
"""
class ExpenseDetail(LoginRequiredMixin, DetailView):
    model = Expense
    context_object_name = 'expense'

    # Default is {expense}_detail.html
    template_name = 'base/expense.html'

"""
View for Creating an Expense
"""
class ExpenseCreate(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = CreateExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_create.html'

    # We want the form to automatically know which user to submit the data
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExpenseCreate, self).form_valid(form)
    
    # Save user information for the form to use
    def get_form_kwargs(self):
        kwargs = super(ExpenseCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Expense successfully created!')
        return self.request.session['previous_page']
    
    # Function to set initial value for date field in forms to today
    # The initial day changes depending on whether it is a call from daily, monthly, or yearly. 
    def get_initial(self):
        if 'day' in self.request.GET:
            return {
                'date': datetime(int(self.request.GET['year']), int(self.request.GET['month']), int(self.request.GET['day']))
            }
        
        if 'month' in self.request.GET:
            return {
                'date': datetime(int(self.request.GET['year']), int(self.request.GET['month']), 1)
            }
        
        if 'year' in self.request.GET:
            return {
                'date': datetime(int(self.request.GET['year']), 1, 1)
            }
        return {
            'date': date.today()
        }


"""
View for editing an expense. 
"""
class ExpenseUpdate(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = CreateExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_update.html'

    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Expense successfully edited!')
        return self.request.session['previous_page']
    
    # Need this or else will have an error, cause the form class uses the user
    def get_form_kwargs(self):
        kwargs = super(ExpenseUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

"""
View for deleting an expense
"""
class ExpenseDelete(LoginRequiredMixin, DeleteView):
    model = Expense
    context_object_name = 'expense'
    success_url = reverse_lazy('expense-list')
    template_name = 'base/expense_delete.html'

    # We want to save the previous url into the sessions so we can redirect back after POST success. 
    def get(self, request, *args, **kwargs):
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    # We change the success url depending on what is saved in the session (based on the get function)
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Expense successfully deleted!')
        return self.request.session['previous_page']

"""
View for listing all the user categories
"""
class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'base/category_list.html'
    context_object_name = 'categories'

    # Here we have to filter by user. 
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


"""
View for creating a new category
"""
class CategoryCreate(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CreateCategoryForm
    template_name = 'base/category_create.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CategoryCreate, self).form_valid(form)
    
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Category successfully created!')
        return reverse_lazy('category-list')
    
"""
View for editing a category
"""
class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CreateCategoryForm
    success_url = reverse_lazy('category-list')
    template_name = 'base/category_update.html'
    context_object_name = 'category'

    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Category successfully updated!')
        return reverse_lazy('category-list')

"""
View for deleting a category
"""
class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')
    template_name = 'base/category_delete.html'

    # Need to display all relevant expenses and subscriptions that are linked to the deleted category
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('pk')
        expenses_under_category = Expense.objects.filter(user=self.request.user).filter(category=category_id)
        context['expenses_under_category'] = expenses_under_category

        subscriptions_under_category = Subscription.objects.filter(user=self.request.user).filter(category=category_id)
        context['subscriptions_under_category'] = subscriptions_under_category
        return context
    
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Category successfully deleted!')
        return reverse_lazy('category-list')





