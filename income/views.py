from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income
from .forms import IncomeForm
from finance_tracker.view_mixins import create_crud_views

# Create CRUD views using the factory function
income_list, income_create, income_update, income_delete, income_detail = create_crud_views(
    model=Income,
    form_class=IncomeForm,
    template_name='income/income_form.html',
    list_url_name='income:income_list',
    success_message='Income entry created successfully!'
)

@login_required
def income_list(request):
    """Custom income list view with additional context."""
    from finance_tracker.view_mixins import BaseCRUDMixin
    
    mixin = BaseCRUDMixin()
    mixin.model = Income  # Set the model explicitly
    queryset = mixin.get_queryset(request)
    context, filtered_queryset = mixin.get_list_context(request, queryset)
    
    # Add income-specific context
    total_income = filtered_queryset.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = mixin.get_categories('income')
    
    context.update({
        'total_income': total_income,
        'categories': categories,
    })
    
    return render(request, 'income/income_list.html', context)
