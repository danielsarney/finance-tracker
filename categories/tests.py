from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal

from .models import Category
from .forms import CategoryForm
from finance_tracker.factories import UserFactory, CategoryFactory


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def setUp(self):
        self.category = CategoryFactory()
    
    def test_category_creation(self):
        """Test that Category can be created with required fields."""
        self.assertIsInstance(self.category, Category)
        self.assertIsNotNone(self.category.name)
        self.assertIsNotNone(self.category.category_type)
        self.assertIsNotNone(self.category.icon)
        self.assertIsNotNone(self.category.color)
    
    def test_category_str_representation(self):
        """Test the string representation of Category."""
        self.assertEqual(str(self.category), self.category.name)
    
    def test_category_default_values(self):
        """Test default values for Category fields."""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(category.category_type, 'general')
        self.assertEqual(category.color, '#6c757d')
        self.assertEqual(category.icon, '')
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_category_type_choices(self):
        """Test that category_type only accepts valid choices."""
        valid_types = ['expense', 'income', 'subscription', 'general']
        for category_type in valid_types:
            category = CategoryFactory(category_type=category_type)
            self.assertEqual(category.category_type, category_type)
    
    def test_category_name_uniqueness(self):
        """Test that category names must be unique."""
        name = "Unique Category"
        Category.objects.create(name=name, category_type='general')
        
        with self.assertRaises(Exception):
            Category.objects.create(name=name, category_type='expense')
    
    def test_category_meta(self):
        """Test Category meta options."""
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')
        self.assertEqual(Category._meta.ordering, ['name'])
    
    def test_category_get_icon_class(self):
        """Test the get_icon_class method."""
        # Test with icon that doesn't start with 'fa-'
        category = CategoryFactory(icon='utensils')
        self.assertEqual(category.get_icon_class(), 'fas fa-utensils')
        
        # Test with icon that starts with 'fa-'
        category = CategoryFactory(icon='fa-car')
        self.assertEqual(category.get_icon_class(), 'fas fa-car')
        
        # Test with no icon (should return default)
        category = CategoryFactory(icon='')
        self.assertEqual(category.get_icon_class(), 'fas fa-tag')
    
    def test_category_ordering(self):
        """Test that categories are ordered by name."""
        Category.objects.all().delete()  # Clear existing categories
        
        # Create categories in random order
        CategoryFactory(name="Zebra")
        CategoryFactory(name="Alpha")
        CategoryFactory(name="Beta")
        
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Alpha")
        self.assertEqual(categories[1].name, "Beta")
        self.assertEqual(categories[2].name, "Zebra")


