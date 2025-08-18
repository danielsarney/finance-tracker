from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon name (e.g., 'fa-utensils')")
    color = models.CharField(max_length=7, default='#6c757d', help_text="Hex color code (e.g., #6c757d)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_icon_class(self):
        """Return the full FontAwesome class for the icon"""
        if self.icon:
            if self.icon.startswith('fas '):
                return self.icon
            elif self.icon.startswith('fa-'):
                return f"fas {self.icon}"
            else:
                return f"fas {self.icon}"
        return "fas fa-tag"  # Default icon
    
    def is_used(self):
        """Check if this category is being used by any financial items"""
        return (
            self.expense_set.exists() or
            self.income_set.exists() or
            self.subscription_set.exists() or
            self.worklog_set.exists()
        )
    
    def get_usage_count(self):
        """Get the total count of items using this category"""
        return (
            self.expense_set.count() +
            self.income_set.count() +
            self.subscription_set.count() +
            self.worklog_set.count()
        )
    
    def get_usage_breakdown(self):
        """Get a breakdown of how this category is being used"""
        return {
            'expenses': self.expense_set.count(),
            'income': self.income_set.count(),
            'subscriptions': self.subscription_set.count(),
            'work_logs': self.worklog_set.count(),
        }
