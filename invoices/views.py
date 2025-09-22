from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import date

from .models import Invoice, InvoiceLineItem
from .forms import InvoiceForm
from clients.models import Client
from work.models import WorkLog

@login_required
def invoice_list(request):
    """Display list of all invoices for the current user with filtering"""
    # Get base queryset
    invoices = Invoice.objects.filter(user=request.user).order_by('-issue_date')
    
    # Apply filters
    client_id = request.GET.get('client')
    status = request.GET.get('status')
    invoice_number = request.GET.get('invoice_number')
    
    if client_id:
        invoices = invoices.filter(client_id=client_id)
    if invoice_number:
        invoices = invoices.filter(invoice_number=invoice_number)
    if status:
        if status == 'paid':
            invoices = invoices.filter(line_items__work_log__status='PAID').distinct()
        elif status == 'overdue':
            from django.utils import timezone
            invoices = invoices.filter(
                due_date__lt=timezone.now().date(),
                line_items__work_log__status__in=['PENDING', 'INVOICED']
            ).distinct()
        elif status == 'outstanding':
            invoices = invoices.filter(
                line_items__work_log__status__in=['PENDING', 'INVOICED']
            ).exclude(
                line_items__work_log__status='PAID'
            ).distinct()
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    clients = Client.objects.filter(user=request.user).order_by('company_name')
    all_invoices = Invoice.objects.filter(user=request.user).order_by('-invoice_number')
    
    context = {
        'page_obj': page_obj,
        'invoices': page_obj,  # For backward compatibility
        'clients': clients,
        'all_invoices': all_invoices,
        'selected_client': client_id,
        'selected_status': status,
        'selected_invoice_number': invoice_number,
    }
    return render(request, 'invoices/invoice_list.html', context)

@login_required
def invoice_create(request):
    """Create a new invoice with multiple work logs"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        if form.is_valid():
            # Get selected work log IDs from form first
            work_log_ids = request.POST.getlist('work_logs')
            
            if not work_log_ids:
                messages.error(request, 'Please select at least one work log to invoice.')
                return redirect('invoices:invoice_create')
            
            # Create invoice but don't save yet
            invoice = form.save(commit=False)
            invoice.user = request.user
            
            # Store sender details at creation time (locked)
            try:
                user_profile = request.user.profile
                invoice.sender_name = request.user.get_full_name() or request.user.username
                invoice.sender_address_line_1 = user_profile.address_line_1
                invoice.sender_address_line_2 = user_profile.address_line_2 or ""
                invoice.sender_town = user_profile.town
                invoice.sender_post_code = user_profile.post_code
                invoice.sender_phone = user_profile.phone
                invoice.sender_email = user_profile.email
                
                # Store bank details at creation time (locked)
                invoice.bank_name = user_profile.bank_name
                invoice.account_name = user_profile.account_name
                invoice.account_number = user_profile.account_number
                invoice.sort_code = user_profile.sort_code
            except:
                # Fallback if profile doesn't exist
                invoice.sender_name = request.user.get_full_name() or request.user.username
                invoice.sender_address_line_1 = "Address not set"
                invoice.sender_address_line_2 = ""
                invoice.sender_town = "Town not set"
                invoice.sender_post_code = "Postcode not set"
                invoice.sender_phone = "Phone not set"
                invoice.sender_email = request.user.email
                invoice.bank_name = "Bank not set"
                invoice.account_name = "Account not set"
                invoice.account_number = "Account number not set"
                invoice.sort_code = "Sort code not set"
            
            # Now save the invoice (this will generate the invoice number)
            invoice.save()
            
            # Link selected work logs to invoice
            for work_log_id in work_log_ids:
                try:
                    work_log = WorkLog.objects.get(id=work_log_id, user=request.user)
                    
                    # Create line item linking work log to invoice
                    InvoiceLineItem.objects.create(
                        invoice=invoice,
                        work_log=work_log
                    )
                    
                    # Update work log status and invoice details
                    work_log.status = 'INVOICED'
                    work_log.invoice_date = invoice.issue_date
                    work_log.invoice_number = invoice.invoice_number
                    work_log.save()
                    
                except WorkLog.DoesNotExist:
                    messages.warning(request, f'Work log {work_log_id} not found.')
                    continue
            
            messages.success(request, f'Invoice {invoice.invoice_number} created with {len(work_log_ids)} work logs!')
            return redirect('invoices:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(user=request.user)
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'title': 'Create New Invoice',
        'submit_text': 'Generate Invoice'
    })

@login_required
def invoice_detail(request, pk):
    """Display invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice
    })

@login_required
def invoice_download_pdf(request, pk):
    """Generate and download PDF invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    # Use the PDF generator
    from .pdf_generator import generate_invoice_pdf_response
    return generate_invoice_pdf_response(invoice)

@login_required
def get_available_worklogs(request, client_id):
    """Get available work logs for a specific client (AJAX endpoint)"""
    try:
        client = Client.objects.get(id=client_id, user=request.user)
        
        # Get work logs that are PENDING and not already invoiced
        available_worklogs = WorkLog.objects.filter(
            user=request.user,
            company_client=client,
            status='PENDING',
            work_date__lte=date.today()  # Can't invoice future work
        ).exclude(
            invoice_line_items__isnull=False  # Not already invoiced
        ).order_by('work_date')
        
        work_logs_data = []
        for worklog in available_worklogs:
            work_logs_data.append({
                'id': worklog.id,
                'work_date': worklog.work_date.strftime('%d/%m/%Y'),
                'hours_worked': str(worklog.hours_worked),
                'hourly_rate': str(worklog.hourly_rate),
                'total_amount': str(worklog.total_amount),
                'description': f"Consulting Services - {worklog.work_date.strftime('%d{worklog.work_date.day} %B')}"
            })
        
        return JsonResponse({
            'success': True,
            'work_logs': work_logs_data
        })
        
    except Client.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Client not found'
        }, status=404)
