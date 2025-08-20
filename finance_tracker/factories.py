import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
import random


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances."""
    class Meta:
        model = 'categories.Category'
    
    name = factory.Sequence(lambda n: f'category_{n}')
    color = factory.Faker('hex_color')
    icon = factory.Iterator([
        'fas fa-shopping-cart',
        'fas fa-money-bill-wave',
        'fas fa-credit-card',
        'fas fa-briefcase',
        'fas fa-home',
        'fas fa-utensils',
        'fas fa-car',
        'fas fa-graduation-cap'
    ])


class ExpenseFactory(DjangoModelFactory):
    """Factory for creating Expense instances."""
    class Meta:
        model = 'expenses.Expense'
    
    user = factory.SubFactory(UserFactory)
    description = factory.Faker('sentence', nb_words=3)
    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    date = factory.Faker('date_between', start_date='-1y', end_date='today')
    category = factory.SubFactory(CategoryFactory)


class IncomeFactory(DjangoModelFactory):
    """Factory for creating Income instances."""
    class Meta:
        model = 'income.Income'
    
    user = factory.SubFactory(UserFactory)
    description = factory.Faker('sentence', nb_words=3)
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    date = factory.Faker('date_between', start_date='-1y', end_date='today')
    category = factory.SubFactory(CategoryFactory)
    payer = factory.Faker('company')
    is_taxable = factory.Iterator([True, False])


class SubscriptionFactory(DjangoModelFactory):
    """Factory for creating Subscription instances."""
    class Meta:
        model = 'subscriptions.Subscription'
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker('company')
    amount = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    date = factory.Faker('date_between', start_date='-6m', end_date='today')
    billing_cycle = factory.Iterator(['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'])
    next_billing_date = factory.LazyAttribute(lambda obj: obj.date)
    category = factory.SubFactory(CategoryFactory)


class WorkLogFactory(DjangoModelFactory):
    """Factory for creating WorkLog instances."""
    class Meta:
        model = 'work.WorkLog'
    
    user = factory.SubFactory(UserFactory)
    company_client = factory.SubFactory('finance_tracker.factories.ClientFactory', user=factory.SelfAttribute('..user'))
    hours_worked = factory.Iterator([Decimal('4.0'), Decimal('8.0'), Decimal('6.5'), Decimal('10.0')])
    hourly_rate = factory.Iterator([Decimal('25.00'), Decimal('30.00'), Decimal('35.00'), Decimal('40.00')])
    work_date = factory.Faker('date_between', start_date='-1y', end_date='today')
    status = factory.Iterator(['PENDING', 'INVOICED', 'PAID'])


class ClientFactory(DjangoModelFactory):
    """Factory for creating Client instances."""
    class Meta:
        model = 'clients.Client'
    
    user = factory.SubFactory(UserFactory)
    company_name = factory.Faker('company')
    contact_person = factory.Faker('name')
    email = factory.LazyAttribute(lambda obj: f'{obj.contact_person.lower().replace(" ", ".")}@{obj.company_name.lower().replace(" ", "").replace(",", "").replace(".", "")}.com')
    phone = factory.LazyFunction(lambda: f"+44 {random.randint(100, 999)} {random.randint(100000, 999999)}")
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')
    town = factory.Faker('city')
    post_code = factory.LazyFunction(lambda: f"{random.choice(['SW1A', 'W1A', 'M1', 'B1', 'L1', 'G1', 'EH1', 'CF10', 'BS1', 'LS1'])} {random.randint(1, 9)}{random.choice(['AA', 'AB', 'CD', 'EF', 'GH', 'IJ', 'KL', 'MN', 'OP', 'QR'])}")
    hourly_rate = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=25, max_value=100)


class UserProfileFactory(DjangoModelFactory):
    """Factory for creating UserProfile instances."""
    class Meta:
        model = 'user_profile.UserProfile'
    
    user = factory.SubFactory(UserFactory)
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')
    town = factory.Faker('city')
    post_code = factory.LazyFunction(lambda: f"{random.choice(['SW1A', 'W1A', 'M1', 'B1', 'L1', 'G1', 'EH1', 'CF10', 'BS1', 'LS1'])} {random.randint(1, 9)}{random.choice(['AA', 'AB', 'CD', 'EF', 'GH', 'IJ', 'KL', 'MN', 'OP', 'QR'])}")
    phone = factory.LazyFunction(lambda: f"+44 {random.randint(100, 999)} {random.randint(100000, 999999)}")
    email = factory.LazyAttribute(lambda obj: f'{obj.user.username}@example.com')
    bank_name = factory.Faker('company')
    account_name = factory.Faker('name')
    account_number = factory.LazyFunction(lambda: f"{random.randint(10000000, 99999999)}")
    sort_code = factory.LazyFunction(lambda: f"{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}")

# Specialized factories for testing scenarios
class ExpenseWithSpecificDateFactory(ExpenseFactory):
    """Factory for creating expenses with a specific date."""
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(1, 30)))


class IncomeWithSpecificDateFactory(IncomeFactory):
    """Factory for creating income with a specific date."""
    date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(1, 30)))


class SubscriptionWithSpecificBillingCycleFactory(SubscriptionFactory):
    """Factory for creating subscriptions with specific billing cycles."""
    billing_cycle = factory.Iterator(['MONTHLY', 'YEARLY'])


class WorkLogWithSpecificHoursFactory(WorkLogFactory):
    """Factory for creating work logs with specific hours."""
    hours_worked = factory.Iterator([Decimal('4.0'), Decimal('8.0'), Decimal('6.5')])


# Batch factories for creating multiple instances
class BatchExpenseFactory:
    """Factory for creating multiple expenses for a user."""
    
    @staticmethod
    def create_batch_for_user(user, count=10, **kwargs):
        """Create multiple expenses for a specific user."""
        return ExpenseFactory.create_batch(count, user=user, **kwargs)
    
    @staticmethod
    def create_batch_for_month(user, year, month, count=5, **kwargs):
        """Create multiple expenses for a specific month."""
        expenses = []
        for _ in range(count):
            day = random.randint(1, 28)  # Avoid month-end issues
            expense_date = date(year, month, day)
            expenses.append(ExpenseFactory(user=user, date=expense_date, **kwargs))
        return expenses


class BatchIncomeFactory:
    """Factory for creating multiple income entries for a user."""
    
    @staticmethod
    def create_batch_for_user(user, count=10, **kwargs):
        """Create multiple income entries for a specific user."""
        return IncomeFactory.create_batch(count, user=user, **kwargs)
    
    @staticmethod
    def create_batch_for_month(user, year, month, count=3, **kwargs):
        """Create multiple income entries for a specific month."""
        incomes = []
        for _ in range(count):
            day = random.randint(1, 28)
            income_date = date(year, month, day)
            incomes.append(IncomeFactory(user=user, date=income_date, **kwargs))
        return incomes


class BatchSubscriptionFactory:
    """Factory for creating multiple subscriptions for a user."""
    
    @staticmethod
    def create_batch_for_user(user, count=5, **kwargs):
        """Create multiple subscriptions for a specific user."""
        return SubscriptionFactory.create_batch(count, user=user, **kwargs)


class BatchWorkLogFactory:
    """Factory for creating multiple work logs for a user."""
    
    @staticmethod
    def create_batch_for_user(user, count=20, **kwargs):
        """Create multiple work logs for a specific user."""
        return WorkLogFactory.create_batch(count, user=user, **kwargs)
    
    @staticmethod
    def create_batch_for_month(user, year, month, count=10, **kwargs):
        """Create multiple work logs for a specific month."""
        work_logs = []
        for _ in range(count):
            day = random.randint(1, 28)
            work_date = date(year, month, day)
            work_logs.append(WorkLogFactory(user=user, work_date=work_date, **kwargs))
        return work_logs


class BatchClientFactory:
    """Factory for creating multiple clients for a user."""
    
    @staticmethod
    def create_batch_for_user(user, count=5, **kwargs):
        """Create multiple clients for a specific user."""
        return ClientFactory.create_batch(count, user=user, **kwargs)
