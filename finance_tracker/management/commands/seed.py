from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from categories.models import Category
from expenses.models import Expense
from income.models import Income
from subscriptions.models import Subscription
from work.models import WorkLog


class Command(BaseCommand):
    help = 'Seed the application with demo data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--user',
            type=str,
            default='demo',
            help='Username for the demo user (default: demo)',
        )

    def handle(self, *args, **options):
        username = options['user']
        clear_existing = options['clear']

        self.stdout.write(self.style.SUCCESS(f'Starting to seed data for user: {username}'))

        # Create or get demo user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created demo user: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing user: {username}'))

        if clear_existing:
            self.stdout.write('Clearing existing data...')
            Expense.objects.filter(user=user).delete()
            Income.objects.filter(user=user).delete()
            Subscription.objects.filter(user=user).delete()
            WorkLog.objects.filter(user=user).delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Create categories
        categories = self.create_categories()
        
        # Create expenses
        self.create_expenses(user, categories)
        
        # Create income
        self.create_income(user, categories)
        
        # Create subscriptions
        self.create_subscriptions(user, categories)
        
        # Create work logs
        self.create_work_logs(user)
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
        self.stdout.write(f'Demo user credentials: {username} / demo123')

    def create_categories(self):
        """Create demo categories"""
        category_data = [
            # Food & Dining
            {'name': 'Food & Dining', 'icon': 'fa-utensils', 'color': '#ff6b6b'},
            {'name': 'Groceries', 'icon': 'fa-shopping-cart', 'color': '#4ecdc4'},
            {'name': 'Restaurants', 'icon': 'fa-utensils', 'color': '#45b7d1'},
            {'name': 'Coffee & Drinks', 'icon': 'fa-coffee', 'color': '#96ceb4'},
            
            # Transportation
            {'name': 'Transportation', 'icon': 'fa-car', 'color': '#feca57'},
            {'name': 'Fuel', 'icon': 'fa-gas-pump', 'color': '#ff9ff3'},
            {'name': 'Public Transport', 'icon': 'fa-bus', 'color': '#54a0ff'},
            {'name': 'Parking', 'icon': 'fa-parking', 'color': '#5f27cd'},
            
            # Shopping
            {'name': 'Shopping', 'icon': 'fa-shopping-bag', 'color': '#ff9ff3'},
            {'name': 'Clothing', 'icon': 'fa-tshirt', 'color': '#00d2d3'},
            {'name': 'Electronics', 'icon': 'fa-laptop', 'color': '#5f27cd'},
            {'name': 'Home & Garden', 'icon': 'fa-home', 'color': '#ff6b6b'},
            
            # Entertainment
            {'name': 'Entertainment', 'icon': 'fa-film', 'color': '#54a0ff'},
            {'name': 'Gaming', 'icon': 'fa-gamepad', 'color': '#5f27cd'},
            {'name': 'Books & Media', 'icon': 'fa-book', 'color': '#00d2d3'},
            {'name': 'Hobbies', 'icon': 'fa-palette', 'color': '#ff9ff3'},
            
            # Health & Fitness
            {'name': 'Healthcare', 'icon': 'fa-heartbeat', 'color': '#ff6b6b'},
            {'name': 'Fitness', 'icon': 'fa-dumbbell', 'color': '#4ecdc4'},
            {'name': 'Pharmacy', 'icon': 'fa-pills', 'color': '#45b7d1'},
            
            # Bills & Utilities
            {'name': 'Bills & Utilities', 'icon': 'fa-bolt', 'color': '#feca57'},
            {'name': 'Internet & Phone', 'icon': 'fa-wifi', 'color': '#54a0ff'},
            {'name': 'Electricity', 'icon': 'fa-lightbulb', 'color': '#ff9ff3'},
            {'name': 'Water', 'icon': 'fa-tint', 'color': '#00d2d3'},
            {'name': 'Gas', 'icon': 'fa-fire', 'color': '#ff6b6b'},
            
            # Income Categories
            {'name': 'Salary', 'icon': 'fa-briefcase', 'color': '#4ecdc4'},
            {'name': 'Freelance', 'icon': 'fa-laptop-code', 'color': '#45b7d1'},
            {'name': 'Investments', 'icon': 'fa-chart-line', 'color': '#96ceb4'},
            {'name': 'Side Hustle', 'icon': 'fa-rocket', 'color': '#feca57'},
            {'name': 'Gifts', 'icon': 'fa-gift', 'color': '#ff9ff3'},
        ]
        
        categories = {}
        for cat_data in category_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        return categories

    def create_expenses(self, user, categories):
        """Create demo expenses"""
        expense_data = [
            # Food & Dining
            {'description': 'Weekly grocery shopping', 'amount': 85.50, 'category': 'Groceries', 'payee': 'Tesco'},
            {'description': 'Lunch at work', 'amount': 12.99, 'category': 'Restaurants', 'payee': 'Pret A Manger'},
            {'description': 'Coffee and pastry', 'amount': 4.50, 'category': 'Coffee & Drinks', 'payee': 'Starbucks'},
            {'description': 'Dinner with friends', 'amount': 45.00, 'category': 'Restaurants', 'payee': 'Nando\'s'},
            {'description': 'Takeaway pizza', 'amount': 18.99, 'category': 'Food & Dining', 'payee': 'Domino\'s'},
            
            # Transportation
            {'description': 'Fuel for car', 'amount': 65.00, 'category': 'Fuel', 'payee': 'Shell'},
            {'description': 'Monthly parking permit', 'amount': 120.00, 'category': 'Parking', 'payee': 'City Council'},
            {'description': 'Train ticket to London', 'amount': 35.50, 'category': 'Public Transport', 'payee': 'GWR'},
            {'description': 'Uber ride', 'amount': 18.75, 'category': 'Transportation', 'payee': 'Uber'},
            
            # Shopping
            {'description': 'New jeans', 'amount': 45.00, 'category': 'Clothing', 'payee': 'H&M'},
            {'description': 'Phone charger', 'amount': 15.99, 'category': 'Electronics', 'payee': 'Amazon'},
            {'description': 'Garden tools', 'amount': 32.50, 'category': 'Home & Garden', 'payee': 'B&Q'},
            {'description': 'Birthday gift', 'amount': 28.00, 'category': 'Shopping', 'payee': 'John Lewis'},
            
            # Entertainment
            {'description': 'Cinema tickets', 'amount': 24.00, 'category': 'Entertainment', 'payee': 'Odeon'},
            {'description': 'Netflix subscription', 'amount': 10.99, 'category': 'Entertainment', 'payee': 'Netflix'},
            {'description': 'New book', 'amount': 12.99, 'category': 'Books & Media', 'payee': 'Waterstones'},
            {'description': 'Gaming headset', 'amount': 89.99, 'category': 'Gaming', 'payee': 'Game'},
            
            # Health & Fitness
            {'description': 'Gym membership', 'amount': 45.00, 'category': 'Fitness', 'payee': 'PureGym'},
            {'description': 'Prescription medication', 'amount': 9.35, 'category': 'Pharmacy', 'payee': 'Boots'},
            {'description': 'Dental checkup', 'amount': 65.00, 'category': 'Healthcare', 'payee': 'Dental Practice'},
            
            # Bills & Utilities
            {'description': 'Electricity bill', 'amount': 89.50, 'category': 'Electricity', 'payee': 'British Gas'},
            {'description': 'Internet bill', 'amount': 35.00, 'category': 'Internet & Phone', 'payee': 'Sky'},
            {'description': 'Water bill', 'amount': 42.00, 'category': 'Water', 'payee': 'Thames Water'},
            {'description': 'Mobile phone bill', 'amount': 28.00, 'category': 'Internet & Phone', 'payee': 'EE'},
        ]
        
        # Create expenses for the last 6 months
        for i in range(6):
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            
            for expense_info in expense_data:
                # Randomize the date within the month
                day = random.randint(1, 28)
                expense_date = month_date.replace(day=day)
                
                # Randomize amount slightly (±20%)
                base_amount = Decimal(str(expense_info['amount']))
                variation = random.uniform(0.8, 1.2)
                amount = round(base_amount * Decimal(str(variation)), 2)
                
                Expense.objects.create(
                    user=user,
                    description=expense_info['description'],
                    amount=amount,
                    date=expense_date,
                    category=categories[expense_info['category']],
                    payee=expense_info['payee'],
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created expenses for user {user.username}'))

    def create_income(self, user, categories):
        """Create demo income"""
        income_data = [
            {'description': 'Monthly salary', 'amount': 2800.00, 'category': 'Salary', 'payer': 'Tech Corp Ltd'},
            {'description': 'Freelance web development', 'amount': 450.00, 'category': 'Freelance', 'payer': 'Startup Inc'},
            {'description': 'Dividend payment', 'amount': 125.50, 'category': 'Investments', 'payer': 'Vanguard'},
            {'description': 'Side project payment', 'amount': 300.00, 'category': 'Side Hustle', 'payer': 'Client XYZ'},
            {'description': 'Birthday money', 'amount': 100.00, 'category': 'Gifts', 'payer': 'Family'},
        ]
        
        # Create income for the last 6 months
        for i in range(6):
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            
            for income_info in income_data:
                # Randomize the date within the month (usually around payday)
                day = random.randint(25, 28) if income_info['category'] == 'Salary' else random.randint(1, 28)
                income_date = month_date.replace(day=day)
                
                # Randomize amount slightly (±10%)
                base_amount = Decimal(str(income_info['amount']))
                variation = random.uniform(0.9, 1.1)
                amount = round(base_amount * Decimal(str(variation)), 2)
                
                Income.objects.create(
                    user=user,
                    description=income_info['description'],
                    amount=amount,
                    date=income_date,
                    category=categories[income_info['category']],
                    payer=income_info['payer'],
                    is_taxable=income_info['category'] in ['Salary', 'Freelance', 'Side Hustle'],
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created income for user {user.username}'))

    def create_subscriptions(self, user, categories):
        """Create demo subscriptions"""
        subscription_data = [
            {'name': 'Netflix', 'amount': 10.99, 'category': 'Entertainment', 'billing_cycle': 'MONTHLY'},
            {'name': 'Spotify Premium', 'amount': 9.99, 'category': 'Entertainment', 'billing_cycle': 'MONTHLY'},
            {'name': 'Gym Membership', 'amount': 45.00, 'category': 'Fitness', 'billing_cycle': 'MONTHLY'},
            {'name': 'Adobe Creative Suite', 'amount': 52.99, 'category': 'Electronics', 'billing_cycle': 'MONTHLY'},
            {'name': 'Amazon Prime', 'amount': 8.99, 'category': 'Shopping', 'billing_cycle': 'MONTHLY'},
            {'name': 'Microsoft 365', 'amount': 59.99, 'category': 'Electronics', 'billing_cycle': 'YEARLY'},
            {'name': 'Car Insurance', 'amount': 85.00, 'category': 'Transportation', 'billing_cycle': 'MONTHLY'},
            {'name': 'Home Insurance', 'amount': 45.00, 'category': 'Bills & Utilities', 'billing_cycle': 'MONTHLY'},
        ]
        
        for sub_info in subscription_data:
            # Calculate next billing date
            today = timezone.now().date()
            if sub_info['billing_cycle'] == 'MONTHLY':
                next_billing = today.replace(day=15)  # Mid-month billing
            elif sub_info['billing_cycle'] == 'YEARLY':
                next_billing = today.replace(month=1, day=1) + timedelta(days=365)
            else:
                next_billing = today + timedelta(days=30)
            
            # Ensure next billing date is in the future
            if next_billing <= today:
                if sub_info['billing_cycle'] == 'MONTHLY':
                    next_billing = today + timedelta(days=30)
                elif sub_info['billing_cycle'] == 'YEARLY':
                    next_billing = today + timedelta(days=365)
            
            Subscription.objects.create(
                user=user,
                name=sub_info['name'],
                amount=Decimal(str(sub_info['amount'])),
                date=today,
                category=categories[sub_info['category']],
                billing_cycle=sub_info['billing_cycle'],
                next_billing_date=next_billing,
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created subscriptions for user {user.username}'))

    def create_work_logs(self, user):
        """Create demo work logs"""
        work_data = [
            {'company_client': 'Tech Startup Ltd', 'hours_worked': 8.0, 'hourly_rate': 45.00},
            {'company_client': 'Digital Agency XYZ', 'hours_worked': 6.5, 'hourly_rate': 50.00},
            {'company_client': 'E-commerce Store', 'hours_worked': 12.0, 'hourly_rate': 40.00},
            {'company_client': 'Consulting Firm', 'hours_worked': 4.0, 'hourly_rate': 75.00},
            {'company_client': 'Mobile App Developer', 'hours_worked': 10.0, 'hourly_rate': 55.00},
        ]
        
        # Create work logs for the last 3 months
        for i in range(3):
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            
            for work_info in work_data:
                # Randomize the date within the month
                day = random.randint(1, 28)
                work_date = month_date.replace(day=day)
                
                # Randomize hours slightly
                hours = round(work_info['hours_worked'] * random.uniform(0.8, 1.2), 2)
                hourly_rate = work_info['hourly_rate']
                total_amount = round(hours * hourly_rate, 2)
                
                # Randomize status
                status = random.choice(['PENDING', 'INVOICED', 'PAID'])
                
                work_log = WorkLog.objects.create(
                    user=user,
                    company_client=work_info['company_client'],
                    hours_worked=hours,
                    hourly_rate=hourly_rate,
                    total_amount=total_amount,
                    work_date=work_date,
                    status=status,
                )
                
                # Add invoice and payment dates based on status
                if status in ['INVOICED', 'PAID']:
                    work_log.invoice_date = work_date + timedelta(days=random.randint(1, 7))
                    work_log.invoice_number = f"INV-{work_date.year}{work_date.month:02d}-{random.randint(1000, 9999)}"
                    
                    if status == 'PAID':
                        work_log.payment_date = work_log.invoice_date + timedelta(days=random.randint(15, 45))
                    
                    work_log.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created work logs for user {user.username}'))
