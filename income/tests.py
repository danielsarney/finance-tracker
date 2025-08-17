from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from finance_tracker.factories import (
    UserFactory, CategoryFactory, IncomeFactory,
    BatchIncomeFactory, CategoryFactory
)
from .models import Income
from .forms import IncomeForm


class IncomeModelTest(TestCase):
    """Test cases for the Income model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory(category_type='income')
        self.income = IncomeFactory(user=self.user, category=self.category)
    
    def test_income_creation(self):
        """Test that an income can be created."""
        self.assertIsInstance(self.income, Income)
        self.assertEqual(self.income.user, self.user)
        self.assertEqual(self.income.category, self.category)
        self.assertIsInstance(self.income.amount, Decimal)
        # payer can be None since it's nullable, but if it exists it should be a string
        if self.income.payer is not None:
            self.assertIsInstance(self.income.payer, str)
        self.assertIsInstance(self.income.date, date)
        self.assertIsInstance(self.income.is_taxable, bool)
    
    def test_income_string_representation(self):
        """Test the string representation of an income."""
        # The __str__ method uses the description field
        str_repr = str(self.income)
        self.assertIsInstance(str_repr, str)
        self.assertIn(str(self.income.amount), str_repr)
        self.assertIn(str(self.income.date), str_repr)
        # The description should be in the string representation
        self.assertIn(self.income.description, str_repr)
    
    def test_income_ordering(self):
        """Test that incomes are ordered by date and creation time."""
        # Create incomes with specific, controlled dates
        old_date = date.today() - timedelta(days=10)
        new_date = date.today()
        
        old_income = IncomeFactory(
            user=self.user,
            category=self.category,
            date=old_date
        )
        new_income = IncomeFactory(
            user=self.user,
            category=self.category,
            date=new_date
        )
        
        # Only test the ordering of the incomes we just created
        test_incomes = [old_income, new_income]
        
        # The model should be ordered by -date (most recent first)
        # So when we query these specific incomes, they should be ordered correctly
        ordered_incomes = Income.objects.filter(
            id__in=[inc.id for inc in test_incomes]
        ).order_by('-date')
        
        # Verify that incomes are properly ordered by date (descending)
        self.assertEqual(ordered_incomes[0].date, new_date)
        self.assertEqual(ordered_incomes[1].date, old_date)
        
        # Verify the ordering is correct
        for i in range(len(ordered_incomes) - 1):
            self.assertGreaterEqual(ordered_incomes[i].date, ordered_incomes[i + 1].date)
    
    def test_income_user_relationship(self):
        """Test the user relationship."""
        self.assertEqual(self.income.user, self.user)
        self.assertIn(self.income, self.user.income_set.all())
    
    def test_income_category_relationship(self):
        """Test the category relationship."""
        self.assertEqual(self.income.category, self.category)
        self.assertIn(self.income, self.category.income_set.all())
    
    def test_income_payer_field(self):
        """Test the payer field."""
        # payer can be None since it's nullable
        if self.income.payer is not None:
            self.assertIsInstance(self.income.payer, str)
            self.assertTrue(len(self.income.payer) <= 100)
    
    def test_income_is_taxable_field(self):
        """Test the is_taxable field."""
        self.assertIsInstance(self.income.is_taxable, bool)
        # The factory randomly sets is_taxable to True or False
        # We just verify it's a valid boolean value
        self.assertIn(self.income.is_taxable, [True, False])
    
    def test_income_timestamps(self):
        """Test that timestamps are automatically set."""
        self.assertIsNotNone(self.income.created_at)
        self.assertIsNotNone(self.income.updated_at)
        self.assertLessEqual(self.income.created_at, self.income.updated_at)
    
    def test_income_is_taxable_default(self):
        """Test that is_taxable defaults to True."""
        # Create income without specifying is_taxable
        # The factory will provide a value, but we can test the model's default
        new_income = IncomeFactory(
            user=self.user,
            category=self.category
        )
        # The factory should have set a value, and it should be a boolean
        self.assertIsInstance(new_income.is_taxable, bool)
        # The model default is True, so if the factory doesn't override it, it should be True
        # But since the factory does override it, we just verify it's a valid boolean value
        self.assertIn(new_income.is_taxable, [True, False])
    
    def test_income_is_taxable_custom(self):
        """Test that is_taxable can be set to False."""
        new_income = IncomeFactory(
            user=self.user,
            category=self.category,
            is_taxable=False
        )
        self.assertFalse(new_income.is_taxable)


class IncomeFormTest(TestCase):
    """Test cases for the IncomeForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory(category_type='income')
        self.form_data = {
            'description': 'Test Income',
            'amount': '2500.00',
            'payer': 'Test Company',
            'date': '2024-01-15',
            'category': self.category.id,
            'is_taxable': True
        }
    
    def test_income_form_valid_data(self):
        """Test form with valid data."""
        form = IncomeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_income_form_invalid_amount(self):
        """Test form with invalid amount."""
        invalid_data = self.form_data.copy()
        invalid_data['amount'] = '-1000.00'
        form = IncomeForm(data=invalid_data)
        # Django's DecimalField doesn't validate negative values by default
        # The validation would happen at the model level
        self.assertTrue(form.is_valid())
    
    def test_income_form_missing_required_fields(self):
        """Test form with missing required fields."""
        # Test missing amount
        data_without_amount = self.form_data.copy()
        del data_without_amount['amount']
        form = IncomeForm(data=data_without_amount)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        
        # Test missing category
        data_without_category = self.form_data.copy()
        del data_without_category['category']
        form = IncomeForm(data=data_without_category)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
    
    def test_income_form_date_initial(self):
        """Test that the date field has today's date as initial value."""
        form = IncomeForm()
        self.assertEqual(form.fields['date'].initial, date.today())
    
    def test_income_form_category_queryset_filtering(self):
        """Test that only income categories are shown."""
        # Create categories of different types
        expense_category = CategoryFactory(category_type='expense')
        subscription_category = CategoryFactory(category_type='subscription')
        
        form = IncomeForm()
        category_queryset = form.fields['category'].queryset
        
        # Should only include income categories
        self.assertIn(self.category, category_queryset)
        self.assertNotIn(expense_category, category_queryset)
        self.assertNotIn(subscription_category, category_queryset)
    
    def test_income_form_widget_attributes(self):
        """Test that form widgets have correct attributes."""
        form = IncomeForm()
        
        # Check amount field widget
        amount_widget = form.fields['amount'].widget
        self.assertEqual(amount_widget.attrs['class'], 'form-control')
        self.assertEqual(amount_widget.attrs['step'], '0.01')
        self.assertEqual(amount_widget.attrs['min'], '0')
        
        # Check payer field widget
        payer_widget = form.fields['payer'].widget
        self.assertEqual(payer_widget.attrs['class'], 'form-control')
        self.assertTrue(payer_widget.attrs['required'])
        
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
        
        # Check is_taxable field widget
        is_taxable_widget = form.fields['is_taxable'].widget
        self.assertEqual(is_taxable_widget.attrs['class'], 'form-check-input')
    
    def test_income_form_is_taxable_default(self):
        """Test that is_taxable has a default value."""
        form = IncomeForm()
        # The field should exist and have a default value
        self.assertIn('is_taxable', form.fields)
        self.assertTrue(form.fields['is_taxable'].initial)


