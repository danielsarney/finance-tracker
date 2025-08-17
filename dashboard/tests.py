from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date
from .models import FinancialSummary
from finance_tracker.factories import (
    UserFactory, CategoryFactory, ExpenseFactory, IncomeFactory, 
    SubscriptionFactory, WorkLogFactory
)


class FinancialSummaryModelTest(TestCase):
    """Test cases for FinancialSummary model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.financial_summary = FinancialSummary.objects.create(
            user=self.user,
            month=6,
            year=2024,
            total_income=Decimal('5000.00'),
            total_expenses=Decimal('3000.00'),
            total_subscriptions=Decimal('200.00'),
            total_work_income=Decimal('1000.00')
        )
    
    def test_financial_summary_creation(self):
        """Test that a financial summary can be created."""
        self.assertIsInstance(self.financial_summary, FinancialSummary)
        self.assertEqual(self.financial_summary.user, self.user)
        self.assertEqual(self.financial_summary.month, 6)
        self.assertEqual(self.financial_summary.year, 2024)
    
    def test_financial_summary_string_representation(self):
        """Test the string representation of a financial summary."""
        expected = f"{self.user.username} - 6/2024"
        self.assertEqual(str(self.financial_summary), expected)
    
    def test_financial_summary_meta_options(self):
        """Test financial summary meta options."""
        self.assertEqual(FinancialSummary._meta.verbose_name, "Financial Summary")
        self.assertEqual(FinancialSummary._meta.verbose_name_plural, "Financial Summaries")
        self.assertEqual(FinancialSummary._meta.ordering, ['-year', '-month'])
    
    def test_financial_summary_unique_together(self):
        """Test that user, month, and year combination must be unique."""
        # Try to create another summary with same user, month, year
        with self.assertRaises(Exception):  # Should raise IntegrityError
            FinancialSummary.objects.create(
                user=self.user,
                month=6,
                year=2024,
                total_income=Decimal('1000.00'),
                total_expenses=Decimal('500.00')
            )
    
    def test_net_income_calculation(self):
        """Test that net income is automatically calculated."""
        self.assertEqual(self.financial_summary.net_income, Decimal('2000.00'))
    
    def test_net_income_update_on_save(self):
        """Test that net income updates when totals change."""
        self.financial_summary.total_income = Decimal('6000.00')
        self.financial_summary.save()
        self.assertEqual(self.financial_summary.net_income, Decimal('3000.00'))
    
    def test_financial_summary_defaults(self):
        """Test financial summary default values."""
        summary = FinancialSummary.objects.create(
            user=self.user,
            month=7,
            year=2024
        )
        self.assertEqual(summary.total_income, Decimal('0.00'))
        self.assertEqual(summary.total_expenses, Decimal('0.00'))
        self.assertEqual(summary.net_income, Decimal('0.00'))
        self.assertEqual(summary.total_subscriptions, Decimal('0.00'))
        self.assertEqual(summary.total_work_income, Decimal('0.00'))
        self.assertIsNotNone(summary.created_at)
        self.assertIsNotNone(summary.updated_at)
    
    def test_financial_summary_ordering(self):
        """Test that financial summaries are ordered correctly."""
        # Create summaries in different order
        summary1 = FinancialSummary.objects.create(
            user=self.user, month=1, year=2024, total_income=Decimal('1000.00'), total_expenses=Decimal('0.00')
        )
        summary2 = FinancialSummary.objects.create(
            user=self.user, month=12, year=2023, total_income=Decimal('1000.00'), total_expenses=Decimal('0.00')
        )
        summary3 = FinancialSummary.objects.create(
            user=self.user, month=5, year=2024, total_income=Decimal('1000.00'), total_expenses=Decimal('0.00')
        )
        
        # Get all summaries for this user
        summaries = FinancialSummary.objects.filter(user=self.user)
        
        # Should be ordered by year desc, month desc
        # setUp creates month 6, year 2024, so ordering should be: 6/2024, 5/2024, 1/2024, 12/2023
        self.assertEqual(summaries[0], self.financial_summary)  # 6/2024 (from setUp)
        self.assertEqual(summaries[1], summary3)  # 5/2024
        self.assertEqual(summaries[2], summary1)  # 1/2024
        self.assertEqual(summaries[3], summary2)  # 12/2023


class DashboardViewTest(TestCase):
    """Test cases for Dashboard views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create categories
        self.expense_category = CategoryFactory(category_type='expense')
        self.income_category = CategoryFactory(category_type='income')
        self.subscription_category = CategoryFactory(category_type='subscription')
        self.work_category = CategoryFactory(category_type='work')
        
        # Create test data for current month
        current_date = timezone.now().date()
        self.current_month = current_date.month
        self.current_year = current_date.year
        
        # Create expenses for current month
        self.expense1 = ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            date=current_date
        )
        self.expense2 = ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('200.00'),
            date=current_date
        )
        
        # Create income for current month
        self.income1 = IncomeFactory(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=current_date
        )
        
        # Create subscription
        self.subscription = SubscriptionFactory(
            user=self.user,
            category=self.subscription_category,
            amount=Decimal('50.00'),
            next_billing_date=timezone.now().date()
        )
        
        # Create work log
        self.work_log = WorkLogFactory(
            user=self.user,
            hours_worked=Decimal('8.0'),
            hourly_rate=Decimal('25.00'),
            work_date=current_date
        )
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated users."""
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
    
    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view redirects unauthenticated users."""
        self.client.logout()
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_context_data(self):
        """Test that dashboard view provides correct context data."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check required context variables
        required_context = [
            'current_month', 'current_year', 'month_names', 'years',
            'total_expenses', 'total_income', 'net_income',
            'total_subscription_cost', 'total_work_hours', 'total_work_earnings',
            'recent_expenses', 'recent_income', 'upcoming_renewals',
            'pending_work', 'active_subscriptions'
        ]
        
        for context_var in required_context:
            self.assertIn(context_var, response.context)
    
    def test_dashboard_current_month_calculations(self):
        """Test dashboard calculations for current month."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check calculations
        self.assertEqual(response.context['total_expenses'], Decimal('300.00'))
        self.assertEqual(response.context['total_income'], Decimal('1000.00'))
        self.assertEqual(response.context['net_income'], Decimal('700.00'))
        self.assertEqual(response.context['total_subscription_cost'], Decimal('50.00'))
        self.assertEqual(response.context['total_work_hours'], Decimal('8.0'))
        self.assertEqual(response.context['total_work_earnings'], Decimal('200.00'))
    
    def test_dashboard_month_year_filter(self):
        """Test dashboard filtering by specific month and year."""
        # Create data for a specific month/year
        specific_date = date(2023, 12, 15)
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('500.00'),
            date=specific_date
        )
        IncomeFactory(
            user=self.user,
            category=self.income_category,
            amount=Decimal('2000.00'),
            date=specific_date
        )
        
        # Filter by specific month/year
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '12',
            'year': '2023'
        })
        
        self.assertEqual(response.context['total_expenses'], Decimal('500.00'))
        self.assertEqual(response.context['total_income'], Decimal('2000.00'))
        self.assertEqual(response.context['net_income'], Decimal('1500.00'))
        self.assertEqual(response.context['current_month'], 12)
        self.assertEqual(response.context['current_year'], 2023)
    
    def test_dashboard_year_only_filter(self):
        """Test dashboard filtering by year only."""
        # Create data for a specific year
        jan_date = date(2023, 1, 15)
        feb_date = date(2023, 2, 15)
        
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            date=jan_date
        )
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('200.00'),
            date=feb_date
        )
        
        # Filter by year only
        response = self.client.get(reverse('dashboard:dashboard'), {
            'year': '2023'
        })
        
        self.assertEqual(response.context['total_expenses'], Decimal('300.00'))
        self.assertEqual(response.context['current_month'], None)
        self.assertEqual(response.context['current_year'], 2023)
    
    def test_dashboard_month_only_filter(self):
        """Test dashboard filtering by month only."""
        # Create data for January across different years
        jan_2023 = date(2023, 1, 15)
        jan_2024 = date(2024, 1, 15)
        
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('150.00'),
            date=jan_2023
        )
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('250.00'),
            date=jan_2024
        )
        
        # Filter by month only
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '1'
        })
        
        self.assertEqual(response.context['total_expenses'], Decimal('400.00'))
        self.assertEqual(response.context['current_month'], 1)
        self.assertEqual(response.context['current_year'], None)
    
    def test_dashboard_no_filters_defaults_to_current(self):
        """Test dashboard defaults to current month/year when no filters."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.context['current_month'], self.current_month)
        self.assertEqual(response.context['current_year'], self.current_year)
        self.assertEqual(response.context['selected_month'], None)
        self.assertEqual(response.context['selected_year'], None)
    
    def test_dashboard_recent_transactions(self):
        """Test that recent transactions are shown."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check recent transactions
        self.assertIn(self.expense1, response.context['recent_expenses'])
        self.assertIn(self.income1, response.context['recent_income'])
        
        # Should be limited to 5
        self.assertLessEqual(len(response.context['recent_expenses']), 5)
        self.assertLessEqual(len(response.context['recent_income']), 5)
    
    def test_dashboard_active_subscriptions(self):
        """Test that all subscriptions are shown (no is_active filter)."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertIn(self.subscription, response.context['active_subscriptions'])
        self.assertEqual(response.context['total_subscription_cost'], Decimal('50.00'))
    
    def test_dashboard_work_logs(self):
        """Test that work logs are calculated correctly."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.context['total_work_hours'], Decimal('8.0'))
        self.assertEqual(response.context['total_work_earnings'], Decimal('200.00'))
    
    def test_dashboard_years_list(self):
        """Test that years list is generated correctly."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        years = response.context['years']
        self.assertIn(2024, years)
        self.assertIn(2023, years)
        self.assertIn(2020, years)
        self.assertIn(2080, years)
    
    def test_dashboard_month_names(self):
        """Test that month names are provided."""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        month_names = response.context['month_names']
        expected_months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        self.assertEqual(month_names, expected_months)
    
    def test_dashboard_empty_data(self):
        """Test dashboard with no data."""
        # Create a new user with no data
        new_user = UserFactory()
        self.client.login(username=new_user.username, password='testpass123')
        
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_expenses'], 0)
        self.assertEqual(response.context['total_income'], 0)
        self.assertEqual(response.context['net_income'], 0)
        self.assertEqual(response.context['total_subscription_cost'], 0)
        self.assertEqual(response.context['total_work_hours'], 0)
        self.assertEqual(response.context['total_work_earnings'], 0)


class DashboardURLTest(TestCase):
    """Test cases for Dashboard URLs."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
    
    def test_dashboard_url(self):
        """Test dashboard URL."""
        url = reverse('dashboard:dashboard')
        self.assertEqual(url, '/')
    
    def test_dashboard_url_with_filters(self):
        """Test dashboard URL with query parameters."""
        url = reverse('dashboard:dashboard')
        # URL should accept query parameters
        self.assertEqual(url, '/')


