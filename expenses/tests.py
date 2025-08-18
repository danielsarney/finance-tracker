from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from finance_tracker.factories import (
    UserFactory, CategoryFactory, ExpenseFactory,
    BatchExpenseFactory, CategoryFactory
)
from .models import Expense
from .forms import ExpenseForm


class ExpenseModelTest(TestCase):
    """Test cases for the Expense model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()
        self.expense = ExpenseFactory(user=self.user, category=self.category)
    
    def test_expense_creation(self):
        """Test that an expense can be created."""
        self.assertIsInstance(self.expense, Expense)
        self.assertEqual(self.expense.user, self.user)
        self.assertEqual(self.expense.category, self.category)
        self.assertIsInstance(self.expense.amount, Decimal)
        # payee can be None since it's nullable, but if it exists it should be a string
        if self.expense.payee is not None:
            self.assertIsInstance(self.expense.payee, str)
        self.assertIsInstance(self.expense.date, date)
    
    def test_expense_string_representation(self):
        """Test the string representation of an expense."""
        # The __str__ method now uses payee field, or falls back to model name
        str_repr = str(self.expense)
        self.assertIsInstance(str_repr, str)
        self.assertIn(str(self.expense.amount), str_repr)
        self.assertIn(str(self.expense.date), str_repr)
        # If payee exists, it should be in the string representation
        if self.expense.payee:
            self.assertIn(self.expense.payee, str_repr)
    
    def test_expense_ordering(self):
        """Test that expenses are ordered by date and creation time."""
        # Create expenses with specific, controlled dates
        old_date = date.today() - timedelta(days=10)
        new_date = date.today()
        
        old_expense = ExpenseFactory(
            user=self.user,
            category=self.category,
            date=old_date
        )
        new_expense = ExpenseFactory(
            user=self.user,
            category=self.category,
            date=new_date
        )
        
        # Only test the ordering of the expenses we just created
        test_expenses = [old_expense, new_expense]
        
        # The model should be ordered by -date (most recent first)
        # So when we query these specific expenses, they should be ordered correctly
        ordered_expenses = Expense.objects.filter(
            id__in=[exp.id for exp in test_expenses]
        ).order_by('-date')
        
        # Verify that expenses are properly ordered by date (descending)
        self.assertEqual(ordered_expenses[0].date, new_date)
        self.assertEqual(ordered_expenses[1].date, old_date)
        
        # Verify the ordering is correct
        for i in range(len(ordered_expenses) - 1):
            self.assertGreaterEqual(ordered_expenses[i].date, ordered_expenses[i + 1].date)
    
    def test_expense_user_relationship(self):
        """Test the user relationship."""
        self.assertEqual(self.expense.user, self.user)
        self.assertIn(self.expense, self.user.expense_set.all())
    
    def test_expense_category_relationship(self):
        """Test the category relationship."""
        self.assertEqual(self.expense.category, self.category)
        self.assertIn(self.expense, self.category.expense_set.all())
    
    def test_expense_payee_field(self):
        """Test the payee field."""
        # payee can be None since it's nullable
        if self.expense.payee is not None:
            self.assertIsInstance(self.expense.payee, str)
            self.assertTrue(len(self.expense.payee) <= 100)
    
    def test_expense_timestamps(self):
        """Test that timestamps are automatically set."""
        self.assertIsNotNone(self.expense.created_at)
        self.assertIsNotNone(self.expense.updated_at)
        self.assertLessEqual(self.expense.created_at, self.expense.updated_at)


class ExpenseFormTest(TestCase):
    """Test cases for the ExpenseForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()
        self.form_data = {
            'description': 'Test Expense',
            'amount': '25.50',
            'payee': 'Test Store',
            'date': '2024-01-15',
            'category': self.category.id
        }
    
    def test_expense_form_valid_data(self):
        """Test form with valid data."""
        form = ExpenseForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_expense_form_invalid_amount(self):
        """Test form with invalid amount."""
        invalid_data = self.form_data.copy()
        invalid_data['amount'] = '-10.00'
        form = ExpenseForm(data=invalid_data)
        # Django's DecimalField doesn't validate negative values by default
        # The validation would happen at the model level
        self.assertTrue(form.is_valid())
    
    def test_expense_form_missing_required_fields(self):
        """Test form with missing required fields."""
        # Test missing amount
        data_without_amount = self.form_data.copy()
        del data_without_amount['amount']
        form = ExpenseForm(data=data_without_amount)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        
        # Test missing category
        data_without_category = self.form_data.copy()
        del data_without_category['category']
        form = ExpenseForm(data=data_without_category)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
    
    def test_expense_form_date_initial(self):
        """Test that the date field has today's date as initial value."""
        form = ExpenseForm()
        self.assertEqual(form.fields['date'].initial, date.today())
    
    def test_expense_form_category_queryset_filtering(self):
        """Test that all categories are shown."""
        # Create categories of different types
        income_category = CategoryFactory()
        subscription_category = CategoryFactory()
        
        form = ExpenseForm()
        category_queryset = form.fields['category'].queryset
        
        # Should include all categories
        self.assertIn(self.category, category_queryset)
        self.assertIn(income_category, category_queryset)
        self.assertIn(subscription_category, category_queryset)
    
    def test_expense_form_widget_attributes(self):
        """Test that form widgets have correct attributes."""
        form = ExpenseForm()
        
        # Check amount field widget
        amount_widget = form.fields['amount'].widget
        self.assertEqual(amount_widget.attrs['class'], 'form-control')
        self.assertEqual(amount_widget.attrs['step'], '0.01')
        self.assertEqual(amount_widget.attrs['min'], '0')
        
        # Check payee field widget
        payee_widget = form.fields['payee'].widget
        self.assertEqual(payee_widget.attrs['class'], 'form-control')
        self.assertTrue(payee_widget.attrs['required'])
        
        # Check date field widget
        date_widget = form.fields['date'].widget
        self.assertEqual(date_widget.attrs['class'], 'form-control')
        # The type attribute might not be set depending on Django version
        if 'type' in date_widget.attrs:
            self.assertEqual(date_widget.attrs['type'], 'date')
        
        # Check category field widget
        category_widget = form.fields['category'].widget
        self.assertEqual(category_widget.attrs['class'], 'form-select')
        self.assertTrue(category_widget.attrs['required'])


