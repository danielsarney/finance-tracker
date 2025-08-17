from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date
from .utils import (
    get_years_list, format_currency, format_date, 
    calculate_monthly_cost, get_upcoming_dates, 
    get_status_color, paginate_queryset
)
from django.core.paginator import Paginator


class UtilsTestCase(TestCase):
    """Test cases for utility functions."""
    
    def test_get_years_list_default(self):
        """Test get_years_list with default start year."""
        years = get_years_list()
        current_year = timezone.now().year
        
        # Should start from 2020
        self.assertEqual(years[0], 2020)
        # Should include current year
        self.assertIn(current_year, years)
        # Should be sequential
        self.assertEqual(years, list(range(2020, current_year + 1)))
    
    def test_get_years_list_custom_start(self):
        """Test get_years_list with custom start year."""
        years = get_years_list(2022)
        current_year = timezone.now().year
        
        self.assertEqual(years[0], 2022)
        self.assertIn(current_year, years)
        self.assertEqual(years, list(range(2022, current_year + 1)))
    
    def test_format_currency_gbp(self):
        """Test format_currency with GBP."""
        amount = Decimal('123.45')
        formatted = format_currency(amount, 'GBP')
        self.assertEqual(formatted, '£123.45')
    
    def test_format_currency_usd(self):
        """Test format_currency with USD."""
        amount = Decimal('123.45')
        formatted = format_currency(amount, 'USD')
        self.assertEqual(formatted, '$123.45')
    
    def test_format_currency_eur(self):
        """Test format_currency with EUR."""
        amount = Decimal('123.45')
        formatted = format_currency(amount, 'EUR')
        self.assertEqual(formatted, '€123.45')
    
    def test_format_currency_none(self):
        """Test format_currency with None."""
        formatted = format_currency(None)
        self.assertEqual(formatted, '£0.00')
    
    def test_format_currency_string_input(self):
        """Test format_currency with string input."""
        formatted = format_currency('123.45')
        self.assertEqual(formatted, '£123.45')
    
    def test_format_date_short(self):
        """Test format_date with short format."""
        test_date = date(2023, 12, 25)
        formatted = format_date(test_date, 'short')
        self.assertEqual(formatted, '25/12/2023')
    
    def test_format_date_long(self):
        """Test format_date with long format."""
        test_date = date(2023, 12, 25)
        formatted = format_date(test_date, 'long')
        self.assertEqual(formatted, '25 December 2023')
    
    def test_format_date_iso(self):
        """Test format_date with ISO format."""
        test_date = date(2023, 12, 25)
        formatted = format_date(test_date, 'iso')
        self.assertEqual(formatted, '2023-12-25')
    
    def test_format_date_string_input(self):
        """Test format_date with string input."""
        formatted = format_date('2023-12-25')
        self.assertEqual(formatted, '25/12/2023')
    
    def test_format_date_none(self):
        """Test format_date with None."""
        formatted = format_date(None)
        self.assertEqual(formatted, '')
    
    def test_format_date_invalid_string(self):
        """Test format_date with invalid string."""
        formatted = format_date('invalid-date')
        self.assertEqual(formatted, 'invalid-date')
    
    def test_calculate_monthly_cost_daily(self):
        """Test calculate_monthly_cost with daily billing."""
        amount = Decimal('10.00')
        monthly_cost = calculate_monthly_cost(amount, 'DAILY')
        self.assertEqual(monthly_cost, Decimal('300.00'))
    
    def test_calculate_monthly_cost_weekly(self):
        """Test calculate_monthly_cost with weekly billing."""
        amount = Decimal('50.00')
        monthly_cost = calculate_monthly_cost(amount, 'WEEKLY')
        self.assertEqual(monthly_cost, Decimal('216.50'))
    
    def test_calculate_monthly_cost_monthly(self):
        """Test calculate_monthly_cost with monthly billing."""
        amount = Decimal('100.00')
        monthly_cost = calculate_monthly_cost(amount, 'MONTHLY')
        self.assertEqual(monthly_cost, Decimal('100.00'))
    
    def test_calculate_monthly_cost_quarterly(self):
        """Test calculate_monthly_cost with quarterly billing."""
        amount = Decimal('300.00')
        monthly_cost = calculate_monthly_cost(amount, 'QUARTERLY')
        self.assertEqual(monthly_cost, Decimal('100.00'))
    
    def test_calculate_monthly_cost_yearly(self):
        """Test calculate_monthly_cost with yearly billing."""
        amount = Decimal('1200.00')
        monthly_cost = calculate_monthly_cost(amount, 'YEARLY')
        self.assertEqual(monthly_cost, Decimal('100.00'))
    
    def test_calculate_monthly_cost_string_input(self):
        """Test calculate_monthly_cost with string input."""
        monthly_cost = calculate_monthly_cost('100.00', 'MONTHLY')
        self.assertEqual(monthly_cost, Decimal('100.00'))
    
    def test_get_upcoming_dates_daily(self):
        """Test get_upcoming_dates with daily billing."""
        start_date = date(2023, 1, 1)
        dates = get_upcoming_dates(start_date, 'DAILY', 3)
        
        expected_dates = [
            date(2023, 1, 1),
            date(2023, 1, 2),
            date(2023, 1, 3)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_get_upcoming_dates_weekly(self):
        """Test get_upcoming_dates with weekly billing."""
        start_date = date(2023, 1, 1)
        dates = get_upcoming_dates(start_date, 'WEEKLY', 3)
        
        expected_dates = [
            date(2023, 1, 1),
            date(2023, 1, 8),
            date(2023, 1, 15)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_get_upcoming_dates_monthly(self):
        """Test get_upcoming_dates with monthly billing."""
        start_date = date(2023, 1, 1)
        dates = get_upcoming_dates(start_date, 'MONTHLY', 3)
        
        expected_dates = [
            date(2023, 1, 1),
            date(2023, 2, 1),
            date(2023, 3, 1)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_get_upcoming_dates_string_input(self):
        """Test get_upcoming_dates with string input."""
        dates = get_upcoming_dates('2023-01-01', 'MONTHLY', 2)
        
        expected_dates = [
            date(2023, 1, 1),
            date(2023, 2, 1)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_get_status_color_pending(self):
        """Test get_status_color with PENDING status."""
        color = get_status_color('PENDING')
        self.assertEqual(color, 'warning')
    
    def test_get_status_color_invoiced(self):
        """Test get_status_color with INVOICED status."""
        color = get_status_color('INVOICED')
        self.assertEqual(color, 'info')
    
    def test_get_status_color_paid(self):
        """Test get_status_color with PAID status."""
        color = get_status_color('PAID')
        self.assertEqual(color, 'success')
    
    def test_get_status_color_unknown(self):
        """Test get_status_color with unknown status."""
        color = get_status_color('UNKNOWN_STATUS')
        self.assertEqual(color, 'secondary')
    
    def test_get_status_color_case_insensitive(self):
        """Test get_status_color is case insensitive."""
        color = get_status_color('pending')
        self.assertEqual(color, 'warning')
    
    def test_paginate_queryset(self):
        """Test paginate_queryset function."""
        # Create a mock queryset (list of numbers)
        queryset = list(range(100))
        paginator, page_obj = paginate_queryset(queryset, 1, 20)
        
        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(paginator.per_page, 20)
        self.assertEqual(len(page_obj), 20)
        self.assertEqual(page_obj.number, 1)
