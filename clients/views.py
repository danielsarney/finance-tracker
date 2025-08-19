from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Client
from .forms import ClientForm

@login_required
def client_list(request):
    """Display list of all clients for the current user"""
    search_query = request.GET.get('search', '')
    
    clients = Client.objects.filter(user=request.user)
    
    # Apply search filter
    if search_query:
        clients = clients.filter(
            Q(company_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(town__icontains=search_query)
        )
    
    # Apply ordering
    clients = clients.order_by('company_name')
    
    context = {
        'clients': clients,
        'search_query': search_query,
        'total_clients': clients.count(),
    }
    
    return render(request, 'clients/client_list.html', context)

@login_required
def client_create(request):
    """Create a new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, f'Client "{client.company_name}" created successfully!')
            return redirect('clients:client_list')
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'title': 'Add New Client',
        'submit_text': 'Create Client'
    })

@login_required
def client_detail(request, pk):
    """Display detailed information about a specific client"""
    client = get_object_or_404(Client, pk=pk, user=request.user)
    
    return render(request, 'clients/client_detail.html', {
        'client': client
    })

@login_required
def client_update(request, pk):
    """Update an existing client"""
    client = get_object_or_404(Client, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{client.company_name}" updated successfully!')
            return redirect('clients:client_list')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client,
        'title': f'Edit Client: {client.company_name}',
        'submit_text': 'Update Client'
    })


