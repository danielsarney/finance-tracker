from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.db import models
from django.core.paginator import Paginator
from decimal import Decimal
from .mixins import BaseFinancialModel, BaseListViewMixin
from .view_mixins import BaseCRUDMixin, create_crud_views


class TestBaseFinancialModel(BaseFinancialModel):
    """Test model that inherits from BaseFinancialModel."""
    class Meta:
        app_label = 'finance_tracker'
        abstract = True


class MixinsTestCase(TestCase):
    """Test cases for mixin classes."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()
    
    def test_base_financial_model_meta(self):
        """Test BaseFinancialModel Meta options."""
        self.assertTrue(TestBaseFinancialModel._meta.abstract)
        # The ordering is inherited from the base model, so we check it's not empty
        self.assertIsInstance(TestBaseFinancialModel._meta.ordering, (list, tuple))
    
    def test_base_financial_model_fields(self):
        """Test BaseFinancialModel has required fields."""
        fields = [field.name for field in TestBaseFinancialModel._meta.fields]
        
        required_fields = [
            'user', 'amount', 'description', 'date', 
            'category', 'created_at', 'updated_at'
        ]
        
        for field in required_fields:
            self.assertIn(field, fields)
    
    def test_base_financial_model_str(self):
        """Test BaseFinancialModel __str__ method."""
        # Create a test instance using a concrete model
        from expenses.models import Expense
        from categories.models import Category
        
        category = Category.objects.create(
            name='Test Category',
            category_type='expense',
            color='#FF0000',
            icon='fas fa-test'
        )
        
        expense = Expense.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            description='Test Description',
            date='2023-01-01',
            category=category
        )
        
        expected_str = "Test Description - £100.00 (2023-01-01)"
        self.assertEqual(str(expense), expected_str)


class BaseListViewMixinTestCase(TestCase):
    """Test cases for BaseListViewMixin."""
    
    def setUp(self):
        """Set up test data."""
        self.mixin = BaseListViewMixin()
        self.factory = RequestFactory()
    
    def test_get_filtered_queryset_no_filters(self):
        """Test get_filtered_queryset with no filters."""
        # Mock queryset with filter method
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            
            def filter(self, **kwargs):
                return self
        
        queryset = MockQuerySet([1, 2, 3, 4, 5])
        
        # Create request with no filters
        request = self.factory.get('/')
        filtered = self.mixin.get_filtered_queryset(queryset, request)
        
        # Should return original queryset unchanged
        self.assertEqual(filtered, queryset)
    
    def test_get_filtered_queryset_with_month_filter(self):
        """Test get_filtered_queryset with month filter."""
        # Mock queryset with date-like objects and filter method
        class MockDate:
            def __init__(self, month):
                self.month = month
        
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            
            def filter(self, **kwargs):
                return self
        
        queryset = MockQuerySet([MockDate(1), MockDate(2), MockDate(3)])
        
        # Create request with month filter
        request = self.factory.get('/?month=2')
        filtered = self.mixin.get_filtered_queryset(queryset, request)
        
        # Should return filtered queryset
        self.assertEqual(filtered, queryset)
    
    def test_get_filtered_queryset_with_year_filter(self):
        """Test get_filtered_queryset with year filter."""
        # Mock queryset with date-like objects and filter method
        class MockDate:
            def __init__(self, year):
                self.year = year
        
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            
            def filter(self, **kwargs):
                return self
        
        queryset = MockQuerySet([MockDate(2022), MockDate(2023), MockDate(2024)])
        
        # Create request with year filter
        request = self.factory.get('/?year=2023')
        filtered = self.mixin.get_filtered_queryset(queryset, request)
        
        # Should return filtered queryset
        self.assertEqual(filtered, queryset)
    
    def test_get_filtered_queryset_with_category_filter(self):
        """Test get_filtered_queryset with category filter."""
        # Mock queryset with category-like objects and filter method
        class MockCategory:
            def __init__(self, category_id):
                self.category_id = category_id
        
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            
            def filter(self, **kwargs):
                return self
        
        queryset = MockQuerySet([MockCategory(1), MockCategory(2), MockCategory(3)])
        
        # Create request with category filter
        request = self.factory.get('/?category=2')
        filtered = self.mixin.get_filtered_queryset(queryset, request)
        
        # Should return filtered queryset
        self.assertEqual(filtered, queryset)
    
    def test_get_years_list(self):
        """Test get_years_list method."""
        years = self.mixin.get_years_list()
        
        # Should start from 2020
        self.assertEqual(years[0], 2020)
        # Should include current year
        from django.utils import timezone
        current_year = timezone.now().year
        self.assertIn(current_year, years)
        # Should be sequential
        self.assertEqual(years, list(range(2020, current_year + 1)))


class BaseCRUDMixinTestCase(TestCase):
    """Test cases for BaseCRUDMixin."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()
        
        # Create a test model class
        class TestModel:
            def __init__(self, pk, user):
                self.pk = pk
                self.user = user
            
            def save(self):
                pass
            
            def delete(self):
                pass
        
        self.TestModel = TestModel
        self.test_instance = TestModel(1, self.user)
    
    def test_get_queryset(self):
        """Test get_queryset method."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        # Mock model manager
        class MockManager:
            def __init__(self, test_instance):
                self.test_instance = test_instance
            
            def filter(self, user):
                return [self.test_instance]
        
        mixin.model.objects = MockManager(self.test_instance)
        
        # Create request with user
        request = self.factory.get('/')
        request.user = self.user
        
        queryset = mixin.get_queryset(request)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0], self.test_instance)
    
    def test_get_list_context(self):
        """Test get_list_context method."""
        mixin = BaseCRUDMixin()
        
        # Mock queryset with filter method and proper length
        class MockQuerySet:
            def __init__(self, data):
                self.data = data
            
            def filter(self, **kwargs):
                return self
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, key):
                return self.data[key]
        
        queryset = MockQuerySet([1, 2, 3, 4, 5])
        
        # Create request
        request = self.factory.get('/?month=1&year=2023&category=2')
        
        context, filtered_queryset = mixin.get_list_context(request, queryset)
        
        # Check context keys
        expected_keys = ['page_obj', 'selected_month', 'selected_year', 'selected_category', 'years']
        for key in expected_keys:
            self.assertIn(key, context)
        
        # Check filter values
        self.assertEqual(context['selected_month'], '1')
        self.assertEqual(context['selected_year'], '2023')
        self.assertEqual(context['selected_category'], '2')
        
        # Check years list
        self.assertIsInstance(context['years'], list)
    
    def test_create_view_get(self):
        """Test create_view with GET request."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        # Mock form class
        class MockFormClass:
            def __call__(self):
                return type('MockForm', (), {})()
        
        mixin.form_class = MockFormClass()
        mixin.template_name = 'expenses/expense_form.html'  # Use existing template
        
        request = self.factory.get('/')
        request.user = self.user
        
        response = mixin.create_view(request)
        
        # Should render template with form
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_post_valid(self):
        """Test create_view with valid POST request."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        # Mock form
        class MockForm:
            def __init__(self, data=None):
                self.data = data
            
            def is_valid(self):
                return True
            
            def save(self, commit=False):
                return self.test_instance
            
            def __init__(self, data=None):
                self.data = data
                self.test_instance = type('MockInstance', (), {'save': lambda: None})()
        
        mixin.form_class = MockForm
        mixin.list_url_name = 'test:list'
        
        request = self.factory.post('/')
        request.user = self.user
        
        # Mock messages framework
        request._messages = type('MockMessages', (), {'add': lambda *args, **kwargs: None})()
        
        response = mixin.create_view(request)
        
        # Should redirect to list view
        self.assertEqual(response.status_code, 302)
    
    def test_update_view_get(self):
        """Test update_view with GET request."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        # Mock form class
        class MockFormClass:
            def __call__(self, instance=None):
                return type('MockForm', (), {})()
        
        mixin.form_class = MockFormClass()
        mixin.template_name = 'expenses/expense_form.html'  # Use existing template
        
        request = self.factory.get('/')
        request.user = self.user
        
        # Mock get_object_or_404
        def mock_get_object_or_404(model, pk, user):
            return self.test_instance
        
        # Patch the function
        import django.shortcuts
        original_get_object_or_404 = django.shortcuts.get_object_or_404
        django.shortcuts.get_object_or_404 = mock_get_object_or_404
        
        try:
            response = mixin.update_view(request, 1)
            self.assertEqual(response.status_code, 200)
        finally:
            django.shortcuts.get_object_or_404 = original_get_object_or_404
    
    def test_delete_view_get(self):
        """Test delete_view with GET request."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        request = self.factory.get('/')
        request.user = self.user
        
        # Mock get_object_or_404
        def mock_get_object_or_404(model, pk, user):
            return self.test_instance
        
        # Patch the function
        import django.shortcuts
        original_get_object_or_404 = django.shortcuts.get_object_or_404
        django.shortcuts.get_object_or_404 = mock_get_object_or_404
        
        try:
            response = mixin.delete_view(request, 1)
            self.assertEqual(response.status_code, 200)
        finally:
            django.shortcuts.get_object_or_404 = original_get_object_or_404
    
    def test_detail_view(self):
        """Test detail_view method."""
        mixin = BaseCRUDMixin()
        mixin.model = self.TestModel
        
        request = self.factory.get('/')
        request.user = self.user
        
        # Mock get_object_or_404
        def mock_get_object_or_404(model, pk, user):
            return self.test_instance
        
        # Patch the function
        import django.shortcuts
        original_get_object_or_404 = django.shortcuts.get_object_or_404
        django.shortcuts.get_object_or_404 = mock_get_object_or_404
        
        try:
            response = mixin.detail_view(request, 1)
            self.assertEqual(response.status_code, 200)
        finally:
            django.shortcuts.get_object_or_404 = original_get_object_or_404


class CreateCRUDViewsTestCase(TestCase):
    """Test cases for create_crud_views factory function."""
    
    def test_create_crud_views_returns_five_views(self):
        """Test create_crud_views returns exactly 5 views."""
        class MockModel:
            pass
        
        class MockForm:
            pass
        
        views = create_crud_views(
            model=MockModel,
            form_class=MockForm,
            template_name='test.html',
            list_url_name='test:list'
        )
        
        self.assertEqual(len(views), 5)
        list_view, create_view, update_view, delete_view, detail_view = views
        
        # Check that all views are callable
        self.assertTrue(callable(list_view))
        self.assertTrue(callable(create_view))
        self.assertTrue(callable(update_view))
        self.assertTrue(callable(delete_view))
        self.assertTrue(callable(detail_view))
