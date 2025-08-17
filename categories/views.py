from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category
from .forms import CategoryForm

@login_required
def category_list(request):
    categories = Category.objects.all()
    
    # Filter by category type
    category_type = request.GET.get('type')
    if category_type:
        categories = categories.filter(category_type=category_type)
    
    # Pagination
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_types': Category.CATEGORY_TYPES,
        'selected_type': category_type,
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
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('categories:category_list')
    
    return render(request, 'categories/category_confirm_delete.html', {'category': category})

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'categories/category_detail.html', {'category': category})
