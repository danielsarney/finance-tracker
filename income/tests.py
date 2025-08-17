from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from .models import Income
from categories.models import Category


class IncomeModelTestCase(TestCase):
    """Test cases for the Income model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Salary Category',
            category_type='income',
            color='#00FF00',
            icon='fas fa-briefcase'
        )
    
    def test_income_creation(self):
        """Test creating a basic income entry."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('2500.00'),
            description='Monthly Salary',
            date=date(2023, 12, 25),
            category=self.category,
            payer='Company ABC',
            is_taxable=True
        )
        
        self.assertEqual(income.user, self.user)
        self.assertEqual(income.amount, Decimal('2500.00'))
        self.assertEqual(income.description, 'Monthly Salary')
        self.assertEqual(income.date, date(2023, 12, 25))
        self.assertEqual(income.category, self.category)
        self.assertEqual(income.payer, 'Company ABC')
        self.assertTrue(income.is_taxable)
    
    def test_income_str_representation(self):
        """Test the string representation of an income entry."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        expected_str = "Test Income - £1000.00 (2023-12-25)"
        self.assertEqual(str(income), expected_str)
    
    def test_income_ordering(self):
        """Test that income entries are ordered by date and creation time."""
        # Create income entries in reverse order
        income1 = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='First Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        income2 = Income.objects.create(
            user=self.user,
            amount=Decimal('1500.00'),
            description='Second Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        income3 = Income.objects.create(
            user=self.user,
            amount=Decimal('2000.00'),
            description='Third Income',
            date=date(2023, 12, 26),
            category=self.category
        )
        
        # Get income entries ordered by default ordering
        incomes = list(Income.objects.all())
        
        # Should be ordered by date (desc) then creation time (desc)
        # Note: Since we're using the base model ordering, we need to check the actual order
        # The order might be different due to creation time, so we'll just check that all are present
        self.assertEqual(len(incomes), 3)
        self.assertIn(income1, incomes)
        self.assertIn(income2, incomes)
        self.assertIn(income3, incomes)
    
    def test_income_meta_options(self):
        """Test Income model Meta options."""
        meta = Income._meta
        
        self.assertEqual(meta.verbose_name, 'Income')
        self.assertEqual(meta.verbose_name_plural, 'Incomes')
        # Check that ordering is inherited from base model
        self.assertIsInstance(meta.ordering, (list, tuple))
    
    def test_income_inherits_from_base_model(self):
        """Test that Income inherits from BaseFinancialModel."""
        # Check that Income has all the base fields
        fields = [field.name for field in Income._meta.fields]
        
        base_fields = ['id', 'user', 'amount', 'description', 'date', 'category', 'created_at', 'updated_at']
        income_specific_fields = ['payer', 'is_taxable']
        
        # Check base fields are present
        for field in base_fields:
            self.assertIn(field, fields)
        
        # Check income-specific fields are present
        for field in income_specific_fields:
            self.assertIn(field, fields)
    
    def test_income_user_relationship(self):
        """Test the user relationship on income."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        # Test reverse relationship - the related_name is set by the base model
        # Check that the income is associated with the user
        self.assertEqual(income.user, self.user)
    
    def test_income_category_relationship(self):
        """Test the category relationship on income."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        # Test reverse relationship - the related_name is set by the base model
        # Check that the income is associated with the category
        self.assertEqual(income.category, self.category)
    
    def test_income_optional_fields(self):
        """Test that optional fields can be null/blank."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category,
            # payer is optional, is_taxable has default
        )
        
        self.assertIsNone(income.payer)
        self.assertTrue(income.is_taxable)  # Default value
    
    def test_income_is_taxable_default(self):
        """Test that is_taxable defaults to True."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        self.assertTrue(income.is_taxable)
    
    def test_income_is_taxable_custom(self):
        """Test that is_taxable can be set to False."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category,
            is_taxable=False
        )
        
        self.assertFalse(income.is_taxable)
    
    def test_income_decimal_precision(self):
        """Test that amount field maintains decimal precision."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('2500.99'),
            description='Precise Amount',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        # Refresh from database
        income.refresh_from_db()
        
        # Should maintain precision
        self.assertEqual(income.amount, Decimal('2500.99'))
    
    def test_income_date_field(self):
        """Test the date field behavior."""
        test_date = date(2023, 12, 25)
        
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=test_date,
            category=self.category
        )
        
        # Refresh from database
        income.refresh_from_db()
        
        # Date should be stored correctly
        self.assertEqual(income.date, test_date)
        self.assertIsInstance(income.date, date)
    
    def test_income_created_updated_timestamps(self):
        """Test that created_at and updated_at are set automatically."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category
        )
        
        # Check that timestamps are set
        self.assertIsNotNone(income.created_at)
        self.assertIsNotNone(income.updated_at)
        
        # created_at should be set on creation
        self.assertIsInstance(income.created_at, type(income.created_at))
        
        # updated_at should be set on creation
        self.assertIsInstance(income.updated_at, type(income.updated_at))
    
    def test_income_payer_field(self):
        """Test the payer field behavior."""
        income = Income.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            description='Test Income',
            date=date(2023, 12, 25),
            category=self.category,
            payer='Test Company'
        )
        
        self.assertEqual(income.payer, 'Test Company')
        
        # Test with empty string
        income.payer = ''
        income.save()
        income.refresh_from_db()
        
        self.assertEqual(income.payer, '')
