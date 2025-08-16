from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Subscription
from .forms import SubscriptionForm

@login_required
def subscription_list(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    
    # Filtering
    status = request.GET.get('status')
    if status:
        subscriptions = subscriptions.filter(status=status)
    
    # Pagination
    paginator = Paginator(subscriptions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_monthly_cost = subscriptions.filter(status='ACTIVE').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Upcoming renewals
    upcoming_renewals = subscriptions.filter(
        status='ACTIVE',
        next_billing_date__gte=timezone.now().date()
    ).order_by('next_billing_date')[:5]
    
    context = {
        'page_obj': page_obj,
        'total_monthly_cost': total_monthly_cost,
        'upcoming_renewals': upcoming_renewals,

        'statuses': Subscription.STATUS_CHOICES,
        'selected_status': status,

    }
    return render(request, 'subscriptions/subscription_list.html', context)

@login_required
def subscription_create(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            messages.success(request, 'Subscription created successfully!')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm()
    
    return render(request, 'subscriptions/subscription_form.html', {'form': form, 'title': 'Add New Subscription'})

@login_required
def subscription_update(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription updated successfully!')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm(instance=subscription)
    
    return render(request, 'subscriptions/subscription_form.html', {'form': form, 'title': 'Edit Subscription'})

@login_required
def subscription_delete(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        subscription.delete()
        messages.success(request, 'Subscription deleted successfully!')
        return redirect('subscriptions:subscription_list')
    
    return render(request, 'subscriptions/subscription_confirm_delete.html', {'subscription': subscription})

@login_required
def subscription_detail(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    return render(request, 'subscriptions/subscription_detail.html', {'subscription': subscription})
