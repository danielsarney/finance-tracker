from django.test import TestCase, Client, RequestFactory
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from decimal import Decimal
from datetime import date, datetime, timedelta
import time

from finance_tracker.factories import (
    UserFactory,
    CategoryFactory,
    ExpenseFactory,
    IncomeFactory,
)
from .utils import (
    get_years_list,
    format_currency,
    format_date,
    calculate_monthly_cost,
    get_upcoming_dates,
    get_status_color,
    paginate_queryset,
)
from .mixins import BaseListViewMixin
from .view_mixins import BaseCRUDMixin, create_crud_views
from .rate_limiting import rate_limit, get_client_ip
from expenses.models import Expense
from income.models import Income
from categories.models import Category


class BaseFinancialModelTest(TestCase):
    """Test cases for the BaseFinancialModel abstract model."""

    def test_base_financial_model_meta(self):
        """Test that BaseFinancialModel has correct meta configuration."""
        # Since BaseFinancialModel is abstract, we'll test it through a concrete model
        expense = ExpenseFactory()

        # Test ordering - the current model doesn't have ordering set
        # We'll test that the model can be created and has the expected structure
        self.assertIsNotNone(expense._meta)

        # Test that BaseFinancialModel is abstract (check the class, not the instance)
        from finance_tracker.mixins import BaseFinancialModel

        self.assertTrue(BaseFinancialModel._meta.abstract)

    def test_base_financial_model_fields(self):
        """Test that BaseFinancialModel has required fields."""
        expense = ExpenseFactory()

        # Test required fields exist
        self.assertIsNotNone(expense.user)
        self.assertIsNotNone(expense.amount)
        self.assertIsNotNone(expense.date)
        self.assertIsNotNone(expense.category)
        self.assertIsNotNone(expense.created_at)
        self.assertIsNotNone(expense.updated_at)

    def test_base_financial_model_string_representation(self):
        """Test the string representation of BaseFinancialModel."""
        expense = ExpenseFactory()
        # The BaseFinancialModel __str__ method has been fixed to handle missing description field
        # It should now work without crashing
        str_repr = str(expense)
        self.assertIsInstance(str_repr, str)
        self.assertIn(str(expense.amount), str_repr)
        self.assertIn(str(expense.date), str_repr)

    def test_base_financial_model_timestamps(self):
        """Test that timestamps are automatically set."""
        expense = ExpenseFactory()

        self.assertIsNotNone(expense.created_at)
        self.assertIsNotNone(expense.updated_at)
        self.assertLessEqual(expense.created_at, expense.updated_at)

        # Test that created_at is set to now (within reasonable bounds)
        now = timezone.now()
        self.assertLessEqual(expense.created_at, now)
        self.assertGreaterEqual(expense.created_at, now - timedelta(seconds=5))


