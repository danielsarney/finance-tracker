from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm
from finance_tracker.view_mixins import create_crud_views

# Create CRUD views using the factory function
expense_list, expense_create, expense_update, expense_delete, expense_detail = create_crud_views(
    model=Expense,
    form_class=ExpenseForm,
    template_name='expenses/expense_form.html',
    list_url_name='expenses:expense_list',
    success_message='Expense created successfully!'
)

@login_required
def expense_list(request):
    """Custom expense list view with additional context."""
    from finance_tracker.view_mixins import BaseCRUDMixin
    
    mixin = BaseCRUDMixin()
    mixin.model = Expense  # Set the model explicitly
    queryset = mixin.get_queryset(request)
    context, filtered_queryset = mixin.get_list_context(request, queryset)
    
    # Add expense-specific context
    total_expenses = filtered_queryset.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = mixin.get_categories('expense')
    
    context.update({
        'total_expenses': total_expenses,
        'categories': categories,
    })
    
    return render(request, 'expenses/expense_list.html', context)
