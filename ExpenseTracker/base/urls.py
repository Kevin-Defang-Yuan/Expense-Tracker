from django .urls import path, include
from .views import ExpenseDetail, ExpenseCreate, ExpenseUpdate, ExpenseDelete
from .views import DailyPanel, MonthlyPanel, YearlyPanel
from .views import ExpenseList, CategoryList, CategoryCreate, CategoryUpdate, CategoryDelete

urlpatterns = [
    # Default path directs to the dailyview of current day
    path('', DailyPanel.as_view(), name="default"),

    # Daily panel
    path('daily-panel/', DailyPanel.as_view(), name="daily-panel"),

    # Monthly panel
    path('monthly-panel/', MonthlyPanel.as_view(), name="monthly-panel"),

    # Yearly panel
    path('yearly-panel/', YearlyPanel.as_view(), name="yearly-panel"),

    # List of expenses
    path('expense-list/', ExpenseList.as_view(), name="expense-list"),

    # List of categories
    path('category-list/', CategoryList.as_view(), name="category-list"),

    # View of a particular expense based on the id of expense
    path('expense/<int:pk>/', ExpenseDetail.as_view(), name='expense'),

    # Create an expense
    path('expense-create/', ExpenseCreate.as_view(), name='expense-create'),

    # Edit a particular expense
    path('expense-update/<int:pk>/', ExpenseUpdate.as_view(), name='expense-update'),

    # Delete a particular expense
    path('expense-delete/<int:pk>/', ExpenseDelete.as_view(), name='expense-delete'),

    # Create a category
    path('category-create/', CategoryCreate.as_view(), name='category-create'),

    # Edit a category
    path('category-update/<int:pk>/', CategoryUpdate.as_view(), name='category-update'),

    # Delete a category
    path('category-delete/<int:pk>/', CategoryDelete.as_view(), name='category-delete'),

    # Include budget views
    path('', include('budget.urls')),

    # Include subscription views
    path('', include('subscription.urls'))

]