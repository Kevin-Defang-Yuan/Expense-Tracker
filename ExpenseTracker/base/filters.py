import django_filters
from .models import Expense

class ExpenseFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains')
    o = django_filters.OrderingFilter(
        fields=(
            ('cost', 'cost'),
        )
    )
    class Meta:
        model = Expense
        fields = {
            'cost': ['lt', 'gt'],
            'date': ['exact', 'lt', 'gt'],
        }