class CategoryFormTest(TestCase):
    """Test cases for CategoryForm."""
    
    def setUp(self):
        self.valid_data = {
            'name': 'Test Category',
            'category_type': 'expense',
            'icon': 'fa-utensils',
            'color': '#ff0000'
        }
    
    def test_form_valid_data(self):
        """Test form with valid data."""
        form = CategoryForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        # Test missing name
        data = self.valid_data.copy()
        del data['name']
        form = CategoryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Test missing category_type
        data = self.valid_data.copy()
        del data['category_type']
        form = CategoryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('category_type', form.errors)
    
    def test_form_invalid_category_type(self):
        """Test form validation with invalid category type."""
        data = self.valid_data.copy()
        data['category_type'] = 'invalid_type'
        form = CategoryForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('category_type', form.errors)
    
    def test_form_save_creates_category(self):
        """Test that form.save() creates a Category instance."""
        form = CategoryForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        category = form.save()
        self.assertIsInstance(category, Category)
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.category_type, 'expense')
        self.assertEqual(category.icon, 'fa-utensils')
        self.assertEqual(category.color, '#ff0000')
    
    def test_form_widget_attributes(self):
        """Test that form fields have correct widget attributes."""
        form = CategoryForm()
        
        # Check name field
        self.assertIn('class', form.fields['name'].widget.attrs)
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        
        # Check category_type field
        self.assertIn('class', form.fields['category_type'].widget.attrs)
        self.assertEqual(form.fields['category_type'].widget.attrs['class'], 'form-select')
        
        # Check icon field
        self.assertIn('class', form.fields['icon'].widget.attrs)
        self.assertEqual(form.fields['icon'].widget.attrs['class'], 'form-control')
        self.assertIn('placeholder', form.fields['icon'].widget.attrs)
        
        # Check color field
        self.assertIn('class', form.fields['color'].widget.attrs)
        self.assertEqual(form.fields['color'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['color'].widget.attrs['type'], 'color')
    
    def test_form_update_existing_category(self):
        """Test updating an existing category with the form."""
        # Create a category first
        category = CategoryFactory()
        
        # Update data
        update_data = {
            'name': 'Updated Category',
            'category_type': 'income',
            'icon': 'fa-money-bill',
            'color': '#00ff00'
        }
        
        form = CategoryForm(data=update_data, instance=category)
        self.assertTrue(form.is_valid())
        
        updated_category = form.save()
        self.assertEqual(updated_category.name, 'Updated Category')
        self.assertEqual(updated_category.category_type, 'income')
        self.assertEqual(updated_category.icon, 'fa-money-bill')
        self.assertEqual(updated_category.color, '#00ff00')


class CategoriesViewsTest(TestCase):
    """Test cases for categories views."""
    
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create some test categories
        self.expense_category = CategoryFactory(category_type='expense')
        self.income_category = CategoryFactory(category_type='income')
        self.subscription_category = CategoryFactory(category_type='subscription')
        self.general_category = CategoryFactory(category_type='general')
    
    def test_category_list_view_get(self):
        """Test category list view GET request."""
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_list.html')
        
        # Check context
        self.assertIn('page_obj', response.context)
        self.assertIn('category_types', response.context)
        self.assertIn('selected_type', response.context)
        
        # Check that all categories are in the response
        self.assertContains(response, self.expense_category.name)
        self.assertContains(response, self.income_category.name)
    
    def test_category_list_view_filtering(self):
        """Test category list view with type filtering."""
        # Filter by expense type
        response = self.client.get(reverse('categories:category_list'), {'type': 'expense'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_type'], 'expense')
        
        # Should only show expense categories
        self.assertContains(response, self.expense_category.name)
        self.assertNotContains(response, self.income_category.name)
    
    def test_category_list_view_pagination(self):
        """Test category list view pagination."""
        # Create many categories to trigger pagination
        for i in range(25):
            CategoryFactory(name=f"Category {i}")
        
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check pagination
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        self.assertIsInstance(page_obj, Paginator)
        self.assertEqual(page_obj.per_page, 20)
    
    def test_category_create_view_get(self):
        """Test category create view GET request."""
        response = self.client.get(reverse('categories:category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_form.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CategoryForm)
        self.assertEqual(response.context['title'], 'Add New Category')
    
    def test_category_create_view_post_valid(self):
        """Test category create view POST request with valid data."""
        data = {
            'name': 'New Test Category',
            'category_type': 'expense',
            'icon': 'fa-test',
            'color': '#123456'
        }
        
        response = self.client.post(reverse('categories:category_create'), data)
        
        # Should redirect to category list
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # Check that category was created
        new_category = Category.objects.get(name='New Test Category')
        self.assertEqual(new_category.category_type, 'expense')
        self.assertEqual(new_category.icon, 'fa-test')
        self.assertEqual(new_category.color, '#123456')
        
        # Check success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Category created successfully!', str(messages_list[0]))
    
    def test_category_create_view_post_invalid(self):
        """Test category create view POST request with invalid data."""
        data = {
            'name': '',  # Invalid: empty name
            'category_type': 'invalid_type',  # Invalid category type
            'icon': 'fa-test',
            'color': '#123456'
        }
        
        response = self.client.post(reverse('categories:category_create'), data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertTemplateUsed(response, 'categories/category_form.html')
        
        # Check that form errors are displayed
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_category_update_view_get(self):
        """Test category update view GET request."""
        response = self.client.get(reverse('categories:category_update', kwargs={'pk': self.expense_category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_form.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CategoryForm)
        self.assertEqual(response.context['title'], 'Edit Category')
        
        # Check that form is pre-populated with existing data
        form = response.context['form']
        self.assertEqual(form.instance.name, self.expense_category.name)
    
    def test_category_update_view_post_valid(self):
        """Test category update view POST request with valid data."""
        data = {
            'name': 'Updated Category Name',
            'category_type': 'income',
            'icon': 'fa-updated',
            'color': '#654321'
        }
        
        response = self.client.post(
            reverse('categories:category_update', kwargs={'pk': self.expense_category.pk}),
            data
        )
        
        # Should redirect to category list
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # Check that category was updated
        self.expense_category.refresh_from_db()
        self.assertEqual(self.expense_category.name, 'Updated Category Name')
        self.assertEqual(self.expense_category.category_type, 'income')
        self.assertEqual(self.expense_category.icon, 'fa-updated')
        self.assertEqual(self.expense_category.color, '#654321')
        
        # Check success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Category updated successfully!', str(messages_list[0]))
    
    def test_category_update_view_post_invalid(self):
        """Test category update view POST request with invalid data."""
        data = {
            'name': '',  # Invalid: empty name
            'category_type': 'expense',
            'icon': 'fa-test',
            'color': '#123456'
        }
        
        response = self.client.post(
            reverse('categories:category_update', kwargs={'pk': self.expense_category.pk}),
            data
        )
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertTemplateUsed(response, 'categories/category_form.html')
        
        # Check that form errors are displayed
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_category_delete_view_get(self):
        """Test category delete view GET request."""
        response = self.client.get(reverse('categories:category_delete', kwargs={'pk': self.expense_category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_confirm_delete.html')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], self.expense_category)
    
    def test_category_delete_view_post(self):
        """Test category delete view POST request."""
        category_pk = self.expense_category.pk
        
        response = self.client.post(reverse('categories:category_delete', kwargs={'pk': category_pk}))
        
        # Should redirect to category list
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # Check that category was deleted
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=category_pk)
        
        # Check success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Category deleted successfully!', str(messages_list[0]))
    
    def test_category_detail_view(self):
        """Test category detail view."""
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': self.expense_category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_detail.html')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], self.expense_category)
    
    def test_category_views_require_login(self):
        """Test that all category views require login."""
        # Logout the user
        self.client.logout()
        
        # Test all views require login
        views_to_test = [
            'categories:category_list',
            'categories:category_create',
            'categories:category_update',
            'categories:category_delete',
            'categories:category_detail'
        ]
        
        for view_name in views_to_test:
            if 'pk' in view_name:
                response = self.client.get(reverse(view_name, kwargs={'pk': 1}))
            else:
                response = self.client.get(reverse(view_name))
            
            # Should redirect to login page
            self.assertRedirects(response, f"/login/?next={reverse(view_name)}")
    
    def test_category_update_view_nonexistent(self):
        """Test category update view with nonexistent category."""
        response = self.client.get(reverse('categories:category_update', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_category_delete_view_nonexistent(self):
        """Test category delete view with nonexistent category."""
        response = self.client.get(reverse('categories:category_delete', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_category_detail_view_nonexistent(self):
        """Test category detail view with nonexistent category."""
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class CategoriesURLsTest(TestCase):
    """Test cases for categories URLs."""
    
    def test_category_list_url(self):
        """Test category list URL pattern."""
        url = reverse('categories:category_list')
        self.assertEqual(url, '/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, 'category_list')
        self.assertEqual(resolver.app_name, 'categories')
    
    def test_category_create_url(self):
        """Test category create URL pattern."""
        url = reverse('categories:category_create')
        self.assertEqual(url, '/create/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, 'category_create')
        self.assertEqual(resolver.app_name, 'categories')
    
    def test_category_detail_url(self):
        """Test category detail URL pattern."""
        url = reverse('categories:category_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/1/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, 'category_detail')
        self.assertEqual(resolver.app_name, 'categories')
    
    def test_category_update_url(self):
        """Test category update URL pattern."""
        url = reverse('categories:category_update', kwargs={'pk': 1})
        self.assertEqual(url, '/1/update/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, 'category_update')
        self.assertEqual(resolver.app_name, 'categories')
    
    def test_category_delete_url(self):
        """Test category delete URL pattern."""
        url = reverse('categories:category_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/1/delete/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, 'category_delete')
        self.assertEqual(resolver.app_name, 'categories')


class CategoryIntegrationTest(TestCase):
    """Integration tests for Category functionality."""
    
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.login(username=self.user.username, password='testpass123')
    
    def test_category_workflow(self):
        """Test the complete category workflow: create, read, update, delete."""
        # 1. Create a category
        create_data = {
            'name': 'Workflow Test Category',
            'category_type': 'expense',
            'icon': 'fa-workflow',
            'color': '#abcdef'
        }
        
        response = self.client.post(reverse('categories:category_create'), create_data)
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # 2. Verify category was created
        category = Category.objects.get(name='Workflow Test Category')
        self.assertEqual(category.category_type, 'expense')
        self.assertEqual(category.icon, 'fa-workflow')
        self.assertEqual(category.color, '#abcdef')
        
        # 3. Read category detail
        response = self.client.get(reverse('categories:category_detail', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workflow Test Category')
        
        # 4. Update category
        update_data = {
            'name': 'Updated Workflow Category',
            'category_type': 'income',
            'icon': 'fa-updated',
            'color': '#fedcba'
        }
        
        response = self.client.post(
            reverse('categories:category_update', kwargs={'pk': category.pk}),
            update_data
        )
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # 5. Verify update
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Workflow Category')
        self.assertEqual(category.category_type, 'income')
        
        # 6. Delete category
        response = self.client.post(reverse('categories:category_delete', kwargs={'pk': category.pk}))
        self.assertRedirects(response, reverse('categories:category_list'))
        
        # 7. Verify deletion
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=category.pk)
    
    def test_category_type_filtering_workflow(self):
        """Test category filtering workflow."""
        # Create categories of different types
        CategoryFactory(category_type='expense', name='Expense Category 1')
        CategoryFactory(category_type='expense', name='Expense Category 2')
        CategoryFactory(category_type='income', name='Income Category 1')
        CategoryFactory(category_type='subscription', name='Subscription Category 1')
        
        # Test filtering by expense type
        response = self.client.get(reverse('categories:category_list'), {'type': 'expense'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expense Category 1')
        self.assertContains(response, 'Expense Category 2')
        self.assertNotContains(response, 'Income Category 1')
        self.assertNotContains(response, 'Subscription Category 1')
        
        # Test filtering by income type
        response = self.client.get(reverse('categories:category_list'), {'type': 'income'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Income Category 1')
        self.assertNotContains(response, 'Expense Category 1')
        
        # Test no filtering (should show all)
        response = self.client.get(reverse('categories:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expense Category 1')
        self.assertContains(response, 'Income Category 1')
        self.assertContains(response, 'Subscription Category 1')


class CategoriesAppConfigTest(TestCase):
    """Test cases for categories app configuration."""
    
    def test_app_config(self):
        """Test that the categories app is properly configured."""
        from django.apps import apps
        app_config = apps.get_app_config('categories')
        self.assertEqual(app_config.name, 'categories')
        self.assertEqual(app_config.label, 'categories')
    
    def test_app_models_registered(self):
        """Test that Category model is registered."""
        from django.apps import apps
        app_config = apps.get_app_config('categories')
        self.assertIn('Category', [model.__name__ for model in app_config.get_models()])
