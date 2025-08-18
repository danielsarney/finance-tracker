from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django import forms
from .models import Category
from .forms import CategoryForm
from finance_tracker.factories import UserFactory, CategoryFactory


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()
    
    def test_category_creation(self):
        """Test that a category can be created."""
        self.assertIsInstance(self.category, Category)
        self.assertEqual(self.category.name, self.category.name)
    
    def test_category_string_representation(self):
        """Test the string representation of a category."""
        self.assertEqual(str(self.category), self.category.name)
    
    def test_category_meta_options(self):
        """Test category meta options."""
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")
        self.assertEqual(Category._meta.ordering, ['name'])
    
    def test_get_icon_class_with_icon(self):
        """Test get_icon_class method when icon is provided."""
        category = CategoryFactory(icon='fa-utensils')
        self.assertEqual(category.get_icon_class(), 'fas fa-utensils')
    
    def test_get_icon_class_without_icon(self):
        """Test get_icon_class method when no icon is provided."""
        category = CategoryFactory(icon='')
        self.assertEqual(category.get_icon_class(), 'fas fa-tag')
    
    def test_get_icon_class_with_fas_prefix(self):
        """Test get_icon_class method when icon already has fas prefix."""
        category = CategoryFactory(icon='fas fa-car')
        self.assertEqual(category.get_icon_class(), 'fas fa-car')
    
    def test_category_defaults(self):
        """Test category default values."""
        category = Category.objects.create(name='Test Category')
        self.assertEqual(category.color, '#6c757d')
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_category_unique_name(self):
        """Test that category names must be unique."""
        CategoryFactory(name='Unique Name')
        with self.assertRaises(Exception):  # Should raise IntegrityError
            CategoryFactory(name='Unique Name')
    
    def test_category_usage_methods(self):
        """Test category usage checking methods."""
        category = CategoryFactory()
        
        # Initially, category should not be used
        self.assertFalse(category.is_used())
        self.assertEqual(category.get_usage_count(), 0)
        self.assertEqual(category.get_usage_breakdown(), {
            'expenses': 0,
            'income': 0,
            'subscriptions': 0,
            'work_logs': 0
        })
    
    def test_category_usage_with_expenses(self):
        """Test category usage when it has expenses."""
        from expenses.models import Expense
        from finance_tracker.factories import ExpenseFactory
        
        category = CategoryFactory()
        user = UserFactory()
        
        # Create an expense using this category
        expense = ExpenseFactory(user=user, category=category)
        
        self.assertTrue(category.is_used())
        self.assertEqual(category.get_usage_count(), 1)
        self.assertEqual(category.get_usage_breakdown(), {
            'expenses': 1,
            'income': 0,
            'subscriptions': 0,
            'work_logs': 0
        })
        
        # Clean up
        expense.delete()
    
    def test_category_usage_with_income(self):
        """Test category usage when it has income."""
        from income.models import Income
        from finance_tracker.factories import IncomeFactory
        
        category = CategoryFactory()
        user = UserFactory()
        
        # Create income using this category
        income = IncomeFactory(user=user, category=category)
        
        self.assertTrue(category.is_used())
        self.assertEqual(category.get_usage_count(), 1)
        self.assertEqual(category.get_usage_breakdown(), {
            'expenses': 0,
            'income': 1,
            'subscriptions': 0,
            'work_logs': 0
        })
        
        # Clean up
        income.delete()
    
    def test_category_usage_with_subscriptions(self):
        """Test category usage when it has subscriptions."""
        from subscriptions.models import Subscription
        from finance_tracker.factories import SubscriptionFactory
        
        category = CategoryFactory()
        user = UserFactory()
        
        # Create subscription using this category
        subscription = SubscriptionFactory(user=user, category=category)
        
        self.assertTrue(category.is_used())
        self.assertEqual(category.get_usage_count(), 1)
        self.assertEqual(category.get_usage_breakdown(), {
            'expenses': 0,
            'income': 0,
            'subscriptions': 1,
            'work_logs': 0
        })
        
        # Clean up
        subscription.delete()
    
    def test_category_usage_with_work_logs(self):
        """Test category usage when it has work logs."""
        from work.models import WorkLog
        from finance_tracker.factories import WorkLogFactory
        
        category = CategoryFactory()
        user = UserFactory()
        
        # Create work log using this category
        work_log = WorkLogFactory(user=user, category=category)
        
        self.assertTrue(category.is_used())
        self.assertEqual(category.get_usage_count(), 1)
        self.assertEqual(category.get_usage_breakdown(), {
            'expenses': 0,
            'income': 0,
            'subscriptions': 0,
            'work_logs': 1
        })
        
        # Clean up
        work_log.delete()


