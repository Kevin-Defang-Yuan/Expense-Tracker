from django .urls import path
from .views import YearlyBudgetList, YearlyBudgetCreate, YearlyBudgetUpdate, YearlyBudgetDelete
from .views import MonthlyBudgetList, MonthlyBudgetCreate, MonthlyBudgetUpdate, MonthlyBudgetDelete



urlpatterns = [
    path('yearlybudget-list', YearlyBudgetList.as_view(), name="yearlybudget-list"),
    path('yearlybudget-create', YearlyBudgetCreate.as_view(), name="yearlybudget-create"),
    path('yearlybudget-update/<int:pk>/', YearlyBudgetUpdate.as_view(), name="yearlybudget-update"),
    path('yearlybudget-delete/<int:pk>/', YearlyBudgetDelete.as_view(), name="yearlybudget-delete"),

    path('monthlybudget-list', MonthlyBudgetList.as_view(), name="monthlybudget-list"),
    path('monthlybudget-create', MonthlyBudgetCreate.as_view(), name="monthlybudget-create"),
    path('monthlybudget-update/<int:pk>/', MonthlyBudgetUpdate.as_view(), name="monthlybudget-update"),
    path('monthlybudget-delete/<int:pk>/', MonthlyBudgetDelete.as_view(), name="monthlybudget-delete"),

]