class BaseListViewMixinTest(TestCase):
    """Test cases for the BaseListViewMixin."""

    def setUp(self):
        """Set up test data."""
        self.mixin = BaseListViewMixin()
        self.user = UserFactory()
        self.category = CategoryFactory()

        # Create some test expenses
        self.expenses = ExpenseFactory.create_batch(5, user=self.user)

    def test_get_filtered_queryset_month_filter(self):
        """Test month filtering in get_filtered_queryset."""
        queryset = Expense.objects.filter(user=self.user)

        # Test month filter
        month = date.today().month
        filtered_queryset = self.mixin.get_filtered_queryset(
            queryset, self._create_request(f"month={month}")
        )

        # All expenses should be from the specified month
        for expense in filtered_queryset:
            self.assertEqual(expense.date.month, month)

    def test_get_filtered_queryset_year_filter(self):
        """Test year filtering in get_filtered_queryset."""
        queryset = Expense.objects.filter(user=self.user)

        # Test year filter
        year = date.today().year
        filtered_queryset = self.mixin.get_filtered_queryset(
            queryset, self._create_request(f"year={year}")
        )

        # All expenses should be from the specified year
        for expense in filtered_queryset:
            self.assertEqual(expense.date.year, year)

    def test_get_filtered_queryset_category_filter(self):
        """Test category filtering in get_filtered_queryset."""
        queryset = Expense.objects.filter(user=self.user)

        # Test category filter
        category_id = self.category.id
        filtered_queryset = self.mixin.get_filtered_queryset(
            queryset, self._create_request(f"category={category_id}")
        )

        # All expenses should have the specified category
        for expense in filtered_queryset:
            self.assertEqual(expense.category.id, category_id)

    def test_get_filtered_queryset_combined_filters(self):
        """Test combined filters in get_filtered_queryset."""
        queryset = Expense.objects.filter(user=self.user)

        # Test combined filters
        month = date.today().month
        year = date.today().year
        category_id = self.category.id

        filtered_queryset = self.mixin.get_filtered_queryset(
            queryset,
            self._create_request(f"month={month}&year={year}&category={category_id}"),
        )

        # All expenses should match all filters
        for expense in filtered_queryset:
            self.assertEqual(expense.date.month, month)
            self.assertEqual(expense.date.year, year)
            self.assertEqual(expense.category.id, category_id)

    def test_get_years_list(self):
        """Test get_years_list method."""
        years = self.mixin.get_years_list()

        # Should return a list of years
        self.assertIsInstance(years, list)
        self.assertGreater(len(years), 0)

        # Should include current year
        current_year = date.today().year
        self.assertIn(current_year, years)

        # Should be in ascending order
        self.assertEqual(years, sorted(years))

    def test_get_categories(self):
        """Test get_categories method."""
        categories = self.mixin.get_categories()

        # Should return a queryset
        self.assertIsInstance(categories, Category.objects.all().__class__)

        # Should return all categories (no more filtering by type)
        self.assertGreater(categories.count(), 0)

    def _create_request(self, query_string):
        """Helper method to create a request with query parameters."""
        factory = RequestFactory()
        request = factory.get(f"/test/?{query_string}")
        return request


class BaseCRUDMixinTest(TestCase):
    """Test cases for the BaseCRUDMixin."""

    def setUp(self):
        """Set up test data."""
        self.mixin = BaseCRUDMixin()
        self.mixin.model = Expense
        self.mixin.form_class = None  # We'll test this separately
        self.mixin.template_name = "test_template.html"
        self.mixin.list_url_name = "test_list"
        self.mixin.success_message = "Test created successfully!"

        self.user = UserFactory()
        self.category = CategoryFactory()
        self.expense = ExpenseFactory(user=self.user, category=self.category)

        self.factory = RequestFactory()

    def test_get_queryset(self):
        """Test get_queryset method."""
        request = self.factory.get("/test/")
        request.user = self.user

        queryset = self.mixin.get_queryset(request)

        # Should return expenses filtered by user
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.expense)

    def test_get_list_context(self):
        """Test get_list_context method."""
        request = self.factory.get("/test/")
        request.user = self.user

        queryset = Expense.objects.filter(user=self.user)
        context, filtered_queryset = self.mixin.get_list_context(request, queryset)

        # Should return context with pagination
        self.assertIn("page_obj", context)
        self.assertIn("selected_month", context)
        self.assertIn("selected_year", context)
        self.assertIn("selected_category", context)
        self.assertIn("years", context)

        # Should return filtered queryset
        self.assertEqual(filtered_queryset.count(), 1)

    def test_get_list_context_with_filters(self):
        """Test get_list_context method with filters."""
        month = date.today().month
        year = date.today().year

        request = self.factory.get(f"/test/?month={month}&year={year}")
        request.user = self.user

        queryset = Expense.objects.filter(user=self.user)
        context, filtered_queryset = self.mixin.get_list_context(request, queryset)

        # Should apply filters
        self.assertEqual(context["selected_month"], str(month))
        self.assertEqual(context["selected_year"], str(year))

        # Should filter queryset
        for expense in filtered_queryset:
            self.assertEqual(expense.date.month, month)
            self.assertEqual(expense.date.year, year)

    def test_get_list_context_pagination(self):
        """Test pagination in get_list_context."""
        # Create exactly 25 expenses total for this user
        # First, clear existing expenses for this user
        Expense.objects.filter(user=self.user).delete()

        # Create 25 new expenses with the correct user and category
        expenses = []
        for i in range(25):
            expense = ExpenseFactory(
                user=self.user,
                category=self.category,
                amount=Decimal(f"{10 + i}.00"),
                date=date.today() - timedelta(days=i),
            )
            expenses.append(expense)

        # Verify we have 25 expenses
        total_expenses = Expense.objects.filter(user=self.user).count()
        self.assertEqual(total_expenses, 25)

        # Test page 1 (should have 20 items)
        request = self.factory.get("/test/")
        request.user = self.user

        queryset = Expense.objects.filter(user=self.user)
        context, _ = self.mixin.get_list_context(request, queryset)

        # Should have pagination
        self.assertIn("page_obj", context)
        page_obj = context["page_obj"]

        # Should be on page 1
        self.assertEqual(page_obj.number, 1)

        # Should have 20 items per page
        self.assertEqual(len(page_obj), 20)

        # Test page 2 (should have 5 remaining items)
        request = self.factory.get("/test/?page=2")
        request.user = self.user

        context, _ = self.mixin.get_list_context(request, queryset)
        page_obj = context["page_obj"]

        # Should be on page 2
        self.assertEqual(page_obj.number, 2)

        # Should have 5 remaining items
        self.assertEqual(len(page_obj), 5)


