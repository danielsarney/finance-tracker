from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from .models import Category
from .forms import CategoryForm

@login_required
def category_list(request):
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'categories/category_list.html', context)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('categories:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'categories/category_form.html', {
        'form': form, 
        'title': 'Add New Category'
    })

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'categories/category_form.html', {
        'form': form, 
        'title': 'Edit Category'
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        replacement_category_id = request.POST.get('replacement_category')
        
        if replacement_category_id and replacement_category_id != 'none':
            try:
                replacement_category = Category.objects.get(pk=replacement_category_id)
                
                with transaction.atomic():
                    # Update all related items to use the replacement category
                    if category.expense_set.exists():
                        category.expense_set.update(category=replacement_category)
                    
                    if category.income_set.exists():
                        category.income_set.update(category=replacement_category)
                    
                    if category.subscription_set.exists():
                        category.subscription_set.update(category=replacement_category)
                    
                    if category.worklog_set.exists():
                        category.worklog_set.update(category=replacement_category)
                    
                    # Now delete the original category
                    category.delete()
                    
                    messages.success(
                        request, 
                        f'Category "{category.name}" deleted successfully! All items have been moved to "{replacement_category.name}".'
                    )
                    
            except Category.DoesNotExist:
                messages.error(request, 'Selected replacement category does not exist.')
                return redirect('categories:category_delete', pk=pk)
        else:
            # No replacement category selected, just delete
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        
        return redirect('categories:category_list')
    
    # Check if category is being used
    is_used = category.is_used()
    usage_breakdown = category.get_usage_breakdown() if is_used else None
    
    # Get other categories for replacement (excluding the current one)
    replacement_categories = Category.objects.exclude(pk=category.pk).order_by('name')
    
    context = {
        'category': category,
        'is_used': is_used,
        'usage_breakdown': usage_breakdown,
        'replacement_categories': replacement_categories,
    }
    
    return render(request, 'categories/category_confirm_delete.html', context)

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'categories/category_detail.html', {'category': category})
