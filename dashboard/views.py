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
    # Get selected month and year from request, default to current month/year
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    current_date = timezone.now().date()
    
    # Initialize base querysets
    expenses_base = Expense.objects.filter(user=request.user)
    income_base = Income.objects.filter(user=request.user)
    work_base = WorkLog.objects.filter(user=request.user)
    
    # Apply filters based on selection
    if selected_month and selected_year:
        # Specific month and year
        month = int(selected_month)
        year = int(selected_year)
        display_month = month
        display_year = year
        
        month_expenses = expenses_base.filter(date__month=month, date__year=year)
        month_income = income_base.filter(date__month=month, date__year=year)
        month_work = work_base.filter(work_date__month=month, work_date__year=year)
        
    elif selected_year and not selected_month:
        # Only year selected - show all months for that year
        year = int(selected_year)
        display_month = None
        display_year = year
        
        month_expenses = expenses_base.filter(date__year=year)
        month_income = income_base.filter(date__year=year)
        month_work = work_base.filter(work_date__year=year)
        
    elif selected_month and not selected_year:
        # Only month selected - show that month for all years
        month = int(selected_month)
        display_month = month
        display_year = None
        
        month_expenses = expenses_base.filter(date__month=month)
        month_income = income_base.filter(date__month=month)
        month_work = work_base.filter(work_date__month=month)
        
    else:
        # No filters - use current month/year
        month = current_date.month
        year = current_date.year
        display_month = month
        display_year = year
        
        month_expenses = expenses_base.filter(date__month=month, date__year=year)
        month_income = income_base.filter(date__month=month, date__year=year)
        month_work = work_base.filter(work_date__month=month, work_date__year=year)
    
    # Calculate totals
    total_expenses = month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = month_income.aggregate(Sum('amount'))['amount__sum'] or 0
    net_income = total_income - total_expenses
    
    # Active subscriptions (always show current total)
    active_subscriptions = Subscription.objects.filter(
        user=request.user
    )
    total_subscription_cost = active_subscriptions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Work logs totals
    total_work_hours = month_work.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    total_work_earnings = month_work.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent transactions (always show recent, not filtered by month)
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    recent_income = Income.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Upcoming subscription renewals (always show upcoming)
    upcoming_renewals = active_subscriptions.filter(
        next_billing_date__gte=current_date
    ).order_by('next_billing_date')[:5]
    
    # Pending work payments (always show pending)
    pending_work = WorkLog.objects.filter(
        user=request.user,
        status='PENDING'
    ).order_by('-work_date')[:5]
    
    # Generate years list for the filter
    years = list(range(2020, 2081))
    
    # Month names for display
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    context = {
        'current_month': display_month,
        'current_year': display_year,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_names': month_names,
        'years': years,
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
