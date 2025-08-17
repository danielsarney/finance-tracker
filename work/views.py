from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import WorkLog
from .forms import WorkLogForm
from finance_tracker.view_mixins import create_crud_views

# Create CRUD views using the factory function
worklog_list, worklog_create, worklog_update, worklog_delete, worklog_detail = create_crud_views(
    model=WorkLog,
    form_class=WorkLogForm,
    template_name='work/worklog_form.html',
    list_url_name='work:worklog_list',
    success_message='Work log created successfully!'
)

@login_required
def worklog_list(request):
    """Custom worklog list view with additional context."""
    from finance_tracker.view_mixins import BaseCRUDMixin
    
    mixin = BaseCRUDMixin()
    mixin.model = WorkLog  # Set the model explicitly
    queryset = mixin.get_queryset(request)
    
    # Apply work-specific filters
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    # Apply date filters
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month:
        queryset = queryset.filter(work_date__month=month)
    if year:
        queryset = queryset.filter(work_date__year=int(year))
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add work-specific context
    total_hours = queryset.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    total_earnings = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_amount = queryset.filter(status='PENDING').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'total_hours': total_hours,
        'total_earnings': total_earnings,
        'pending_amount': pending_amount,
        'statuses': WorkLog.STATUS_CHOICES,
        'selected_status': status,
        'selected_month': month,
        'selected_year': year,
        'years': mixin.get_years_list(),
    }
    
    return render(request, 'work/worklog_list.html', context)