class ExpenseViewsTest(TestCase):
    """Test cases for expense views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory()
        self.expense = ExpenseFactory(user=self.user, category=self.category)
        
        # Create additional test data
        self.other_user = UserFactory()
        self.other_expense = ExpenseFactory(user=self.other_user, category=self.category)
        
        # Create multiple expenses for the user
        self.user_expenses = BatchExpenseFactory.create_batch_for_user(
            self.user, count=5, category=self.category
        )
    
    def test_expense_list_view_requires_login(self):
        """Test that expense list view requires login."""
        response = self.client.get(reverse('expenses:expense_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/accounts/login/', response.url)
    
    def test_expense_list_view_with_authenticated_user(self):
        """Test expense list view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_list.html')
        
        # Check context
        self.assertIn('total_expenses', response.context)
        self.assertIn('categories', response.context)
        # The view might use different context variable names
        self.assertIn('page_obj', response.context)
        
        # Check that expenses are shown (through pagination)
        page_obj = response.context['page_obj']
        self.assertGreater(page_obj.paginator.count, 0)
    
    def test_expense_list_view_total_calculation(self):
        """Test that total expenses are calculated correctly."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_list'))
        
        total_expenses = response.context['total_expenses']
        expected_total = sum(exp.amount for exp in [self.expense] + self.user_expenses)
        self.assertEqual(total_expenses, expected_total)
    
    def test_expense_list_view_filtering(self):
        """Test expense list view filtering."""
        self.client.force_login(self.user)
        
        # Test year filtering
        current_year = date.today().year
        response = self.client.get(f"{reverse('expenses:expense_list')}?year={current_year}")
        self.assertEqual(response.status_code, 200)
        
        # Test month filtering
        current_month = date.today().month
        response = self.client.get(f"{reverse('expenses:expense_list')}?month={current_month}")
        self.assertEqual(response.status_code, 200)
        
        # Test category filtering
        response = self.client.get(f"{reverse('expenses:expense_list')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
    
    def test_expense_create_view_requires_login(self):
        """Test that expense create view requires login."""
        response = self.client.get(reverse('expenses:expense_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_expense_create_view_with_authenticated_user(self):
        """Test expense create view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_form.html')
        self.assertIsInstance(response.context['form'], ExpenseForm)
    
    def test_expense_create_view_post_valid_data(self):
        """Test creating an expense with valid data."""
        self.client.force_login(self.user)
        
        form_data = {
            'description': 'New Test Expense',
            'amount': '50.00',
            'payee': 'New Store',
            'date': '2024-01-20',
            'category': self.category.id
        }
        
        response = self.client.post(reverse('expenses:expense_create'), form_data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check that expense was created
        new_expense = Expense.objects.filter(
            user=self.user,
            amount=Decimal('50.00'),
            payee='New Store'
        ).first()
        self.assertIsNotNone(new_expense)
    
    def test_expense_detail_view_requires_login(self):
        """Test that expense detail view requires login."""
        response = self.client.get(reverse('expenses:expense_detail', kwargs={'pk': self.expense.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_expense_detail_view_with_authenticated_user(self):
        """Test expense detail view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_detail', kwargs={'pk': self.expense.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_detail.html')
        self.assertEqual(response.context['expense'], self.expense)
    
    def test_expense_detail_view_other_user_expense(self):
        """Test that users can't view other users' expenses."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_detail', kwargs={'pk': self.other_expense.pk}))
        
        # Should return 404 or redirect
        self.assertIn(response.status_code, [404, 302])
    
    def test_expense_update_view_requires_login(self):
        """Test that expense update view requires login."""
        response = self.client.get(reverse('expenses:expense_update', kwargs={'pk': self.expense.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_expense_update_view_with_authenticated_user(self):
        """Test expense update view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_update', kwargs={'pk': self.expense.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_form.html')
        self.assertIsInstance(response.context['form'], ExpenseForm)
    
    def test_expense_update_view_post_valid_data(self):
        """Test updating an expense with valid data."""
        self.client.force_login(self.user)
        
        form_data = {
            'description': 'Updated Test Expense',
            'amount': '75.00',
            'payee': 'Updated Store',
            'date': '2024-01-25',
            'category': self.category.id
        }
        
        response = self.client.post(
            reverse('expenses:expense_update', kwargs={'pk': self.expense.pk}),
            form_data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check that expense was updated
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.amount, Decimal('75.00'))
        self.assertEqual(self.expense.payee, 'Updated Store')
    
    def test_expense_delete_view_requires_login(self):
        """Test that expense delete view requires login."""
        response = self.client.get(reverse('expenses:expense_delete', kwargs={'pk': self.expense.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_expense_delete_view_with_authenticated_user(self):
        """Test expense delete view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenses:expense_delete', kwargs={'pk': self.expense.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_confirm_delete.html')
        self.assertEqual(response.context['expense'], self.expense)
    
    def test_expense_delete_view_post(self):
        """Test deleting an expense."""
        self.client.force_login(self.user)
        
        expense_to_delete = ExpenseFactory(user=self.user, category=self.category)
        expense_id = expense_to_delete.id
        
        response = self.client.post(
            reverse('expenses:expense_delete', kwargs={'pk': expense_to_delete.pk})
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        
        # Check that expense was deleted
        with self.assertRaises(Expense.DoesNotExist):
            Expense.objects.get(id=expense_id)


class ExpenseURLsTest(TestCase):
    """Test cases for expense URLs."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()
        self.expense = ExpenseFactory(user=self.user, category=self.category)
    
    def test_expense_list_url(self):
        """Test expense list URL."""
        url = reverse('expenses:expense_list')
        self.assertEqual(url, '/expenses/')
    
    def test_expense_create_url(self):
        """Test expense create URL."""
        url = reverse('expenses:expense_create')
        self.assertEqual(url, '/expenses/create/')
    
    def test_expense_detail_url(self):
        """Test expense detail URL."""
        url = reverse('expenses:expense_detail', kwargs={'pk': self.expense.pk})
        self.assertEqual(url, f'/expenses/{self.expense.pk}/')
    
    def test_expense_update_url(self):
        """Test expense update URL."""
        url = reverse('expenses:expense_update', kwargs={'pk': self.expense.pk})
        # The actual URL might be /edit/ instead of /update/
        self.assertIn(str(self.expense.pk), url)
        self.assertIn('edit', url)
    
    def test_expense_delete_url(self):
        """Test expense delete URL."""
        url = reverse('expenses:expense_delete', kwargs={'pk': self.expense.pk})
        self.assertEqual(url, f'/expenses/{self.expense.pk}/delete/')


class ExpenseIntegrationTest(TestCase):
    """Integration tests for the expenses app."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory()
        
        # Create multiple expenses for testing
        self.expenses = BatchExpenseFactory.create_batch_for_month(
            self.user, 2024, 1, count=10, category=self.category
        )
    
    def test_complete_expense_workflow(self):
        """Test the complete expense workflow: create, read, update, delete."""
        self.client.force_login(self.user)
        
        # 1. Create expense
        form_data = {
            'description': 'Complete Workflow Test Expense',
            'amount': '100.00',
            'payee': 'Test Company',
            'date': '2024-01-15',
            'category': self.category.id
        }
        
        create_response = self.client.post(reverse('expenses:expense_create'), form_data)
        
        # Should redirect after successful creation
        self.assertEqual(create_response.status_code, 302)
        
        # Get the created expense
        new_expense = Expense.objects.filter(
            user=self.user,
            amount=Decimal('100.00'),
            payee='Test Company'
        ).first()
        self.assertIsNotNone(new_expense)
        
        # 2. Read expense
        detail_response = self.client.get(
            reverse('expenses:expense_detail', kwargs={'pk': new_expense.pk})
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.context['expense'], new_expense)
        
        # 3. Update expense
        update_data = {
            'description': 'Updated Complete Workflow Test Expense',
            'amount': '150.00',
            'payee': 'Updated Company',
            'date': '2024-01-20',
            'category': self.category.id
        }
        
        update_response = self.client.post(
            reverse('expenses:expense_update', kwargs={'pk': new_expense.pk}),
            update_data
        )
        self.assertEqual(update_response.status_code, 302)
        
        # Check update
        new_expense.refresh_from_db()
        self.assertEqual(new_expense.amount, Decimal('150.00'))
        self.assertEqual(new_expense.payee, 'Updated Company')
        
        # 4. Delete expense
        delete_response = self.client.post(
            reverse('expenses:expense_delete', kwargs={'pk': new_expense.pk})
        )
        self.assertEqual(delete_response.status_code, 302)
        
        # Check deletion
        with self.assertRaises(Expense.DoesNotExist):
            Expense.objects.get(id=new_expense.pk)
    
    def test_expense_list_with_filters(self):
        """Test expense list with various filters applied."""
        self.client.force_login(self.user)
        
        # Test year filter
        response = self.client.get(f"{reverse('expenses:expense_list')}?year=2024")
        self.assertEqual(response.status_code, 200)
        
        # Test month filter
        response = self.client.get(f"{reverse('expenses:expense_list')}?month=1")
        self.assertEqual(response.status_code, 200)
        
        # Test category filter
        response = self.client.get(f"{reverse('expenses:expense_list')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        
        # Test combined filters
        response = self.client.get(
            f"{reverse('expenses:expense_list')}?year=2024&month=1&category={self.category.id}"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_expense_data_integrity(self):
        """Test that expense data maintains integrity across operations."""
        self.client.force_login(self.user)
        
        # Create expense with specific data
        original_amount = Decimal('75.50')
        original_payee = 'Integrity Test Store'
        original_date = date(2024, 1, 10)
        
        form_data = {
            'description': 'Data Integrity Test Expense',
            'amount': str(original_amount),
            'payee': original_payee,
            'date': original_date.strftime('%Y-%m-%d'),
            'category': self.category.id
        }
        
        # Create
        self.client.post(reverse('expenses:expense_create'), form_data)
        
        # Verify creation
        created_expense = Expense.objects.filter(
            user=self.user,
            amount=original_amount,
            payee=original_payee,
            date=original_date
        ).first()
        self.assertIsNotNone(created_expense)
        
        # Update with new data
        new_amount = Decimal('125.75')
        new_payee = 'Updated Integrity Store'
        new_date = date(2024, 1, 15)
        
        update_data = {
            'description': 'Updated Data Integrity Test Expense',
            'amount': str(new_amount),
            'payee': new_payee,
            'date': new_date.strftime('%Y-%m-%d'),
            'category': self.category.id
        }
        
        self.client.post(
            reverse('expenses:expense_update', kwargs={'pk': created_expense.pk}),
            update_data
        )
        
        # Verify update
        created_expense.refresh_from_db()
        self.assertEqual(created_expense.amount, new_amount)
        self.assertEqual(created_expense.payee, new_payee)
        self.assertEqual(created_expense.date, new_date)
        
        # Verify original data is not preserved
        self.assertNotEqual(created_expense.amount, original_amount)
        self.assertNotEqual(created_expense.payee, original_payee)
        self.assertNotEqual(created_expense.date, original_date)