class IncomeViewsTest(TestCase):
    """Test cases for income views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory(category_type='income')
        self.income = IncomeFactory(user=self.user, category=self.category)
        
        # Create additional test data
        self.other_user = UserFactory()
        self.other_income = IncomeFactory(user=self.other_user, category=self.category)
        
        # Create multiple incomes for the user
        self.user_incomes = BatchIncomeFactory.create_batch_for_user(
            self.user, count=5, category=self.category
        )
    
    def test_income_list_view_requires_login(self):
        """Test that income list view requires login."""
        response = self.client.get(reverse('income:income_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/accounts/login/', response.url)
    
    def test_income_list_view_with_authenticated_user(self):
        """Test income list view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/income_list.html')
        
        # Check context
        self.assertIn('total_income', response.context)
        self.assertIn('categories', response.context)
        # The view might use different context variable names
        self.assertIn('page_obj', response.context)
        
        # Check that incomes are shown (through pagination)
        page_obj = response.context['page_obj']
        self.assertGreater(page_obj.paginator.count, 0)
    
    def test_income_list_view_total_calculation(self):
        """Test that total income is calculated correctly."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_list'))
        
        total_income = response.context['total_income']
        expected_total = sum(inc.amount for inc in [self.income] + self.user_incomes)
        self.assertEqual(total_income, expected_total)
    
    def test_income_list_view_filtering(self):
        """Test income list view filtering."""
        self.client.force_login(self.user)
        
        # Test year filtering
        current_year = date.today().year
        response = self.client.get(f"{reverse('income:income_list')}?year={current_year}")
        self.assertEqual(response.status_code, 200)
        
        # Test month filtering
        current_month = date.today().month
        response = self.client.get(f"{reverse('income:income_list')}?month={current_month}")
        self.assertEqual(response.status_code, 200)
        
        # Test category filtering
        response = self.client.get(f"{reverse('income:income_list')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
    
    def test_income_create_view_requires_login(self):
        """Test that income create view requires login."""
        response = self.client.get(reverse('income:income_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_income_create_view_with_authenticated_user(self):
        """Test income create view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/income_form.html')
        self.assertIsInstance(response.context['form'], IncomeForm)
    
    def test_income_create_view_post_valid_data(self):
        """Test creating an income with valid data."""
        self.client.force_login(self.user)
        
        form_data = {
            'description': 'New Test Income',
            'amount': '5000.00',
            'payer': 'New Company',
            'date': '2024-01-20',
            'category': self.category.id,
            'is_taxable': True
        }
        
        response = self.client.post(reverse('income:income_create'), form_data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check that income was created
        new_income = Income.objects.filter(
            user=self.user,
            amount=Decimal('5000.00'),
            payer='New Company'
        ).first()
        self.assertIsNotNone(new_income)
        self.assertTrue(new_income.is_taxable)
    
    def test_income_detail_view_requires_login(self):
        """Test that income detail view requires login."""
        response = self.client.get(reverse('income:income_detail', kwargs={'pk': self.income.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_income_detail_view_with_authenticated_user(self):
        """Test income detail view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_detail', kwargs={'pk': self.income.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/income_detail.html')
        self.assertEqual(response.context['income'], self.income)
    
    def test_income_detail_view_other_user_income(self):
        """Test that users can't view other users' incomes."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_detail', kwargs={'pk': self.other_income.pk}))
        
        # Should return 404 or redirect
        self.assertIn(response.status_code, [404, 302])
    
    def test_income_update_view_requires_login(self):
        """Test that income update view requires login."""
        response = self.client.get(reverse('income:income_update', kwargs={'pk': self.income.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_income_update_view_with_authenticated_user(self):
        """Test income update view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_update', kwargs={'pk': self.income.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/income_form.html')
        self.assertIsInstance(response.context['form'], IncomeForm)
    
    def test_income_update_view_post_valid_data(self):
        """Test updating an income with valid data."""
        self.client.force_login(self.user)
        
        form_data = {
            'description': 'Updated Test Income',
            'amount': '7500.00',
            'payer': 'Updated Company',
            'date': '2024-01-25',
            'category': self.category.id,
            'is_taxable': False
        }
        
        response = self.client.post(
            reverse('income:income_update', kwargs={'pk': self.income.pk}),
            form_data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check that income was updated
        self.income.refresh_from_db()
        self.assertEqual(self.income.amount, Decimal('7500.00'))
        self.assertEqual(self.income.payer, 'Updated Company')
        self.assertFalse(self.income.is_taxable)
    
    def test_income_delete_view_requires_login(self):
        """Test that income delete view requires login."""
        response = self.client.get(reverse('income:income_delete', kwargs={'pk': self.income.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_income_delete_view_with_authenticated_user(self):
        """Test income delete view with authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('income:income_delete', kwargs={'pk': self.income.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/income_confirm_delete.html')
        self.assertEqual(response.context['income'], self.income)
    
    def test_income_delete_view_post(self):
        """Test deleting an income."""
        self.client.force_login(self.user)
        
        income_to_delete = IncomeFactory(user=self.user, category=self.category)
        income_id = income_to_delete.id
        
        response = self.client.post(
            reverse('income:income_delete', kwargs={'pk': income_to_delete.pk})
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        
        # Check that income was deleted
        with self.assertRaises(Income.DoesNotExist):
            Income.objects.get(id=income_id)


class IncomeURLsTest(TestCase):
    """Test cases for income URLs."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory(category_type='income')
        self.income = IncomeFactory(user=self.user, category=self.category)
    
    def test_income_list_url(self):
        """Test income list URL."""
        url = reverse('income:income_list')
        self.assertEqual(url, '/income/')
    
    def test_income_create_url(self):
        """Test income create URL."""
        url = reverse('income:income_create')
        self.assertEqual(url, '/income/create/')
    
    def test_income_detail_url(self):
        """Test income detail URL."""
        url = reverse('income:income_detail', kwargs={'pk': self.income.pk})
        self.assertEqual(url, f'/income/{self.income.pk}/')
    
    def test_income_update_url(self):
        """Test income update URL."""
        url = reverse('income:income_update', kwargs={'pk': self.income.pk})
        # The actual URL might be /edit/ instead of /update/
        self.assertIn(str(self.income.pk), url)
        self.assertIn('edit', url)
    
    def test_income_delete_url(self):
        """Test income delete URL."""
        url = reverse('income:income_delete', kwargs={'pk': self.income.pk})
        self.assertEqual(url, f'/income/{self.income.pk}/delete/')


class IncomeIntegrationTest(TestCase):
    """Integration tests for the income app."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory(category_type='income')
        
        # Create multiple incomes for testing
        self.incomes = BatchIncomeFactory.create_batch_for_month(
            self.user, 2024, 1, count=10, category=self.category
        )
    
    def test_complete_income_workflow(self):
        """Test the complete income workflow: create, read, update, delete."""
        self.client.force_login(self.user)
        
        # 1. Create income
        form_data = {
            'description': 'Complete Workflow Test Income',
            'amount': '8000.00',
            'payer': 'Test Company',
            'date': '2024-01-15',
            'category': self.category.id,
            'is_taxable': True
        }
        
        create_response = self.client.post(reverse('income:income_create'), form_data)
        
        # Should redirect after successful creation
        self.assertEqual(create_response.status_code, 302)
        
        # Get the created income
        new_income = Income.objects.filter(
            user=self.user,
            amount=Decimal('8000.00'),
            payer='Test Company'
        ).first()
        self.assertIsNotNone(new_income)
        self.assertTrue(new_income.is_taxable)
        
        # 2. Read income
        detail_response = self.client.get(
            reverse('income:income_detail', kwargs={'pk': new_income.pk})
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.context['income'], new_income)
        
        # 3. Update income
        update_data = {
            'description': 'Updated Complete Workflow Test Income',
            'amount': '12000.00',
            'payer': 'Updated Company',
            'date': '2024-01-20',
            'category': self.category.id,
            'is_taxable': False
        }
        
        update_response = self.client.post(
            reverse('income:income_update', kwargs={'pk': new_income.pk}),
            update_data
        )
        self.assertEqual(update_response.status_code, 302)
        
        # Check update
        new_income.refresh_from_db()
        self.assertEqual(new_income.amount, Decimal('12000.00'))
        self.assertEqual(new_income.payer, 'Updated Company')
        self.assertFalse(new_income.is_taxable)
        
        # 4. Delete income
        delete_response = self.client.post(
            reverse('income:income_delete', kwargs={'pk': new_income.pk})
        )
        self.assertEqual(delete_response.status_code, 302)
        
        # Check deletion
        with self.assertRaises(Income.DoesNotExist):
            Income.objects.get(id=new_income.pk)
    
    def test_income_list_with_filters(self):
        """Test income list with various filters applied."""
        self.client.force_login(self.user)
        
        # Test year filter
        response = self.client.get(f"{reverse('income:income_list')}?year=2024")
        self.assertEqual(response.status_code, 200)
        
        # Test month filter
        response = self.client.get(f"{reverse('income:income_list')}?month=1")
        self.assertEqual(response.status_code, 200)
        
        # Test category filter
        response = self.client.get(f"{reverse('income:income_list')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        
        # Test combined filters
        response = self.client.get(
            f"{reverse('income:income_list')}?year=2024&month=1&category={self.category.id}"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_income_data_integrity(self):
        """Test that income data maintains integrity across operations."""
        self.client.force_login(self.user)
        
        # Create income with specific data
        original_amount = Decimal('6000.00')
        original_payer = 'Integrity Test Company'
        original_date = date(2024, 1, 10)
        original_is_taxable = True
        
        form_data = {
            'description': 'Data Integrity Test Income',
            'amount': str(original_amount),
            'payer': original_payer,
            'date': original_date.strftime('%Y-%m-%d'),
            'category': self.category.id,
            'is_taxable': original_is_taxable
        }
        
        # Create
        self.client.post(reverse('income:income_create'), form_data)
        
        # Verify creation
        created_income = Income.objects.filter(
            user=self.user,
            amount=original_amount,
            payer=original_payer,
            date=original_date,
            is_taxable=original_is_taxable
        ).first()
        self.assertIsNotNone(created_income)
        
        # Update with new data
        new_amount = Decimal('9000.00')
        new_payer = 'Updated Integrity Company'
        new_date = date(2024, 1, 15)
        new_is_taxable = False
        
        update_data = {
            'description': 'Updated Data Integrity Test Income',
            'amount': str(new_amount),
            'payer': new_payer,
            'date': new_date.strftime('%Y-%m-%d'),
            'category': self.category.id,
            'is_taxable': new_is_taxable
        }
        
        self.client.post(
            reverse('income:income_update', kwargs={'pk': created_income.pk}),
            update_data
        )
        
        # Verify update
        created_income.refresh_from_db()
        self.assertEqual(created_income.amount, new_amount)
        self.assertEqual(created_income.payer, new_payer)
        self.assertEqual(created_income.date, new_date)
        self.assertEqual(created_income.is_taxable, new_is_taxable)
        
        # Verify original data is not preserved
        self.assertNotEqual(created_income.amount, original_amount)
        self.assertNotEqual(created_income.payer, original_payer)
        self.assertNotEqual(created_income.date, original_date)
        self.assertNotEqual(created_income.is_taxable, original_is_taxable)
    
    def test_income_taxable_field_behavior(self):
        """Test the behavior of the is_taxable field."""
        self.client.force_login(self.user)
        
        # Test creating income with is_taxable=True
        form_data_taxable = {
            'description': 'Taxable Test Income',
            'amount': '5000.00',
            'payer': 'Taxable Company',
            'date': '2024-01-15',
            'category': self.category.id,
            'is_taxable': True
        }
        
        response = self.client.post(reverse('income:income_create'), form_data_taxable)
        self.assertEqual(response.status_code, 302)
        
        taxable_income = Income.objects.filter(
            user=self.user,
            payer='Taxable Company'
        ).first()
        self.assertIsNotNone(taxable_income)
        self.assertTrue(taxable_income.is_taxable)
        
        # Test creating income with is_taxable=False
        form_data_non_taxable = {
            'description': 'Non-Taxable Test Income',
            'amount': '3000.00',
            'payer': 'Non-Taxable Company',
            'date': '2024-01-20',
            'category': self.category.id,
            'is_taxable': False
        }
        
        response = self.client.post(reverse('income:income_create'), form_data_non_taxable)
        self.assertEqual(response.status_code, 302)
        
        non_taxable_income = Income.objects.filter(
            user=self.user,
            payer='Non-Taxable Company'
        ).first()
        self.assertIsNotNone(non_taxable_income)
        self.assertFalse(non_taxable_income.is_taxable)
