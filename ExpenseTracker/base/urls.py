from django .urls import path
from .views import Dashboard, ExpenseDetail, ExpenseCreate, ExpenseUpdate, ExpenseDelete


urlpatterns = [
    # as_view is used to determine if the request is get or post
    path('', Dashboard.as_view(), name="dashboard"),
    path('expense/<int:pk>/', ExpenseDetail.as_view(), name='expense'),
    path('expense-create/', ExpenseCreate.as_view(), name='expense-create'),
    path('expense-update/<int:pk>/', ExpenseUpdate.as_view(), name='expense-update'),
    path('expense-delete/<int:pk>/', ExpenseDelete.as_view(), name='expense-delete')

]