class DashboardIntegrationTest(TestCase):
    """Integration tests for Dashboard functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create categories
        self.expense_category = CategoryFactory(category_type='expense')
        self.income_category = CategoryFactory(category_type='income')
        self.subscription_category = CategoryFactory(category_type='subscription')
        self.work_category = CategoryFactory(category_type='work')
    
    def test_dashboard_complete_workflow(self):
        """Test complete dashboard workflow with data creation and filtering."""
        # 1. Create financial data for different periods
        jan_2024 = date(2024, 1, 15)
        feb_2024 = date(2024, 2, 15)
        mar_2024 = date(2024, 3, 15)
        
        # January data
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            date=jan_2024
        )
        IncomeFactory(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=jan_2024
        )
        
        # February data
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('200.00'),
            date=feb_2024
        )
        IncomeFactory(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1500.00'),
            date=feb_2024
        )
        
        # March data
        ExpenseFactory(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('300.00'),
            date=mar_2024
        )
        IncomeFactory(
            user=self.user,
            category=self.income_category,
            amount=Decimal('2000.00'),
            date=mar_2024
        )
        
        # 2. Test January dashboard
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '1',
            'year': '2024'
        })
        self.assertEqual(response.context['total_expenses'], Decimal('100.00'))
        self.assertEqual(response.context['total_income'], Decimal('1000.00'))
        self.assertEqual(response.context['net_income'], Decimal('900.00'))
        
        # 3. Test February dashboard
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '2',
            'year': '2024'
        })
        self.assertEqual(response.context['total_expenses'], Decimal('200.00'))
        self.assertEqual(response.context['total_income'], Decimal('1500.00'))
        self.assertEqual(response.context['net_income'], Decimal('1300.00'))
        
        # 4. Test March dashboard
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '3',
            'year': '2024'
        })
        self.assertEqual(response.context['total_expenses'], Decimal('300.00'))
        self.assertEqual(response.context['total_income'], Decimal('2000.00'))
        self.assertEqual(response.context['net_income'], Decimal('1700.00'))
        
        # 5. Test year view (all months combined)
        response = self.client.get(reverse('dashboard:dashboard'), {
            'year': '2024'
        })
        self.assertEqual(response.context['total_expenses'], Decimal('600.00'))
        self.assertEqual(response.context['total_income'], Decimal('4500.00'))
        self.assertEqual(response.context['net_income'], Decimal('3900.00'))
    
    def test_dashboard_with_subscriptions_and_work(self):
        """Test dashboard with subscriptions and work logs."""
        # Create subscriptions
        subscription1 = SubscriptionFactory(
            user=self.user,
            category=self.subscription_category,
            amount=Decimal('25.00'),
            next_billing_date=timezone.now().date()
        )
        subscription2 = SubscriptionFactory(
            user=self.user,
            category=self.subscription_category,
            amount=Decimal('35.00'),
            next_billing_date=timezone.now().date()
        )
        
        # Create work logs
        work_date = date(2024, 4, 15)
        WorkLogFactory(
            user=self.user,
            hours_worked=Decimal('8.0'),
            hourly_rate=Decimal('30.00'),
            work_date=work_date
        )
        WorkLogFactory(
            user=self.user,
            hours_worked=Decimal('4.0'),
            hourly_rate=Decimal('30.00'),
            work_date=work_date
        )
        
        # Test dashboard with April data
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '4',
            'year': '2024'
        })
        
        # Check subscription totals
        self.assertEqual(response.context['total_subscription_cost'], Decimal('60.00'))
        
        # Check work totals
        self.assertEqual(response.context['total_work_hours'], Decimal('12.0'))
        self.assertEqual(response.context['total_work_earnings'], Decimal('360.00'))
    
    def test_dashboard_edge_cases(self):
        """Test dashboard edge cases and error handling."""
        # Test with invalid month
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '13',  # Invalid month
            'year': '2024'
        })
        self.assertEqual(response.status_code, 200)  # Should not crash
        
        # Test with invalid year
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': '1',
            'year': '9999'  # Invalid year
        })
        self.assertEqual(response.status_code, 200)  # Should not crash
        
        # Test with non-numeric values
        response = self.client.get(reverse('dashboard:dashboard'), {
            'month': 'abc',
            'year': 'def'
        })
        self.assertEqual(response.status_code, 200)  # Should not crash
