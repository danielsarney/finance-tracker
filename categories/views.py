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
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }
    return render(request, "categories/category_list.html", context)


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect("categories:category_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "categories/category_form.html",
        {"form": form, "title": "Add New Category"},
    )


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("categories:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "categories/category_form.html",
        {"form": form, "title": "Edit Category"},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        replacement_category_id = request.POST.get("replacement_category")

        # Debug: Print what we received
        print(f"POST data: {request.POST}")
        print(f"Replacement category ID: {replacement_category_id}")
        print(f"Category is_used: {category.is_used()}")

        # Check if category is being used
        is_used = category.is_used()

        if is_used:
            if not replacement_category_id or replacement_category_id == "":
                print("No replacement category selected")
                messages.error(request, "Please select a replacement category.")
                return redirect("categories:category_delete", pk=pk)

            try:
                replacement_category = Category.objects.get(pk=replacement_category_id)
                print(f"Found replacement category: {replacement_category.name}")

                with transaction.atomic():
                    # Update all related items to use the replacement category
                    if category.expense_set.exists():
                        print(f"Updating {category.expense_set.count()} expenses")
                        category.expense_set.update(category=replacement_category)

                    if category.income_set.exists():
                        print(f"Updating {category.income_set.count()} income entries")
                        category.income_set.update(category=replacement_category)

                    if category.subscription_set.exists():
                        print(
                            f"Updating {category.subscription_set.count()} subscriptions"
                        )
                        category.subscription_set.update(category=replacement_category)

                    # Now delete the original category
                    print("Deleting original category")
                    category.delete()
                    print("Category deleted successfully")
                    messages.success(
                        request,
                        f"Category deleted successfully! All items moved to {replacement_category.name}.",
                    )

                    # If we get here, deletion was successful
                    return redirect("categories:category_list")

            except Category.DoesNotExist:
                print("Replacement category not found")
                messages.error(request, "Selected replacement category does not exist.")
                return redirect("categories:category_delete", pk=pk)
            except Exception as e:
                print(f"Error during deletion: {e}")
                # If any error occurs, redirect back to delete page
                return redirect("categories:category_delete", pk=pk)
        else:
            # Category is not being used, safe to delete
            try:
                print("Category not in use, deleting directly")
                category.delete()
                print("Category deleted successfully")
                messages.success(request, "Category deleted successfully!")

                return redirect("categories:category_list")
            except Exception as e:
                print(f"Error during deletion: {e}")
                # If deletion fails, redirect back to delete page
                return redirect("categories:category_delete", pk=pk)

    # Check if category is being used
    is_used = category.is_used()

    # Only get replacement categories if the category is being used
    replacement_categories = None
    usage_breakdown = None
    if is_used:
        replacement_categories = Category.objects.exclude(pk=category.pk).order_by(
            "name"
        )
        # Create usage breakdown
        usage_breakdown = {
            "expenses": category.expense_set.count(),
            "income": category.income_set.count(),
            "subscriptions": category.subscription_set.count(),
        }

    context = {
        "category": category,
        "is_used": is_used,
        "replacement_categories": replacement_categories,
        "usage_breakdown": usage_breakdown,
    }

    return render(request, "categories/category_confirm_delete.html", context)


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, "categories/category_detail.html", {"category": category})
