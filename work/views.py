from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from .models import WorkLog
from .forms import WorkLogForm
from clients.models import Client
from finance_tracker.view_mixins import create_crud_views

# Create CRUD views using the factory function
worklog_list, worklog_create, worklog_update, worklog_delete, worklog_detail = (
    create_crud_views(
        model=WorkLog,
        form_class=WorkLogForm,
        template_name="work/worklog_form.html",
        list_url_name="work:worklog_list",
        success_message="Work log created successfully!",
    )
)


@login_required
def worklog_list(request):
    """Custom worklog list view with additional context."""
    from finance_tracker.view_mixins import BaseCRUDMixin

    mixin = BaseCRUDMixin()
    mixin.model = WorkLog  # Set the model explicitly
    queryset = mixin.get_queryset(request)

    # Apply work-specific filters
    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    # Apply client filter
    client_id = request.GET.get("client")
    if client_id:
        try:
            queryset = queryset.filter(company_client_id=client_id)
        except (ValueError, Client.DoesNotExist):
            pass

    # Apply date filters
    month = request.GET.get("month")
    year = request.GET.get("year")

    if month:
        queryset = queryset.filter(work_date__month=month)
    if year:
        queryset = queryset.filter(work_date__year=int(year))

    # Pagination
    from django.core.paginator import Paginator

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get all clients for the filter dropdown
    clients = Client.objects.filter(user=request.user).order_by("company_name")

    context = {
        "page_obj": page_obj,
        "statuses": WorkLog.STATUS_CHOICES,
        "clients": clients,
        "selected_status": status,
        "selected_month": month,
        "selected_year": year,
        "selected_client_id": client_id,
        "years": mixin.get_years_list(),
    }

    return render(request, "work/worklog_list.html", context)


@login_required
def worklog_create(request):
    """Custom create view to handle client filtering."""
    if request.method == "POST":
        form = WorkLogForm(request.POST)
        if form.is_valid():
            worklog = form.save(commit=False)
            worklog.user = request.user
            worklog.save()
            return redirect("work:worklog_list")
    else:
        form = WorkLogForm()
        form.set_user(request.user)

    # Get all clients with their hourly rates for JavaScript
    clients = Client.objects.filter(user=request.user).order_by("company_name")
    clients_data = {str(client.id): str(client.hourly_rate) for client in clients}

    return render(
        request,
        "work/worklog_form.html",
        {
            "form": form,
            "title": "Add Work Log",
            "clients_data": json.dumps(clients_data),
        },
    )


@login_required
def worklog_update(request, pk):
    """Custom update view to handle client filtering."""
    try:
        worklog = WorkLog.objects.get(pk=pk, user=request.user)
    except WorkLog.DoesNotExist:
        return redirect("work:worklog_list")

    if request.method == "POST":
        form = WorkLogForm(request.POST, instance=worklog)
        if form.is_valid():
            form.save()
            return redirect("work:worklog_detail", pk=worklog.pk)
    else:
        form = WorkLogForm(instance=worklog)
        form.set_user(request.user)

    # Get all clients with their hourly rates for JavaScript
    clients = Client.objects.filter(user=request.user).order_by("company_name")
    clients_data = {str(client.id): str(client.hourly_rate) for client in clients}

    return render(
        request,
        "work/worklog_form.html",
        {"form": form, "title": "Edit Work Log", "clients_data": clients_data},
    )
