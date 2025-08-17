from django.db import models

class Category(models.Model):
    CATEGORY_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'), 
        ('subscription', 'Subscription'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='general')
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
