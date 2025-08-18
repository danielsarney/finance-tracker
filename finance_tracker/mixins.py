from django.db import models
from django.contrib.auth.models import User
from .utils import get_years_list

class BaseFinancialModel(models.Model):
    """
    Base mixin for financial models with common fields and methods.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_set')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey('categories.Category', on_delete=models.PROTECT, related_name='%(class)s_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        # Try to get a description-like field, fallback to model name
        if hasattr(self, 'description'):
            display_name = self.description
        elif hasattr(self, 'name'):
            display_name = self.name
        elif hasattr(self, 'payee'):
            display_name = self.payee or "Unknown"
        elif hasattr(self, 'payer'):
            display_name = self.payer or "Unknown"
        else:
            display_name = self.__class__.__name__
        
        return f"{display_name} - £{self.amount} ({self.date})"

class BaseListViewMixin:
    """
    Mixin for common list view functionality.
    """
    def get_filtered_queryset(self, queryset, request):
        """Apply common filters to queryset."""
        month = request.GET.get('month')
        year = request.GET.get('year')
        category_id = request.GET.get('category')
        
        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=int(year))
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
    
    def get_years_list(self):
        """Generate years list for filtering."""
        return get_years_list()
    
    def get_categories(self):
        """Get all categories for filtering."""
        from categories.models import Category
        return Category.objects.all()