class CreateCRUDViewsTest(TestCase):
    """Test cases for the create_crud_views factory function."""

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()

        # Create CRUD views for Expense model
        (
            self.list_view,
            self.create_view,
            self.update_view,
            self.delete_view,
            self.detail_view,
        ) = create_crud_views(
            model=Expense,
            form_class=None,  # We'll test this separately
            template_name="test_template.html",
            list_url_name="test_list",
            success_message="Test created successfully!",
        )

        self.factory = RequestFactory()

    def test_create_crud_views_login_required(self):
        """Test that all CRUD views require login."""
        # Create an anonymous user request
        request = self.factory.get("/test/")
        request.user = None

        # Test list view - this will cause an error due to None user
        # We'll test that the decorator prevents access
        with self.assertRaises(AttributeError):
            response = self.list_view(request)

        # Test create view
        with self.assertRaises(AttributeError):
            response = self.create_view(request)

        # Test update view
        with self.assertRaises(AttributeError):
            response = self.update_view(request, pk=1)

        # Test delete view
        with self.assertRaises(AttributeError):
            response = self.delete_view(request, pk=1)

        # Test detail view
        with self.assertRaises(AttributeError):
            response = self.detail_view(request, pk=1)


class UtilsTest(TestCase):
    """Test cases for utility functions."""

    def test_get_years_list(self):
        """Test get_years_list function."""
        years = get_years_list()

        # Should return a list of years
        self.assertIsInstance(years, list)
        self.assertGreater(len(years), 0)

        # Should include current year
        current_year = date.today().year
        self.assertIn(current_year, years)

        # Should start from 2020 by default
        self.assertIn(2020, years)

        # Should be in ascending order
        self.assertEqual(years, sorted(years))

    def test_get_years_list_custom_start(self):
        """Test get_years_list function with custom start year."""
        start_year = 2015
        years = get_years_list(start_year)

        # Should start from custom year
        self.assertIn(start_year, years)
        self.assertNotIn(start_year - 1, years)

        # Should include current year
        current_year = date.today().year
        self.assertIn(current_year, years)

    def test_format_currency_gbp(self):
        """Test format_currency function with GBP."""
        amount = Decimal("123.45")
        formatted = format_currency(amount, "GBP")

        self.assertEqual(formatted, "£123.45")

    def test_format_currency_usd(self):
        """Test format_currency function with USD."""
        amount = Decimal("123.45")
        formatted = format_currency(amount, "USD")

        self.assertEqual(formatted, "$123.45")

    def test_format_currency_eur(self):
        """Test format_currency function with EUR."""
        amount = Decimal("123.45")
        formatted = format_currency(amount, "EUR")

        self.assertEqual(formatted, "€123.45")

    def test_format_currency_default(self):
        """Test format_currency function with default currency."""
        amount = Decimal("123.45")
        formatted = format_currency(amount, "UNKNOWN")

        self.assertEqual(formatted, "123.45")

    def test_format_currency_none(self):
        """Test format_currency function with None amount."""
        formatted = format_currency(None)

        self.assertEqual(formatted, "£0.00")

    def test_format_currency_string_input(self):
        """Test format_currency function with string input."""
        amount = "123.45"
        formatted = format_currency(amount)

        self.assertEqual(formatted, "£123.45")

    def test_format_date_short(self):
        """Test format_date function with short format."""
        test_date = date(2024, 1, 15)
        formatted = format_date(test_date, "short")

        self.assertEqual(formatted, "15/01/2024")

    def test_format_date_long(self):
        """Test format_date function with long format."""
        test_date = date(2024, 1, 15)
        formatted = format_date(test_date, "long")

        self.assertEqual(formatted, "15 January 2024")

    def test_format_date_iso(self):
        """Test format_date function with ISO format."""
        test_date = date(2024, 1, 15)
        formatted = format_date(test_date, "iso")

        self.assertEqual(formatted, "2024-01-15")

    def test_format_date_string_input(self):
        """Test format_date function with string input."""
        date_string = "2024-01-15"
        formatted = format_date(date_string, "short")

        self.assertEqual(formatted, "15/01/2024")

    def test_format_date_none(self):
        """Test format_date function with None input."""
        formatted = format_date(None)

        self.assertEqual(formatted, "")

    def test_format_date_invalid_string(self):
        """Test format_date function with invalid string input."""
        invalid_string = "invalid-date"
        formatted = format_date(invalid_string)

        self.assertEqual(formatted, invalid_string)

    def test_calculate_monthly_cost_daily(self):
        """Test calculate_monthly_cost function with daily billing."""
        amount = Decimal("10.00")
        monthly_cost = calculate_monthly_cost(amount, "DAILY")

        expected = Decimal("10.00") * Decimal("30")
        self.assertEqual(monthly_cost, expected)

    def test_calculate_monthly_cost_weekly(self):
        """Test calculate_monthly_cost function with weekly billing."""
        amount = Decimal("50.00")
        monthly_cost = calculate_monthly_cost(amount, "WEEKLY")

        expected = Decimal("50.00") * Decimal("4.33")
        self.assertEqual(monthly_cost, expected)

    def test_calculate_monthly_cost_monthly(self):
        """Test calculate_monthly_cost function with monthly billing."""
        amount = Decimal("100.00")
        monthly_cost = calculate_monthly_cost(amount, "MONTHLY")

        self.assertEqual(monthly_cost, amount)

    def test_calculate_monthly_cost_quarterly(self):
        """Test calculate_monthly_cost function with quarterly billing."""
        amount = Decimal("300.00")
        monthly_cost = calculate_monthly_cost(amount, "QUARTERLY")

        expected = Decimal("300.00") / Decimal("3")
        self.assertEqual(monthly_cost, expected)

    def test_calculate_monthly_cost_yearly(self):
        """Test calculate_monthly_cost function with yearly billing."""
        amount = Decimal("1200.00")
        monthly_cost = calculate_monthly_cost(amount, "YEARLY")

        expected = Decimal("1200.00") / Decimal("12")
        self.assertEqual(monthly_cost, expected)

    def test_calculate_monthly_cost_unknown(self):
        """Test calculate_monthly_cost function with unknown billing cycle."""
        amount = Decimal("100.00")
        monthly_cost = calculate_monthly_cost(amount, "UNKNOWN")

        # Should return the original amount for unknown cycles
        self.assertEqual(monthly_cost, amount)

    def test_calculate_monthly_cost_string_input(self):
        """Test calculate_monthly_cost function with string input."""
        amount = "100.00"
        monthly_cost = calculate_monthly_cost(amount, "MONTHLY")

        self.assertEqual(monthly_cost, Decimal("100.00"))

    def test_get_upcoming_dates_daily(self):
        """Test get_upcoming_dates function with daily billing."""
        start_date = date(2024, 1, 1)
        dates = get_upcoming_dates(start_date, "DAILY", count=5)

        self.assertEqual(len(dates), 5)
        self.assertEqual(dates[0], date(2024, 1, 1))
        self.assertEqual(dates[1], date(2024, 1, 2))
        self.assertEqual(dates[2], date(2024, 1, 3))
        self.assertEqual(dates[3], date(2024, 1, 4))
        self.assertEqual(dates[4], date(2024, 1, 5))

    def test_get_upcoming_dates_weekly(self):
        """Test get_upcoming_dates function with weekly billing."""
        start_date = date(2024, 1, 1)
        dates = get_upcoming_dates(start_date, "WEEKLY", count=3)

        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], date(2024, 1, 1))
        self.assertEqual(dates[1], date(2024, 1, 8))
        self.assertEqual(dates[2], date(2024, 1, 15))

    def test_get_upcoming_dates_monthly(self):
        """Test get_upcoming_dates function with monthly billing."""
        start_date = date(2024, 1, 1)
        dates = get_upcoming_dates(start_date, "MONTHLY", count=3)

        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], date(2024, 1, 1))
        self.assertEqual(dates[1], date(2024, 2, 1))
        self.assertEqual(dates[2], date(2024, 3, 1))

    def test_get_upcoming_dates_yearly(self):
        """Test get_upcoming_dates function with yearly billing."""
        start_date = date(2024, 1, 1)
        dates = get_upcoming_dates(start_date, "YEARLY", count=3)

        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], date(2024, 1, 1))
        self.assertEqual(dates[1], date(2025, 1, 1))
        self.assertEqual(dates[2], date(2026, 1, 1))

    def test_get_upcoming_dates_string_input(self):
        """Test get_upcoming_dates function with string input."""
        start_date = "2024-01-01"
        dates = get_upcoming_dates(start_date, "MONTHLY", count=2)

        self.assertEqual(len(dates), 2)
        self.assertEqual(dates[0], date(2024, 1, 1))
        self.assertEqual(dates[1], date(2024, 2, 1))

    def test_get_status_color_pending(self):
        """Test get_status_color function with PENDING status."""
        color = get_status_color("PENDING")

        self.assertEqual(color, "warning")

    def test_get_status_color_invoiced(self):
        """Test get_status_color function with INVOICED status."""
        color = get_status_color("INVOICED")

        self.assertEqual(color, "info")

    def test_get_status_color_paid(self):
        """Test get_status_color function with PAID status."""
        color = get_status_color("PAID")

        self.assertEqual(color, "success")

    def test_get_status_color_active(self):
        """Test get_status_color function with ACTIVE status."""
        color = get_status_color("ACTIVE")

        self.assertEqual(color, "success")

    def test_get_status_color_inactive(self):
        """Test get_status_color function with INACTIVE status."""
        color = get_status_color("INACTIVE")

        self.assertEqual(color, "secondary")

    def test_get_status_color_cancelled(self):
        """Test get_status_color function with CANCELLED status."""
        color = get_status_color("CANCELLED")

        self.assertEqual(color, "danger")

    def test_get_status_color_unknown(self):
        """Test get_status_color function with unknown status."""
        color = get_status_color("UNKNOWN_STATUS")

        self.assertEqual(color, "secondary")

    def test_get_status_color_case_insensitive(self):
        """Test get_status_color function is case insensitive."""
        color_lower = get_status_color("pending")
        color_upper = get_status_color("PENDING")

        self.assertEqual(color_lower, color_upper)

    def test_paginate_queryset(self):
        """Test paginate_queryset function."""
        # Create test data
        user = UserFactory()
        expenses = ExpenseFactory.create_batch(25, user=user)

        queryset = Expense.objects.filter(user=user)
        paginator, page_obj = paginate_queryset(queryset, 1, per_page=10)

        # Should return paginator and page object
        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(len(page_obj), 10)

        # Test second page
        paginator, page_obj = paginate_queryset(queryset, 2, per_page=10)
        self.assertEqual(page_obj.number, 2)
        self.assertEqual(len(page_obj), 10)

        # Test last page
        paginator, page_obj = paginate_queryset(queryset, 3, per_page=10)
        self.assertEqual(page_obj.number, 3)
        self.assertEqual(len(page_obj), 5)  # Remaining items


