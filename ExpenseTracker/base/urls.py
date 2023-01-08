from django .urls import path
from .views import Dashboard, ExpenseDetail, ExpenseCreate, ExpenseUpdate, ExpenseDelete
from .views import DailyPanel, MonthlyPanel, YearlyPanel
from .views import ExpenseList
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # path('login/', CustomLoginView.as_view(), name='login'),

    # # Instead of customzing our logout view, we just use it directly here after importing it
    # # Next page dicates that once we log out, the user is sent to the specified location
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('register/', RegisterPage.as_view(), name='register'),
    # # as_view is used to determine if the request is get or post
    path('', DailyPanel.as_view(), name="default"),
    path('daily-panel/', DailyPanel.as_view(), name="daily-panel"),
    path('monthly-panel/', MonthlyPanel.as_view(), name="monthly-panel"),
    path('yearly-panel/', YearlyPanel.as_view(), name="yearly-panel"),
    path('expense-list/', ExpenseList.as_view(), name="expense-list"),
    path('expense/<int:pk>/', ExpenseDetail.as_view(), name='expense'),
    path('fixed-expense-create/', ExpenseCreate.as_view(), name='fixed-expense-create'),
    path('expense-update/<int:pk>/', ExpenseUpdate.as_view(), name='expense-update'),
    path('expense-delete/<int:pk>/', ExpenseDelete.as_view(), name='expense-delete'),
]