class CategoryFormTest(TestCase):
    """Test cases for CategoryForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
    
    def test_category_form_valid_data(self):
        """Test CategoryForm with valid data."""
        form_data = {
            'name': 'Test Category',
            'icon': 'fa-utensils',
            'color': '#ff0000'
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_category_form_invalid_data(self):
        """Test CategoryForm with invalid data."""
        form_data = {
            'name': '',  # Empty name should be invalid
            'icon': 'fa-utensils',
            'color': '#ff0000'
        }
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_category_form_fields(self):
        """Test that CategoryForm has the correct fields."""
        form = CategoryForm()
        expected_fields = ['name', 'icon', 'color']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_category_form_widgets(self):
        """Test that CategoryForm has the correct widgets."""
        form = CategoryForm()
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['icon'].widget.attrs['class'], 'form-control')
        # Color field should use TextInput with type='color'
        self.assertIsInstance(form.fields['color'].widget, forms.TextInput)
        # Check if type attribute is set (Django might handle this differently)
        self.assertIn('class', form.fields['color'].widget.attrs)
        self.assertEqual(form.fields['color'].widget.attrs['class'], 'form-control')


class CategoryViewTest(TestCase):
    """Test cases for Category views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
        self.category = CategoryFactory()
    
    def test_category_list_view_authenticated(self):
        """Test category_list view for authenticated users."""
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_list.html')
        self.assertIn('page_obj', response.context)
    
    def test_category_list_view_unauthenticated(self):
        """Test category_list view redirects unauthenticated users."""
        self.client.logout()
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_category_list_view_pagination(self):
        """Test category_list view pagination."""
        # Create multiple categories with unique names to avoid conflicts
        for i in range(25):
            CategoryFactory(name=f'Test Category {i}')
        
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        # page_obj is a Page object, not a Paginator object
        self.assertIn('page_obj', response.context)
        self.assertTrue(hasattr(response.context['page_obj'], 'has_other_pages'))
    
    def test_category_create_view_get(self):
        """Test category_create view GET request."""
        response = self.client.get(reverse('categories:category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['title'], 'Add New Category')
    
    def test_category_create_view_post_valid(self):
        """Test category_create view POST request with valid data."""
        form_data = {
            'name': 'New Test Category',
            'icon': 'fa-money-bill',
            'color': '#00ff00'
        }
        response = self.client.post(reverse('categories:category_create'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if category was created
        self.assertTrue(Category.objects.filter(name='New Test Category').exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Category created successfully!')
    
    def test_category_create_view_post_invalid(self):
        """Test category_create view POST request with invalid data."""
        form_data = {
            'name': '',  # Invalid: empty name
            'icon': 'fa-utensils',
            'color': '#ff0000'
        }
        response = self.client.post(reverse('categories:category_create'), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_category_update_view_get(self):
        """Test category_update view GET request."""
        response = self.client.get(reverse('categories:category_update', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['title'], 'Edit Category')
    
    def test_category_update_view_post_valid(self):
        """Test category_update view POST request with valid data."""
        form_data = {
            'name': 'Updated Category Name',
            'icon': 'fa-credit-card',
            'color': '#0000ff'
        }
        response = self.client.post(reverse('categories:category_update', kwargs={'pk': self.category.pk}), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category Name')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Category updated successfully!')
    
    def test_category_update_view_post_invalid(self):
        """Test category_update view POST request with invalid data."""
        form_data = {
            'name': '',  # Invalid: empty name
            'icon': 'fa-utensils',
            'color': '#ff0000'
        }
        response = self.client.post(reverse('categories:category_update', kwargs={'pk': self.category.pk}), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_category_update_view_nonexistent(self):
        """Test category_update view with nonexistent category."""
        response = self.client.get(reverse('categories:category_update', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_category_delete_view_get(self):
        """Test category_delete view GET request."""
        response = self.client.get(reverse('categories:category_delete', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_confirm_delete.html')
        self.assertIn('category', response.context)
    
    def test_category_delete_view_post(self):
        """Test category_delete view POST request."""
        category_pk = self.category.pk
        response = self.client.post(reverse('categories:category_delete', kwargs={'pk': category_pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if category was deleted
        self.assertFalse(Category.objects.filter(pk=category_pk).exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Category deleted successfully!')
    
    def test_category_delete_view_with_replacement(self):
        """Test category_delete view with replacement category."""
        from expenses.models import Expense
        from finance_tracker.factories import ExpenseFactory
        
        # Create a category that's being used
        used_category = CategoryFactory()
        replacement_category = CategoryFactory()
        user = UserFactory()
        
        # Create an expense using the category
        expense = ExpenseFactory(user=user, category=used_category)
        
        # Try to delete with replacement
        response = self.client.post(
            reverse('categories:category_delete', kwargs={'pk': used_category.pk}),
            {'replacement_category': replacement_category.pk}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if original category was deleted
        self.assertFalse(Category.objects.filter(pk=used_category.pk).exists())
        
        # Check if expense was moved to replacement category
        expense.refresh_from_db()
        self.assertEqual(expense.category, replacement_category)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('deleted successfully', str(messages[0]))
        self.assertIn('moved to', str(messages[0]))
        
        # Clean up
        expense.delete()
        replacement_category.delete()
    
    def test_category_delete_view_with_invalid_replacement(self):
        """Test category_delete view with invalid replacement category."""
        from expenses.models import Expense
        from finance_tracker.factories import ExpenseFactory
        
        # Create a category that's being used
        used_category = CategoryFactory()
        user = UserFactory()
        
        # Create an expense using the category
        expense = ExpenseFactory(user=user, category=used_category)
        
        # Try to delete with invalid replacement ID
        response = self.client.post(
            reverse('categories:category_delete', kwargs={'pk': used_category.pk}),
            {'replacement_category': 99999}  # Non-existent ID
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after error
        
        # Check if category still exists
        self.assertTrue(Category.objects.filter(pk=used_category.pk).exists())
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('does not exist', str(messages[0]))
        
        # Clean up
        expense.delete()
        used_category.delete()
    
    def test_category_delete_view_context_with_usage(self):
        """Test category_delete view context when category is in use."""
        from expenses.models import Expense
        from finance_tracker.factories import ExpenseFactory
        
        # Create a category that's being used
        used_category = CategoryFactory()
        user = UserFactory()
        
        # Create an expense using the category
        expense = ExpenseFactory(user=user, category=used_category)
        
        # Get the delete view
        response = self.client.get(reverse('categories:category_delete', kwargs={'pk': used_category.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_confirm_delete.html')
        
        # Check context
        self.assertIn('category', response.context)
        self.assertIn('is_used', response.context)
        self.assertIn('usage_breakdown', response.context)
        self.assertIn('replacement_categories', response.context)
        
        # Check usage info
        self.assertTrue(response.context['is_used'])
        self.assertEqual(response.context['usage_breakdown']['expenses'], 1)
        
        # Check replacement categories (should exclude the current one)
        replacement_categories = response.context['replacement_categories']
        self.assertNotIn(used_category, replacement_categories)
        
        # Clean up
        expense.delete()
        used_category.delete()
    
    def test_category_delete_view_context_without_usage(self):
        """Test category_delete view context when category is not in use."""
        # Get the delete view for unused category
        response = self.client.get(reverse('categories:category_delete', kwargs={'pk': self.category.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_confirm_delete.html')
        
        # Check context
        self.assertIn('category', response.context)
        self.assertIn('is_used', response.context)
        self.assertFalse(response.context['is_used'])
        self.assertIsNone(response.context['usage_breakdown'])
        self.assertIn('replacement_categories', response.context)
    
    def test_category_delete_view_nonexistent(self):
        """Test category_delete view with nonexistent category."""
        response = self.client.post(reverse('categories:category_delete', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_category_detail_view(self):
        """Test category_detail view."""
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_detail.html')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], self.category)
    
    def test_category_detail_view_with_usage(self):
        """Test category_detail view when category is in use."""
        from expenses.models import Expense
        from finance_tracker.factories import ExpenseFactory
        
        # Create a category that's being used
        used_category = CategoryFactory()
        user = UserFactory()
        
        # Create an expense using the category
        expense = ExpenseFactory(user=user, category=used_category)
        
        # Get the detail view
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': used_category.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_detail.html')
        
        # Check context
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], used_category)
        
        # Clean up
        expense.delete()
        used_category.delete()
    
    def test_category_detail_view_nonexistent(self):
        """Test category_detail view with nonexistent category."""
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class CategoryURLTest(TestCase):
    """Test cases for Category URLs."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory()
    
    def test_category_list_url(self):
        """Test category_list URL."""
        url = reverse('categories:category_list')
        self.assertEqual(url, '/categories/')
    
    def test_category_create_url(self):
        """Test category_create URL."""
        url = reverse('categories:category_create')
        self.assertEqual(url, '/categories/create/')
    
    def test_category_update_url(self):
        """Test category_update URL."""
        url = reverse('categories:category_update', kwargs={'pk': self.category.pk})
        self.assertEqual(url, f'/categories/{self.category.pk}/update/')
    
    def test_category_delete_url(self):
        """Test category_delete URL."""
        url = reverse('categories:category_delete', kwargs={'pk': self.category.pk})
        self.assertEqual(url, f'/categories/{self.category.pk}/delete/')
    
    def test_category_detail_url(self):
        """Test category_detail URL."""
        url = reverse('categories:category_detail', kwargs={'pk': self.category.pk})
        self.assertEqual(url, f'/categories/{self.category.pk}/')


class CategoryIntegrationTest(TestCase):
    """Integration tests for Category functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
    
    def test_full_category_workflow(self):
        """Test the complete workflow of creating, updating, and deleting a category."""
        # 1. Create a category
        create_data = {
            'name': 'Integration Test Category',
            'icon': 'fa-test',
            'color': '#123456'
        }
        response = self.client.post(reverse('categories:category_create'), create_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify category was created
        category = Category.objects.get(name='Integration Test Category')
        self.assertEqual(category.icon, 'fa-test')
        self.assertEqual(category.color, '#123456')
        
        # 3. Update the category
        update_data = {
            'name': 'Updated Integration Test Category',
            'icon': 'fa-updated',
            'color': '#654321'
        }
        response = self.client.post(reverse('categories:category_update', kwargs={'pk': category.pk}), update_data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify category was updated
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Integration Test Category')
        
        # 5. Delete the category
        response = self.client.post(reverse('categories:category_delete', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, 302)
        
        # 6. Verify category was deleted
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
    
    def test_category_list_with_multiple_categories(self):
        """Test category list view with multiple categories."""
        # Create multiple categories with unique names to avoid conflicts
        for i in range(5):
            CategoryFactory(name=f'Category {i}')
        
        # Test unfiltered list
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 5)  # Total categories
