from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Expense
from .forms import ExpenseForm

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    
    # Date filtering
    month = request.GET.get('month')
    year = request.GET.get('year')
    category_id = request.GET.get('category')
    
    if month:
        expenses = expenses.filter(date__month=month)
    if year:
        expenses = expenses.filter(date__year=int(year))
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Generate years list for the filter
    current_year = timezone.now().year
    years = list(range(2020, 2081))
    
    # Get categories for the filter dropdown
    from categories.models import Category
    categories = Category.objects.filter(category_type='expense')
    
    context = {
        'page_obj': page_obj,
        'total_expenses': total_expenses,
        'selected_month': month,
        'selected_year': year,
        'selected_category': category_id,
        'years': years,
        'categories': categories,
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense created successfully!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add New Expense'})

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expenses:expense_list')
    
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})
