from django .urls import path
from .views import Dashboard, ExpenseDetail, FixedExpenseCreate, ExpenseUpdate, ExpenseDelete, CustomLoginView, RegisterPage
from .views import TodayPanel
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),

    # Instead of customzing our logout view, we just use it directly here after importing it
    # Next page dicates that once we log out, the user is sent to the specified location
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    # as_view is used to determine if the request is get or post
    path('', TodayPanel.as_view(), name="default"),
    path('today-panel', TodayPanel.as_view(), name="today-panel"),
    path('expense/<int:pk>/', ExpenseDetail.as_view(), name='expense'),
    path('fixed-expense-create/', FixedExpenseCreate.as_view(), name='fixed-expense-create'),
    path('expense-update/<int:pk>/', ExpenseUpdate.as_view(), name='expense-update'),
    path('expense-delete/<int:pk>/', ExpenseDelete.as_view(), name='expense-delete'),

    

]