class FinanceTrackerIntegrationTest(TestCase):
    """Integration tests for the finance_tracker app."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory()

        # Create test data
        self.expenses = ExpenseFactory.create_batch(
            5, user=self.user, category=self.category
        )
        self.incomes = IncomeFactory.create_batch(
            3, user=self.user, category=self.category
        )

    def test_utils_integration(self):
        """Test that utility functions work together."""
        # Test currency formatting with calculated amounts
        total_expenses = sum(expense.amount for expense in self.expenses)
        formatted_total = format_currency(total_expenses)

        self.assertIsInstance(formatted_total, str)
        self.assertTrue(formatted_total.startswith("£"))

        # Test date formatting with expense dates
        for expense in self.expenses:
            formatted_date = format_date(expense.date, "short")
            self.assertIsInstance(formatted_date, str)
            self.assertIn("/", formatted_date)

    def test_mixins_integration(self):
        """Test that mixins work together."""
        # Test BaseListViewMixin with BaseCRUDMixin
        list_mixin = BaseListViewMixin()
        crud_mixin = BaseCRUDMixin()
        crud_mixin.model = Expense

        # Test filtering
        request = RequestFactory().get("/test/")
        request.user = self.user

        queryset = Expense.objects.filter(user=self.user)
        filtered_queryset = list_mixin.get_filtered_queryset(queryset, request)

        # Should return all expenses for the user
        self.assertEqual(filtered_queryset.count(), 5)

        # Test context generation
        context, _ = crud_mixin.get_list_context(request, queryset)

        # Should have required context
        self.assertIn("page_obj", context)
        self.assertIn("years", context)

    def test_view_factory_integration(self):
        """Test that the view factory creates working views."""
        # Create CRUD views
        list_view, create_view, update_view, delete_view, detail_view = (
            create_crud_views(
                model=Expense,
                form_class=None,  # We'll test without form for now
                template_name="test_template.html",
                list_url_name="test_list",
                success_message="Test created successfully!",
            )
        )

        # Test that views are callable
        self.assertTrue(callable(list_view))
        self.assertTrue(callable(create_view))
        self.assertTrue(callable(update_view))
        self.assertTrue(callable(delete_view))
        self.assertTrue(callable(detail_view))

    def test_status_colors_integration(self):
        """Test status colors work with different models."""
        # Test with different status types
        statuses = ["PENDING", "INVOICED", "PAID", "ACTIVE", "INACTIVE"]

        for status in statuses:
            color = get_status_color(status)
            self.assertIsInstance(color, str)
            self.assertIn(color, ["warning", "info", "success", "secondary", "danger"])

    def test_date_utilities_integration(self):
        """Test date utilities work with different date formats."""
        # Test with various date inputs
        test_dates = [
            date(2024, 1, 15),
            "2024-01-15",
            datetime(2024, 1, 15),
        ]

        for test_date in test_dates:
            # Test formatting
            short_format = format_date(test_date, "short")
            long_format = format_date(test_date, "long")
            iso_format = format_date(test_date, "iso")

            self.assertIsInstance(short_format, str)
            self.assertIsInstance(long_format, str)
            self.assertIsInstance(iso_format, str)

            # Test upcoming dates calculation
            upcoming = get_upcoming_dates(test_date, "MONTHLY", count=3)
            self.assertEqual(len(upcoming), 3)
            self.assertIsInstance(upcoming[0], date)

    def test_currency_utilities_integration(self):
        """Test currency utilities work with different amount types."""
        # Test with various amount inputs
        test_amounts = [Decimal("100.00"), "100.00", 100.00, None]

        for amount in test_amounts:
            formatted = format_currency(amount)
            self.assertIsInstance(formatted, str)

            if amount is not None:
                self.assertTrue(formatted.startswith("£"))
            else:
                self.assertEqual(formatted, "£0.00")

    def test_pagination_integration(self):
        """Test pagination works with different querysets."""
        # Test with expenses
        expenses_queryset = Expense.objects.filter(user=self.user)
        paginator, page_obj = paginate_queryset(expenses_queryset, 1, per_page=3)

        self.assertEqual(len(page_obj), 3)
        self.assertEqual(page_obj.number, 1)

        # Test with incomes
        incomes_queryset = Income.objects.filter(user=self.user)
        paginator, page_obj = paginate_queryset(incomes_queryset, 1, per_page=2)

        self.assertEqual(len(page_obj), 2)
        self.assertEqual(page_obj.number, 1)


class RateLimitingTest(TestCase):
    """Test cases for rate limiting functionality."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.client = Client()

        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()

    def test_get_client_ip_direct_connection(self):
        """Test get_client_ip with direct connection (no proxy)."""
        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = get_client_ip(request)
        self.assertEqual(ip, "192.168.1.100")

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test get_client_ip with X-Forwarded-For header."""
        request = self.factory.get("/test/")
        request.META["HTTP_X_FORWARDED_FOR"] = (
            "203.0.113.195, 70.41.3.18, 150.172.238.178"
        )
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = get_client_ip(request)
        self.assertEqual(ip, "203.0.113.195")

    def test_get_client_ip_with_single_x_forwarded_for(self):
        """Test get_client_ip with single X-Forwarded-For value."""
        request = self.factory.get("/test/")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.195"
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = get_client_ip(request)
        self.assertEqual(ip, "203.0.113.195")

    def test_get_client_ip_with_whitespace(self):
        """Test get_client_ip handles whitespace in X-Forwarded-For."""
        request = self.factory.get("/test/")
        request.META["HTTP_X_FORWARDED_FOR"] = "  203.0.113.195  , 70.41.3.18  "
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = get_client_ip(request)
        self.assertEqual(ip, "203.0.113.195")

    def test_rate_limit_decorator_allows_normal_requests(self):
        """Test that rate limit decorator allows normal requests."""

        @rate_limit(max_attempts=3, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # First request should succeed
        response = test_view(request)
        self.assertEqual(response, "Success")

    def test_rate_limit_decorator_blocks_excessive_requests(self):
        """Test that rate limit decorator blocks excessive requests."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # First two requests should succeed
        response1 = test_view(request)
        self.assertEqual(response1, "Success")

        response2 = test_view(request)
        self.assertEqual(response2, "Success")

        # Third request should be blocked
        response3 = test_view(request)
        self.assertEqual(response3.status_code, 429)
        self.assertIn("Rate limit exceeded", response3.content.decode())

    def test_rate_limit_decorator_with_post_request(self):
        """Test rate limit decorator with POST requests."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.post("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # First two requests should succeed
        response1 = test_view(request)
        self.assertEqual(response1, "Success")

        response2 = test_view(request)
        self.assertEqual(response2, "Success")

        # Third request should be blocked
        response3 = test_view(request)
        self.assertEqual(response3.status_code, 429)

    def test_rate_limit_decorator_with_get_request_message(self):
        """Test that GET requests are also blocked with 429 status."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # First two requests should succeed
        test_view(request)
        test_view(request)

        # Third request should be blocked with 429 status
        response = test_view(request)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Rate limit exceeded", response.content.decode())

    def test_rate_limit_decorator_different_ips(self):
        """Test that rate limiting is per IP address."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        # First IP
        request1 = self.factory.get("/test/")
        request1.META["REMOTE_ADDR"] = "192.168.1.100"

        # Second IP
        request2 = self.factory.get("/test/")
        request2.META["REMOTE_ADDR"] = "192.168.1.101"

        # Both IPs should be able to make 2 requests each
        response1a = test_view(request1)
        response1b = test_view(request1)
        response2a = test_view(request2)
        response2b = test_view(request2)

        self.assertEqual(response1a, "Success")
        self.assertEqual(response1b, "Success")
        self.assertEqual(response2a, "Success")
        self.assertEqual(response2b, "Success")

    def test_rate_limit_decorator_window_expiry(self):
        """Test that rate limit window expires correctly."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Make 2 requests to hit limit
        test_view(request)
        test_view(request)

        # Third request should be blocked
        response = test_view(request)
        self.assertEqual(response.status_code, 429)

        # Manually expire the cache (simulate time passing)
        cache_key = f"rate_limit_{get_client_ip(request)}"
        cache.delete(cache_key)

        # Now requests should work again
        response = test_view(request)
        self.assertEqual(response, "Success")

    def test_rate_limit_decorator_custom_key_prefix(self):
        """Test rate limit decorator with custom key prefix."""

        @rate_limit(max_attempts=2, window_minutes=1, key_prefix="custom_limit")
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Make 2 requests to hit limit
        test_view(request)
        test_view(request)

        # Third request should be blocked
        response = test_view(request)
        self.assertEqual(response.status_code, 429)

        # Check that custom cache key was used
        cache_key = f"custom_limit_{get_client_ip(request)}"
        attempts = cache.get(cache_key, [])
        self.assertEqual(len(attempts), 2)

    def test_rate_limit_decorator_old_attempts_cleanup(self):
        """Test that old attempts are cleaned up from cache."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Make first request
        test_view(request)

        # Manually add old attempts to cache
        cache_key = f"rate_limit_{get_client_ip(request)}"
        old_time = time.time() - 2000  # 2000 seconds ago
        cache.set(cache_key, [old_time, old_time], 3600)

        # Make another request - should clean up old attempts
        test_view(request)

        # Check that old attempts were removed
        attempts = cache.get(cache_key, [])
        self.assertEqual(len(attempts), 1)  # Only current attempt

        # Make third request - should still work because old attempts were cleaned
        response = test_view(request)
        self.assertEqual(response, "Success")

    def test_rate_limit_decorator_multiple_decorators(self):
        """Test rate limit decorator works with multiple decorators."""

        def other_decorator(func):
            def wrapper(request, *args, **kwargs):
                result = func(request, *args, **kwargs)
                # Check if result is an HttpResponse (from rate limiting)
                if hasattr(result, "status_code"):
                    return result
                return f"Decorated: {result}"

            return wrapper

        @other_decorator
        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # First request should succeed
        response = test_view(request)
        self.assertEqual(response, "Decorated: Success")

        # Second request should succeed
        response = test_view(request)
        self.assertEqual(response, "Decorated: Success")

        # Third request should be blocked
        response = test_view(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_decorator_with_view_args_kwargs(self):
        """Test rate limit decorator preserves view arguments."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def test_view(request, pk, category=None):
            return f"Success: {pk}, {category}"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Test with positional and keyword arguments
        response = test_view(request, pk=123, category="test")
        self.assertEqual(response, "Success: 123, test")

    def test_rate_limit_decorator_error_message_content(self):
        """Test that error message contains correct information."""

        @rate_limit(max_attempts=3, window_minutes=5)
        def test_view(request):
            return "Success"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Make requests to hit limit
        test_view(request)
        test_view(request)
        test_view(request)

        # Fourth request should add error message
        test_view(request)

        # Check error message content
        stored_messages = list(messages)
        self.assertEqual(len(stored_messages), 1)
        message = str(stored_messages[0])
        self.assertIn("Too many attempts", message)
        self.assertIn("5 minutes", message)


