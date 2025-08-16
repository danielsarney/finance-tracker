from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import WorkLog
from .forms import WorkLogForm

@login_required
def worklog_list(request):
    worklogs = WorkLog.objects.filter(user=request.user)
    
    # Filtering
    status = request.GET.get('status')
    if status:
        worklogs = worklogs.filter(status=status)
    
    # Date filtering
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        worklogs = worklogs.filter(work_date__month=month, work_date__year=year)
    
    # Pagination
    paginator = Paginator(worklogs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_hours = worklogs.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    total_earnings = worklogs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_amount = worklogs.filter(status='PENDING').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Generate years list for the filter
    current_year = timezone.now().year
    years = list(range(current_year - 5, current_year + 2))
    
    context = {
        'page_obj': page_obj,
        'total_hours': total_hours,
        'total_earnings': total_earnings,
        'pending_amount': pending_amount,
        'statuses': WorkLog.STATUS_CHOICES,
        'selected_status': status,
        'selected_month': month,
        'selected_year': year,
        'years': years,
    }
    return render(request, 'work/worklog_list.html', context)

@login_required
def worklog_create(request):
    if request.method == 'POST':
        form = WorkLogForm(request.POST)
        if form.is_valid():
            worklog = form.save(commit=False)
            worklog.user = request.user
            worklog.save()
            messages.success(request, 'Work log created successfully!')
            return redirect('work:worklog_list')
    else:
        form = WorkLogForm()
    
    return render(request, 'work/worklog_form.html', {'form': form, 'title': 'Add New Work Log'})

@login_required
def worklog_update(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WorkLogForm(request.POST, instance=worklog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work log updated successfully!')
            return redirect('work:worklog_list')
    else:
        form = WorkLogForm(instance=worklog)
    
    return render(request, 'work/worklog_form.html', {'form': form, 'title': 'Edit Work Log'})

@login_required
def worklog_delete(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk, user=request.user)
    if request.method == 'POST':
        worklog.delete()
        messages.success(request, 'Work log deleted successfully!')
        return redirect('work:worklog_list')
    
    return render(request, 'work/worklog_confirm_delete.html', {'worklog': worklog})

@login_required
def worklog_detail(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk, user=request.user)
    return render(request, 'work/worklog_detail.html', {'worklog': worklog})
