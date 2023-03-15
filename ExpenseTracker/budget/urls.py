from django .urls import path
from .views import YearlyBudgetList, YearlyBudgetCreate, YearlyBudgetUpdate, YearlyBudgetDelete
from .views import MonthlyBudgetList, MonthlyBudgetCreate, MonthlyBudgetUpdate, MonthlyBudgetDelete



urlpatterns = [
    # List of yearly budgets
    path('yearlybudget-list', YearlyBudgetList.as_view(), name="yearlybudget-list"),

    # Create a yearly budget
    path('yearlybudget-create', YearlyBudgetCreate.as_view(), name="yearlybudget-create"),

    # Edit a yearly budget
    path('yearlybudget-update/<int:pk>/', YearlyBudgetUpdate.as_view(), name="yearlybudget-update"),

    # Delete a yearly budget
    path('yearlybudget-delete/<int:pk>/', YearlyBudgetDelete.as_view(), name="yearlybudget-delete"),

    # List of monthly budgets
    path('monthlybudget-list', MonthlyBudgetList.as_view(), name="monthlybudget-list"),

    # Create a monthly budget
    path('monthlybudget-create', MonthlyBudgetCreate.as_view(), name="monthlybudget-create"),

    # Edit a monthly budget
    path('monthlybudget-update/<int:pk>/', MonthlyBudgetUpdate.as_view(), name="monthlybudget-update"),

    # Delete a monthly budget
    path('monthlybudget-delete/<int:pk>/', MonthlyBudgetDelete.as_view(), name="monthlybudget-delete"),

]