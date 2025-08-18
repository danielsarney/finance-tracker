from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from .forms import SubscriptionForm
from finance_tracker.view_mixins import create_crud_views

def update_expired_billing_dates(subscriptions):
    """Update next billing dates for subscriptions that have passed their billing date."""
    today = timezone.now().date()
    updated_count = 0
    
    for subscription in subscriptions:
        if subscription.next_billing_date < today:
            # Calculate how many billing cycles have passed
            days_passed = (today - subscription.next_billing_date).days
            
            # Calculate the new next billing date
            new_next_date = subscription.next_billing_date
            while new_next_date < today:
                if subscription.billing_cycle == 'DAILY':
                    new_next_date += timedelta(days=1)
                elif subscription.billing_cycle == 'WEEKLY':
                    new_next_date += timedelta(weeks=1)
                elif subscription.billing_cycle == 'MONTHLY':
                    # Add months (approximate)
                    if new_next_date.month == 12:
                        new_next_date = new_next_date.replace(year=new_next_date.year + 1, month=1)
                    else:
                        new_next_date = new_next_date.replace(month=new_next_date.month + 1)
                elif subscription.billing_cycle == 'QUARTERLY':
                    # Add 3 months
                    for _ in range(3):
                        if new_next_date.month == 12:
                            new_next_date = new_next_date.replace(year=new_next_date.year + 1, month=1)
                        else:
                            new_next_date = new_next_date.replace(month=new_next_date.month + 1)
                elif subscription.billing_cycle == 'YEARLY':
                    new_next_date = new_next_date.replace(year=new_next_date.year + 1)
            
            # Update the subscription
            subscription.next_billing_date = new_next_date
            subscription.save()
            updated_count += 1
    
    return updated_count

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
    
    # Update expired billing dates
    updated_count = update_expired_billing_dates(filtered_queryset)
    
    # Refresh queryset after updates
    if updated_count > 0:
        queryset = mixin.get_queryset(request)
        context, filtered_queryset = mixin.get_list_context(request, queryset)
    
    # Add subscription-specific context
    total_monthly_cost = filtered_queryset.aggregate(Sum('amount'))['amount__sum'] or 0
    upcoming_renewals = filtered_queryset.filter(
        next_billing_date__gte=timezone.now().date()
    ).order_by('next_billing_date')[:5]
    categories = mixin.get_categories()
    
    context.update({
        'total_monthly_cost': total_monthly_cost,
        'upcoming_renewals': upcoming_renewals,
        'categories': categories,
        'updated_subscriptions': updated_count,
    })
    
    return render(request, 'subscriptions/subscription_list.html', context)
