from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from finance_tracker.mixins import BaseListViewMixin
from .models import MileageLog
from .forms import MileageLogForm
from datetime import date


class MileageLogListView(LoginRequiredMixin, BaseListViewMixin, ListView):
    """List view for mileage logs with filtering."""
    model = MileageLog
    template_name = 'mileage/mileage_list.html'
    context_object_name = 'mileage_logs'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter mileage logs for the current user."""
        queryset = MileageLog.objects.filter(user=self.request.user)
        
        # Apply filters
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        client_id = self.request.GET.get('client')
        
        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=int(year))
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter values and summary data to context."""
        context = super().get_context_data(**kwargs)
        
        # Add filter values for template
        context['selected_year'] = self.request.GET.get('year')
        context['years'] = self.get_years_list()
        
        # Add clients for filter dropdown
        from clients.models import Client
        context['clients'] = Client.objects.filter(user=self.request.user)
        
        # Add summary data
        queryset = self.get_queryset()
        context['total_miles'] = queryset.aggregate(Sum('miles'))['miles__sum'] or 0
        context['total_claim'] = queryset.aggregate(Sum('total_claim'))['total_claim__sum'] or 0
        
        # Add current tax year summary
        current_year = date.today().year
        context['tax_year_summary'] = MileageLog.get_tax_year_summary(self.request.user, current_year)
        
        return context


class MileageLogDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single mileage log."""
    model = MileageLog
    template_name = 'mileage/mileage_detail.html'
    context_object_name = 'mileage_log'
    
    def get_queryset(self):
        """Only show mileage logs belonging to the current user."""
        return MileageLog.objects.filter(user=self.request.user)


class MileageLogCreateView(LoginRequiredMixin, CreateView):
    """Create view for new mileage logs."""
    model = MileageLog
    form_class = MileageLogForm
    template_name = 'mileage/mileage_form.html'
    success_url = reverse_lazy('mileage:mileage_list')
    
    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add client data for JavaScript auto-population."""
        context = super().get_context_data(**kwargs)
        
        # Get client data for JavaScript
        from clients.models import Client
        import json
        clients = Client.objects.filter(user=self.request.user)
        clients_data = {}
        for client in clients:
            clients_data[str(client.id)] = client.full_address
        
        context['clients_data'] = json.dumps(clients_data)
        return context
    
    def form_valid(self, form):
        """Set user."""
        form.instance.user = self.request.user
        return super().form_valid(form)


class MileageLogUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for existing mileage logs."""
    model = MileageLog
    form_class = MileageLogForm
    template_name = 'mileage/mileage_form.html'
    success_url = reverse_lazy('mileage:mileage_list')
    
    def get_queryset(self):
        """Only allow editing mileage logs belonging to the current user."""
        return MileageLog.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add client data for JavaScript auto-population."""
        context = super().get_context_data(**kwargs)
        
        # Get client data for JavaScript
        from clients.models import Client
        import json
        clients = Client.objects.filter(user=self.request.user)
        clients_data = {}
        for client in clients:
            clients_data[str(client.id)] = client.full_address
        
        context['clients_data'] = json.dumps(clients_data)
        return context
    
    def form_valid(self, form):
        """Recalculate claim."""
        # Recalculate the claim
        form.instance.calculate_claim()
        response = super().form_valid(form)
        return response


class MileageLogDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for mileage logs."""
    model = MileageLog
    template_name = 'mileage/mileage_confirm_delete.html'
    success_url = reverse_lazy('mileage:mileage_list')
    context_object_name = 'mileage_log'
    
    def get_queryset(self):
        """Only allow deleting mileage logs belonging to the current user."""
        return MileageLog.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Delete mileage log."""
        return super().delete(request, *args, **kwargs)


@login_required
def mileage_summary(request):
    """View to show mileage summary and tax year information."""
    current_year = date.today().year
    
    # Get summary for current tax year
    tax_year_summary = MileageLog.get_tax_year_summary(request.user, current_year)
    
    # Get summary for previous tax year for comparison
    prev_tax_year_summary = MileageLog.get_tax_year_summary(request.user, current_year - 1)
    
    # Get monthly breakdown for current year
    monthly_data = []
    for month in range(1, 13):
        month_logs = MileageLog.objects.filter(
            user=request.user,
            date__year=current_year,
            date__month=month
        )
        total_miles = month_logs.aggregate(Sum('miles'))['miles__sum'] or 0
        total_claim = month_logs.aggregate(Sum('total_claim'))['total_claim__sum'] or 0
        
        monthly_data.append({
            'month': month,
            'month_name': date(current_year, month, 1).strftime('%B'),
            'total_miles': total_miles,
            'total_claim': total_claim,
            'journeys': month_logs.count()
        })
    
    context = {
        'tax_year_summary': tax_year_summary,
        'prev_tax_year_summary': prev_tax_year_summary,
        'monthly_data': monthly_data,
        'current_year': current_year,
    }
    
    return render(request, 'mileage/mileage_summary.html', context)


@login_required
@require_http_methods(["GET"])
def calculate_mileage_claim(request):
    """API endpoint to calculate mileage claim for given miles."""
    miles = request.GET.get('miles')
    user = request.user
    
    if not miles:
        return JsonResponse({'error': 'Miles parameter required'}, status=400)
    
    try:
        miles = float(miles)
        if miles <= 0:
            return JsonResponse({'error': 'Miles must be greater than 0'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid miles value'}, status=400)
    
    # Create a temporary MileageLog to calculate the claim
    temp_log = MileageLog(
        user=user,
        date=date.today(),
        miles=miles,
        start_location='',
        end_location='',
        purpose=''
    )
    temp_log.calculate_claim()
    
    return JsonResponse({
        'miles': miles,
        'rate_per_mile': float(temp_log.rate_per_mile),
        'total_claim': float(temp_log.total_claim),
        'effective_rate': float(temp_log.effective_rate_per_mile)
    })