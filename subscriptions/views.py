from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Subscription
from .forms import SubscriptionForm
from finance_tracker.view_mixins import create_crud_views

# Create CRUD views using the factory function
subscription_list, subscription_create, subscription_update, subscription_delete, subscription_detail = create_crud_views(
    model=Subscription,
    form_class=SubscriptionForm,
    template_name='subscriptions/subscription_form.html',
    list_url_name='subscriptions:subscription_list',
    success_message='Subscription created successfully!'
)

@login_required
def subscription_list(request):
    """Custom subscription list view with additional context."""
    from finance_tracker.view_mixins import BaseCRUDMixin
    
    mixin = BaseCRUDMixin()
    mixin.model = Subscription  # Set the model explicitly
    queryset = mixin.get_queryset(request)
    context, filtered_queryset = mixin.get_list_context(request, queryset)
    
    # Add subscription-specific context
    total_monthly_cost = filtered_queryset.aggregate(Sum('amount'))['amount__sum'] or 0
    upcoming_renewals = filtered_queryset.filter(
        next_billing_date__gte=timezone.now().date()
    ).order_by('next_billing_date')[:5]
    categories = mixin.get_categories('subscription')
    
    context.update({
        'total_monthly_cost': total_monthly_cost,
        'upcoming_renewals': upcoming_renewals,
        'categories': categories,
    })
    
    return render(request, 'subscriptions/subscription_list.html', context)
