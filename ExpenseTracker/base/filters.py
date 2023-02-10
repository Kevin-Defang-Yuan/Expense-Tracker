import django_filters
from .models import Expense, Category
from django.forms import TextInput

# 
def categories(request):
    return Category.objects.filter(user=request.user)

class ExpenseFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains', label="Description Contains:")
    category = django_filters.ModelChoiceFilter(queryset=categories, label="Category:")
    o = django_filters.OrderingFilter(
        fields=(
            ('cost', 'cost'),
            ('date', 'date')
        ),
        label="Ordering"
    )
    class Meta:
        model = Expense
        fields = ['category']
        widgets = {
            'description': TextInput(attrs={'class': 'form-control'})
        }
        
        # fields = {
        #     'cost': ['lt', 'gt'],
        #     'date': ['exact', 'lt', 'gt'],
        #     'category': [],
        # }
    
    # Code that filters by request object (so categories only include user-specific)
    @property
    def qs(self):
        parent = super().qs
        user = getattr(self.request, 'user', None)
        print(user)
        return parent.filter(user=user)