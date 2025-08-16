from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from expenses.models import Expense
from income.models import Income
from subscriptions.models import Subscription
from work.models import WorkLog

@login_required
def dashboard(request):
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get current month data
    current_month_expenses = Expense.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    )
    
    current_month_income = Income.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    )
    
    # Calculate totals
    total_expenses = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = current_month_income.aggregate(Sum('amount'))['amount__sum'] or 0
    net_income = total_income - total_expenses
    
    # Active subscriptions
    active_subscriptions = Subscription.objects.filter(
        user=request.user,
        status='ACTIVE'
    )
    total_subscription_cost = active_subscriptions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Work logs
    current_month_work = WorkLog.objects.filter(
        user=request.user,
        work_date__month=current_month,
        work_date__year=current_year
    )
    total_work_hours = current_month_work.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    total_work_earnings = current_month_work.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent transactions
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    recent_income = Income.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Upcoming subscription renewals
    upcoming_renewals = active_subscriptions.filter(
        next_billing_date__gte=current_date
    ).order_by('next_billing_date')[:5]
    
    # Pending work payments
    pending_work = WorkLog.objects.filter(
        user=request.user,
        status='PENDING'
    ).order_by('-work_date')[:5]
    

    
    context = {
        'current_month': current_month,
        'current_year': current_year,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_income': net_income,
        'total_subscription_cost': total_subscription_cost,
        'total_work_hours': total_work_hours,
        'total_work_earnings': total_work_earnings,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'upcoming_renewals': upcoming_renewals,
        'pending_work': pending_work,

        'active_subscriptions': active_subscriptions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
