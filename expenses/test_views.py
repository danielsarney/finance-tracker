from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from decimal import Decimal
from datetime import date
from .models import Expense
from .forms import ExpenseForm
from categories.models import Category


class ExpenseViewsTestCase(TestCase):
    """Test cases for expense views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Food',
            category_type='expense',
            color='#FF0000',
            icon='fas fa-utensils'
        )
        
        self.expense = Expense.objects.create(
            user=self.user,
            amount=Decimal('25.50'),
            description='Test Expense',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        self.factory = RequestFactory()
    
    def test_expense_list_view_authenticated(self):
        """Test expense list view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_list.html')
        self.assertContains(response, 'Test Expense')
    
    def test_expense_list_view_unauthenticated(self):
        """Test expense list view redirects unauthenticated users."""
        response = self.client.get(reverse('expenses:expense_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={reverse("expenses:expense_list")}')
    
    def test_expense_list_view_with_filters(self):
        """Test expense list view with various filters."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test month filter
        response = self.client.get(reverse('expenses:expense_list'), {'month': '12'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Expense')
        
        # Test year filter
        response = self.client.get(reverse('expenses:expense_list'), {'year': '2023'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Expense')
        
        # Test category filter
        response = self.client.get(reverse('expenses:expense_list'), {'category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Expense')
    
    def test_expense_list_view_context(self):
        """Test expense list view provides correct context."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_list'))
        
        # Check required context variables
        self.assertIn('page_obj', response.context)
        self.assertIn('total_expenses', response.context)
        self.assertIn('years', response.context)
        self.assertIn('categories', response.context)
        
        # Check total expenses calculation
        self.assertEqual(response.context['total_expenses'], Decimal('25.50'))
        
        # Check years list
        self.assertIsInstance(response.context['years'], list)
        self.assertGreater(len(response.context['years']), 0)
        
        # Check categories
        self.assertIn(self.category, response.context['categories'])
    
    def test_expense_create_view_get(self):
        """Test expense create view GET request."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_form.html')
        self.assertContains(response, 'Add New Expense')
    
    def test_expense_create_view_post_valid(self):
        """Test expense create view POST with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'amount': '50.00',
            'description': 'New Test Expense',
            'date': '2023-12-26',
            'category': self.category.id,
            'payee': 'Test Store',
            'is_taxable': False,
            'notes': 'Test notes'
        }
        
        response = self.client.post(reverse('expenses:expense_create'), data)
        
        # Should redirect to list view
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expenses:expense_list'))
        
        # Check expense was created
        new_expense = Expense.objects.get(description='New Test Expense')
        self.assertEqual(new_expense.amount, Decimal('50.00'))
        self.assertEqual(new_expense.user, self.user)
        self.assertEqual(new_expense.payee, 'Test Store')
        self.assertFalse(new_expense.is_taxable)
        self.assertEqual(new_expense.notes, 'Test notes')
    
    def test_expense_create_view_post_invalid(self):
        """Test expense create view POST with invalid data."""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'amount': 'invalid',
            'description': '',
            'date': 'invalid-date',
            'category': self.category.id
        }
        
        response = self.client.post(reverse('expenses:expense_create'), data)
        
        # Should return to form with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_form.html')
        
        # Check form errors
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('date', form.errors)
    
    def test_expense_update_view_get(self):
        """Test expense update view GET request."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_update', args=[self.expense.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_form.html')
        self.assertContains(response, 'Edit Expense')
        
        # Check form is pre-populated
        form = response.context['form']
        self.assertEqual(form.instance, self.expense)
    
    def test_expense_update_view_post_valid(self):
        """Test expense update view POST with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'amount': '75.00',
            'description': 'Updated Test Expense',
            'date': '2023-12-27',
            'category': self.category.id,
            'payee': 'Updated Store',
            'is_taxable': True,
            'notes': 'Updated notes'
        }
        
        response = self.client.post(reverse('expenses:expense_update', args=[self.expense.pk]), data)
        
        # Should redirect to list view
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expenses:expense_list'))
        
        # Check expense was updated
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.amount, Decimal('75.00'))
        self.assertEqual(self.expense.description, 'Updated Test Expense')
        self.assertEqual(self.expense.payee, 'Updated Store')
        self.assertTrue(self.expense.is_taxable)
        self.assertEqual(self.expense.notes, 'Updated notes')
    
    def test_expense_update_view_other_user(self):
        """Test expense update view prevents access to other user's expenses."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_update', args=[self.expense.pk]))
        
        # Should return 404 (expense not found for this user)
        self.assertEqual(response.status_code, 404)
    
    def test_expense_delete_view_get(self):
        """Test expense delete view GET request."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_delete', args=[self.expense.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_confirm_delete.html')
        self.assertContains(response, 'Test Expense')
    
    def test_expense_delete_view_post(self):
        """Test expense delete view POST request."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('expenses:expense_delete', args=[self.expense.pk]))
        
        # Should redirect to list view
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expenses:expense_list'))
        
        # Check expense was deleted
        self.assertFalse(Expense.objects.filter(pk=self.expense.pk).exists())
    
    def test_expense_delete_view_other_user(self):
        """Test expense delete view prevents access to other user's expenses."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(reverse('expenses:expense_delete', args=[self.expense.pk]))
        
        # Should return 404 (expense not found for this user)
        self.assertEqual(response.status_code, 404)
        
        # Expense should still exist
        self.assertTrue(Expense.objects.filter(pk=self.expense.pk).exists())
    
    def test_expense_detail_view(self):
        """Test expense detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_detail', args=[self.expense.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_detail.html')
        self.assertContains(response, 'Test Expense')
        self.assertContains(response, '25.50')
    
    def test_expense_detail_view_other_user(self):
        """Test expense detail view prevents access to other user's expenses."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('expenses:expense_detail', args=[self.expense.pk]))
        
        # Should return 404 (expense not found for this user)
        self.assertEqual(response.status_code, 404)
    
    def test_expense_list_pagination(self):
        """Test expense list view pagination."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create more expenses to test pagination
        for i in range(25):  # More than 20 (default page size)
            Expense.objects.create(
                user=self.user,
                amount=Decimal(f'{i}.00'),
                description=f'Expense {i}',
                date=date(2023, 12, 25),
                category=self.category
            )
        
        response = self.client.get(reverse('expenses:expense_list'))
        
        # Check pagination context
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        
        # Should have pagination
        self.assertTrue(page_obj.has_other_pages())
        self.assertEqual(len(page_obj), 20)  # First page should have 20 items
        
        # Test second page
        response = self.client.get(reverse('expenses:expense_list'), {'page': 2})
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.number, 2)
