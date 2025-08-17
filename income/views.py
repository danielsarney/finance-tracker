from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Income
from .forms import IncomeForm

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user)
    
    # Date filtering
    month = request.GET.get('month')
    year = request.GET.get('year')
    category_id = request.GET.get('category')
    
    if month:
        incomes = incomes.filter(date__month=month)
    if year:
        incomes = incomes.filter(date__year=int(year))
    if category_id:
        incomes = incomes.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(incomes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Generate years list for the filter
    current_year = timezone.now().year
    years = list(range(2020, 2081))
    
    # Get categories for the filter dropdown
    from categories.models import Category
    categories = Category.objects.filter(category_type='income')
    
    context = {
        'page_obj': page_obj,
        'total_income': total_income,
        'selected_month': month,
        'selected_year': year,
        'selected_category': category_id,
        'years': years,
        'categories': categories,
    }
    return render(request, 'income/income_list.html', context)

@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income entry created successfully!')
            return redirect('income:income_list')
    else:
        form = IncomeForm()
    
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Add New Income'})

@login_required
def income_update(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income entry updated successfully!')
            return redirect('income:income_list')
    else:
        form = IncomeForm(instance=income)
    
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Edit Income'})

@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income entry deleted successfully!')
        return redirect('income:income_list')
    
    return render(request, 'income/income_confirm_delete.html', {'income': income})

@login_required
def income_detail(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    return render(request, 'income/income_detail.html', {'income': income})
