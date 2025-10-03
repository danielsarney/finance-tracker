from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import json
from .models import WorkLog, ClockSession
from .forms import WorkLogForm, ClockInForm
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


@login_required
def clock_dashboard(request):
    """Main clock in/out dashboard"""
    # Get active clock session for current user
    active_session = ClockSession.objects.filter(
        user=request.user, is_active=True
    ).first()

    # Get recent clock sessions
    recent_sessions = ClockSession.objects.filter(user=request.user).order_by(
        "-clock_in_time"
    )[:10]

    # Get all clients for clock in form
    clients = Client.objects.filter(user=request.user).order_by("company_name")

    context = {
        "active_session": active_session,
        "recent_sessions": recent_sessions,
        "clients": clients,
    }

    return render(request, "work/clock_dashboard.html", context)


@login_required
def clock_in(request):
    """Clock in for a client"""
    if request.method == "POST":
        form = ClockInForm(request.POST, user=request.user)
        if form.is_valid():
            client = form.cleaned_data["client"]

            # Check if user already has an active session
            active_session = ClockSession.objects.filter(
                user=request.user, is_active=True
            ).first()

            if active_session:
                messages.warning(
                    request,
                    f"You are already clocked in for {active_session.client.company_name}. Please clock out first.",
                )
                return redirect("work:clock_dashboard")

            # Create new clock session
            clock_session = ClockSession.objects.create(
                user=request.user, client=client, clock_in_time=timezone.now()
            )

            messages.success(
                request,
                f"Clocked in for {client.company_name} at {clock_session.clock_in_time.strftime('%H:%M')}",
            )
            return redirect("work:clock_dashboard")
    else:
        form = ClockInForm(user=request.user)

    return render(request, "work/clock_in.html", {"form": form})


@login_required
def clock_out(request, session_id):
    """Clock out from a session"""
    session = get_object_or_404(ClockSession, id=session_id, user=request.user)

    if not session.is_active:
        messages.error(request, "This session is already completed.")
        return redirect("work:clock_dashboard")

    # Clock out and calculate hours
    hours_worked = session.clock_out()

    # Create or update work log
    work_date = session.clock_in_time.date()
    work_log, is_new = WorkLog.create_or_update_from_clock_session(
        user=request.user,
        client=session.client,
        work_date=work_date,
        hours_to_add=hours_worked,
    )

    action = "created" if is_new else "updated"
    messages.success(
        request,
        f"Clocked out! Work log {action} with {hours_worked} hour(s) for {session.client.company_name}.",
    )

    return redirect("work:clock_dashboard")


@login_required
def clock_out_ajax(request, session_id):
    """AJAX endpoint for clocking out"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        session = ClockSession.objects.get(id=session_id, user=request.user)

        if not session.is_active:
            return JsonResponse({"error": "Session already completed"}, status=400)

        # Clock out and calculate hours
        hours_worked = session.clock_out()

        # Create or update work log
        work_date = session.clock_in_time.date()
        work_log, is_new = WorkLog.create_or_update_from_clock_session(
            user=request.user,
            client=session.client,
            work_date=work_date,
            hours_to_add=hours_worked,
        )

        return JsonResponse(
            {
                "success": True,
                "hours_worked": hours_worked,
                "client_name": session.client.company_name,
                "work_log_action": "created" if is_new else "updated",
                "clock_out_time": session.clock_out_time.strftime("%H:%M"),
                "duration_display": session.get_duration_display(),
            }
        )

    except ClockSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def clock_session_delete(request, session_id):
    """Delete a clock session"""
    session = get_object_or_404(ClockSession, id=session_id, user=request.user)

    if request.method == "POST":
        # Store session info for success message
        client_name = session.client.company_name
        session.delete()

        messages.success(
            request, f"Clock session for {client_name} has been deleted successfully."
        )
        return redirect("work:clock_dashboard")

    # If GET request, show confirmation
    context = {
        "session": session,
    }
    return render(request, "work/clock_session_confirm_delete.html", context)
