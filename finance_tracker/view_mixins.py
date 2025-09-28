from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .mixins import BaseListViewMixin


class BaseCRUDMixin(BaseListViewMixin):
    """
    Base mixin for CRUD operations with common functionality.
    """

    model = None
    form_class = None
    template_name = None
    list_url_name = None
    success_message = None

    def get_queryset(self, request):
        """Get base queryset filtered by user."""
        return self.model.objects.filter(user=request.user)

    def get_list_context(self, request, queryset):
        """Get common context for list views."""
        # Apply filters
        filtered_queryset = self.get_filtered_queryset(queryset, request)

        # Ensure queryset is ordered for consistent pagination
        if not filtered_queryset.ordered:
            filtered_queryset = filtered_queryset.order_by("-date", "-created_at")

        # Pagination
        paginator = Paginator(filtered_queryset, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Get filter values
        month = request.GET.get("month")
        year = request.GET.get("year")
        category_id = request.GET.get("category")

        context = {
            "page_obj": page_obj,
            "selected_month": month,
            "selected_year": year,
            "selected_category": category_id,
            "years": self.get_years_list(),
        }

        return context, filtered_queryset

    def create_view(self, request):
        """Handle create operation."""
        if request.method == "POST":
            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                return redirect(self.list_url_name)
        else:
            form = self.form_class()

        return render(
            request,
            self.template_name,
            {"form": form, "title": f"Add New {self.model.__name__}"},
        )

    def update_view(self, request, pk):
        """Handle update operation."""
        instance = get_object_or_404(self.model, pk=pk, user=request.user)
        if request.method == "POST":
            form = self.form_class(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect(self.list_url_name)
        else:
            form = self.form_class(instance=instance)

        return render(
            request,
            self.template_name,
            {"form": form, "title": f"Edit {self.model.__name__}"},
        )

    def delete_view(self, request, pk):
        """Handle delete operation."""
        instance = get_object_or_404(self.model, pk=pk, user=request.user)
        if request.method == "POST":
            instance.delete()
            return redirect(self.list_url_name)

        return render(
            request,
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_confirm_delete.html",
            {self.model._meta.model_name: instance},
        )

    def detail_view(self, request, pk):
        """Handle detail view."""
        instance = get_object_or_404(self.model, pk=pk, user=request.user)
        return render(
            request,
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_detail.html",
            {self.model._meta.model_name: instance},
        )


def create_crud_views(
    model, form_class, template_name, list_url_name, success_message=None
):
    """
    Factory function to create CRUD views for a model.
    """
    mixin = BaseCRUDMixin()
    mixin.model = model
    mixin.form_class = form_class
    mixin.template_name = template_name
    mixin.list_url_name = list_url_name
    mixin.success_message = success_message

    @login_required
    def list_view(request):
        queryset = mixin.get_queryset(request)
        context, _ = mixin.get_list_context(request, queryset)
        return render(
            request,
            f"{model._meta.app_label}/{model._meta.model_name}_list.html",
            context,
        )

    @login_required
    def create_view(request):
        return mixin.create_view(request)

    @login_required
    def update_view(request, pk):
        return mixin.update_view(request, pk)

    @login_required
    def delete_view(request, pk):
        return mixin.delete_view(request, pk)

    @login_required
    def detail_view(request, pk):
        return mixin.detail_view(request, pk)

    return list_view, create_view, update_view, delete_view, detail_view