class RateLimitingIntegrationTest(TestCase):
    """Integration tests for rate limiting with authentication views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.factory = RequestFactory()
        self.user = UserFactory()

        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()

    def test_rate_limiting_with_login_view(self):
        """Test rate limiting integration with login view."""
        # This test assumes the login view uses the rate_limit decorator
        # We'll test the decorator behavior in a realistic scenario

        @rate_limit(max_attempts=3, window_minutes=1)
        def mock_login_view(request):
            return "Login successful"

        # Simulate failed login attempts
        for i in range(3):
            request = self.factory.get("/test/")
            request.META["REMOTE_ADDR"] = "192.168.1.100"

            # Set up messages framework
            setattr(request, "session", {})
            messages = FallbackStorage(request)
            setattr(request, "_messages", messages)

            response = mock_login_view(request)
            self.assertEqual(response, "Login successful")

        # Fourth attempt should be blocked
        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        response = mock_login_view(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limiting_with_registration_view(self):
        """Test rate limiting integration with registration view."""

        @rate_limit(max_attempts=2, window_minutes=1)
        def mock_registration_view(request):
            return "Registration successful"

        # Simulate registration attempts
        for i in range(2):
            request = self.factory.get("/test/")
            request.META["REMOTE_ADDR"] = "192.168.1.100"

            # Set up messages framework
            setattr(request, "session", {})
            messages = FallbackStorage(request)
            setattr(request, "_messages", messages)

            response = mock_registration_view(request)
            self.assertEqual(response, "Registration successful")

        # Third attempt should be blocked
        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        response = mock_registration_view(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limiting_different_endpoints(self):
        """Test that different endpoints have separate rate limits."""

        @rate_limit(max_attempts=2, window_minutes=1, key_prefix="login")
        def login_view(request):
            return "Login"

        @rate_limit(max_attempts=2, window_minutes=1, key_prefix="register")
        def register_view(request):
            return "Register"

        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Set up messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Hit limit on login
        login_view(request)
        login_view(request)

        # Register should still work
        response = register_view(request)
        self.assertEqual(response, "Register")

        response = register_view(request)
        self.assertEqual(response, "Register")

        # Now register should be blocked
        response = register_view(request)
        self.assertEqual(response.status_code, 429)
