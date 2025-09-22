from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from categories.models import Category
from expenses.models import Expense
from income.models import Income
from subscriptions.models import Subscription
from work.models import WorkLog
from user_profile.models import UserProfile
from clients.models import Client
from mileage.models import MileageLog


class Command(BaseCommand):
    help = 'Seed the application with demo data for testing (clears existing data by default)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='Skip clearing existing data before seeding (default: clear all data)',
        )
        parser.add_argument(
            '--user',
            type=str,
            default='demo',
            help='Username for the demo user (default: demo)',
        )

    def handle(self, *args, **options):
        username = options['user']
        clear_existing = not options['no_clear']  # Default to True (clear data)

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
            MileageLog.objects.filter(user=user).delete()
            Client.objects.filter(user=user).delete()
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
        
        # Create clients
        clients = self.create_clients(user)
        
        # Create work logs
        self.create_work_logs(user, clients)
        
        # Create mileage logs
        self.create_mileage_logs(user, clients)
        
        # Create or update user profile
        self.create_user_profile(user)
        
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
            {'description': 'Weekly grocery shopping', 'amount': 85.50, 'category': 'Groceries', 'payee': 'Tesco', 'is_tax_deductible': False},
            {'description': 'Lunch at work', 'amount': 12.99, 'category': 'Restaurants', 'payee': 'Pret A Manger', 'is_tax_deductible': True},
            {'description': 'Coffee and pastry', 'amount': 4.50, 'category': 'Coffee & Drinks', 'payee': 'Starbucks', 'is_tax_deductible': False},
            {'description': 'Dinner with friends', 'amount': 45.00, 'category': 'Restaurants', 'payee': 'Nando\'s', 'is_tax_deductible': False},
            {'description': 'Takeaway pizza', 'amount': 18.99, 'category': 'Food & Dining', 'payee': 'Domino\'s', 'is_tax_deductible': False},
            
            # Transportation
            {'description': 'Fuel for car', 'amount': 65.00, 'category': 'Fuel', 'payee': 'Shell', 'is_tax_deductible': True},
            {'description': 'Monthly parking permit', 'amount': 120.00, 'category': 'Parking', 'payee': 'City Council', 'is_tax_deductible': True},
            {'description': 'Train ticket to London', 'amount': 35.50, 'category': 'Public Transport', 'payee': 'GWR', 'is_tax_deductible': True},
            {'description': 'Uber ride', 'amount': 18.75, 'category': 'Transportation', 'payee': 'Uber', 'is_tax_deductible': True},
            
            # Shopping
            {'description': 'New jeans', 'amount': 45.00, 'category': 'Clothing', 'payee': 'H&M', 'is_tax_deductible': False},
            {'description': 'Phone charger', 'amount': 15.99, 'category': 'Electronics', 'payee': 'Amazon', 'is_tax_deductible': True},
            {'description': 'Garden tools', 'amount': 32.50, 'category': 'Home & Garden', 'payee': 'B&Q', 'is_tax_deductible': False},
            {'description': 'Birthday gift', 'amount': 28.00, 'category': 'Shopping', 'payee': 'John Lewis', 'is_tax_deductible': False},
            
            # Entertainment
            {'description': 'Cinema tickets', 'amount': 24.00, 'category': 'Entertainment', 'payee': 'Odeon', 'is_tax_deductible': False},
            {'description': 'Netflix subscription', 'amount': 10.99, 'category': 'Entertainment', 'payee': 'Netflix', 'is_tax_deductible': False},
            {'description': 'New book', 'amount': 12.99, 'category': 'Books & Media', 'payee': 'Waterstones', 'is_tax_deductible': False},
            {'description': 'Gaming headset', 'amount': 89.99, 'category': 'Gaming', 'payee': 'Game', 'is_tax_deductible': False},
            
            # Health & Fitness
            {'description': 'Gym membership', 'amount': 45.00, 'category': 'Fitness', 'payee': 'PureGym', 'is_tax_deductible': False},
            {'description': 'Prescription medication', 'amount': 9.35, 'category': 'Pharmacy', 'payee': 'Boots', 'is_tax_deductible': False},
            {'description': 'Dental checkup', 'amount': 65.00, 'category': 'Healthcare', 'payee': 'Dental Practice', 'is_tax_deductible': False},
            
            # Bills & Utilities
            {'description': 'Electricity bill', 'amount': 89.50, 'category': 'Electricity', 'payee': 'British Gas', 'is_tax_deductible': False},
            {'description': 'Internet bill', 'amount': 35.00, 'category': 'Internet & Phone', 'payee': 'Sky', 'is_tax_deductible': True},
            {'description': 'Water bill', 'amount': 42.00, 'category': 'Water', 'payee': 'Thames Water', 'is_tax_deductible': False},
            {'description': 'Mobile phone bill', 'amount': 28.00, 'category': 'Internet & Phone', 'payee': 'EE', 'is_tax_deductible': True},
            
            # Business Expenses (Tax Deductible)
            {'description': 'Office supplies', 'amount': 25.50, 'category': 'Shopping', 'payee': 'Staples', 'is_tax_deductible': True},
            {'description': 'Professional development course', 'amount': 150.00, 'category': 'Entertainment', 'payee': 'Udemy', 'is_tax_deductible': True},
            {'description': 'Business lunch with client', 'amount': 65.00, 'category': 'Restaurants', 'payee': 'The Ivy', 'is_tax_deductible': True},
            {'description': 'Software license', 'amount': 89.99, 'category': 'Electronics', 'payee': 'Adobe', 'is_tax_deductible': True},
            {'description': 'Co-working space', 'amount': 200.00, 'category': 'Bills & Utilities', 'payee': 'WeWork', 'is_tax_deductible': True},
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
                    is_tax_deductible=expense_info['is_tax_deductible'],
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

    def create_clients(self, user):
        """Create demo clients"""
        client_data = [
            {
                'company_name': 'Tech Startup Ltd',
                'contact_person': 'John Smith',
                'email': 'john@techstartup.com',
                'phone': '+44 20 1234 5678',
                'address_line_1': '123 Innovation Street',
                'address_line_2': 'Floor 5',
                'town': 'London',
                'post_code': 'EC1A 1BB',
                'hourly_rate': 45.00,
            },
            {
                'company_name': 'Digital Agency XYZ',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@digitalagency.com',
                'phone': '+44 20 2345 6789',
                'address_line_1': '456 Creative Lane',
                'address_line_2': 'Studio 12',
                'town': 'Manchester',
                'post_code': 'M1 1AA',
                'hourly_rate': 50.00,
            },
            {
                'company_name': 'E-commerce Store',
                'contact_person': 'Mike Brown',
                'email': 'mike@ecommerce.com',
                'phone': '+44 20 3456 7890',
                'address_line_1': '789 Business Park',
                'address_line_2': 'Unit 15',
                'town': 'Birmingham',
                'post_code': 'B1 1BB',
                'hourly_rate': 40.00,
            },
            {
                'company_name': 'Consulting Firm',
                'contact_person': 'Emma Wilson',
                'email': 'emma@consulting.com',
                'phone': '+44 20 4567 8901',
                'address_line_1': '321 Corporate Plaza',
                'address_line_2': 'Suite 200',
                'town': 'Edinburgh',
                'post_code': 'EH1 1AA',
                'hourly_rate': 75.00,
            },
            {
                'company_name': 'Mobile App Developer',
                'contact_person': 'David Lee',
                'email': 'david@mobileapp.com',
                'phone': '+44 20 5678 9012',
                'address_line_1': '654 Tech Hub',
                'address_line_2': 'Floor 3',
                'town': 'Bristol',
                'post_code': 'BS1 1BB',
                'hourly_rate': 55.00,
            },
        ]
        
        clients = {}
        for client_info in client_data:
            client, created = Client.objects.get_or_create(
                user=user,
                company_name=client_info['company_name'],
                defaults={
                    'contact_person': client_info['contact_person'],
                    'email': client_info['email'],
                    'phone': client_info['phone'],
                    'address_line_1': client_info['address_line_1'],
                    'address_line_2': client_info['address_line_2'],
                    'town': client_info['town'],
                    'post_code': client_info['post_code'],
                    'hourly_rate': client_info['hourly_rate'],
                }
            )
            clients[client_info['company_name']] = client
            if created:
                self.stdout.write(f'Created client: {client.company_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(clients)} clients'))
        return clients

    def create_work_logs(self, user, clients):
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
                    company_client=clients[work_info['company_client']],
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

    def create_mileage_logs(self, user, clients):
        """Create demo mileage logs"""
        mileage_data = [
            {
                'start_location': 'Home',
                'end_location': 'Tech Startup Ltd Office',
                'purpose': 'Client meeting - project kickoff',
                'miles': 15.5,
                'client': 'Tech Startup Ltd'
            },
            {
                'start_location': 'Tech Startup Ltd Office',
                'end_location': 'Home',
                'purpose': 'Return journey from client meeting',
                'miles': 15.5,
                'client': 'Tech Startup Ltd'
            },
            {
                'start_location': 'Home',
                'end_location': 'Digital Agency XYZ Studio',
                'purpose': 'Site visit and requirements gathering',
                'miles': 25.3,
                'client': 'Digital Agency XYZ'
            },
            {
                'start_location': 'Digital Agency XYZ Studio',
                'end_location': 'Home',
                'purpose': 'Return journey from site visit',
                'miles': 25.3,
                'client': 'Digital Agency XYZ'
            },
            {
                'start_location': 'Home',
                'end_location': 'E-commerce Store Warehouse',
                'purpose': 'System installation and testing',
                'miles': 18.7,
                'client': 'E-commerce Store'
            },
            {
                'start_location': 'E-commerce Store Warehouse',
                'end_location': 'Home',
                'purpose': 'Return journey from installation',
                'miles': 18.7,
                'client': 'E-commerce Store'
            },
            {
                'start_location': 'Home',
                'end_location': 'Consulting Firm Office',
                'purpose': 'Strategy session with client',
                'miles': 32.1,
                'client': 'Consulting Firm'
            },
            {
                'start_location': 'Consulting Firm Office',
                'end_location': 'Home',
                'purpose': 'Return journey from strategy session',
                'miles': 32.1,
                'client': 'Consulting Firm'
            },
            {
                'start_location': 'Home',
                'end_location': 'Mobile App Developer Office',
                'purpose': 'Code review and technical discussion',
                'miles': 22.8,
                'client': 'Mobile App Developer'
            },
            {
                'start_location': 'Mobile App Developer Office',
                'end_location': 'Home',
                'purpose': 'Return journey from code review',
                'miles': 22.8,
                'client': 'Mobile App Developer'
            },
            {
                'start_location': 'Home',
                'end_location': 'Tech Startup Ltd Office',
                'purpose': 'Progress review meeting',
                'miles': 15.5,
                'client': 'Tech Startup Ltd'
            },
            {
                'start_location': 'Tech Startup Ltd Office',
                'end_location': 'Home',
                'purpose': 'Return journey from progress review',
                'miles': 15.5,
                'client': 'Tech Startup Ltd'
            },
            {
                'start_location': 'Home',
                'end_location': 'Digital Agency XYZ Studio',
                'purpose': 'Design presentation and feedback',
                'miles': 25.3,
                'client': 'Digital Agency XYZ'
            },
            {
                'start_location': 'Digital Agency XYZ Studio',
                'end_location': 'Home',
                'purpose': 'Return journey from design presentation',
                'miles': 25.3,
                'client': 'Digital Agency XYZ'
            },
            {
                'start_location': 'Home',
                'end_location': 'E-commerce Store Warehouse',
                'purpose': 'Training session for staff',
                'miles': 18.7,
                'client': 'E-commerce Store'
            },
            {
                'start_location': 'E-commerce Store Warehouse',
                'end_location': 'Home',
                'purpose': 'Return journey from training',
                'miles': 18.7,
                'client': 'E-commerce Store'
            },
            {
                'start_location': 'Home',
                'end_location': 'Consulting Firm Office',
                'purpose': 'Final project delivery',
                'miles': 32.1,
                'client': 'Consulting Firm'
            },
            {
                'start_location': 'Consulting Firm Office',
                'end_location': 'Home',
                'purpose': 'Return journey from project delivery',
                'miles': 32.1,
                'client': 'Consulting Firm'
            },
            {
                'start_location': 'Home',
                'end_location': 'Mobile App Developer Office',
                'purpose': 'Testing and debugging session',
                'miles': 22.8,
                'client': 'Mobile App Developer'
            },
            {
                'start_location': 'Mobile App Developer Office',
                'end_location': 'Home',
                'purpose': 'Return journey from testing session',
                'miles': 22.8,
                'client': 'Mobile App Developer'
            },
        ]
        
        # Create mileage logs for the last 4 months
        for i in range(4):
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            
            for mileage_info in mileage_data:
                # Randomize the date within the month
                day = random.randint(1, 28)
                mileage_date = month_date.replace(day=day)
                
                # Randomize miles slightly (±10%)
                base_miles = Decimal(str(mileage_info['miles']))
                variation = random.uniform(0.9, 1.1)
                miles = round(base_miles * Decimal(str(variation)), 1)
                
                MileageLog.objects.create(
                    user=user,
                    date=mileage_date,
                    start_location=mileage_info['start_location'],
                    end_location=mileage_info['end_location'],
                    purpose=mileage_info['purpose'],
                    miles=miles,
                    client=clients[mileage_info['client']],
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created mileage logs for user {user.username}'))

    def create_user_profile(self, user):
        """Create or update demo user profile"""
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'address_line_1': '123 Business Street',
                'address_line_2': 'Suite 456, Floor 3',
                'town': 'London',
                'post_code': 'SW1A 1AA',
                'email': 'demo@businessexample.com',
                'phone': '+44 20 7946 0958',
                'bank_name': 'Barclays Bank',
                'account_name': 'Demo Business Ltd',
                'account_number': '12345678',
                'sort_code': '20-00-00',
            }
        )
        
        if created:
            self.stdout.write(f'Created user profile for {user.username}')
        else:
            # Update existing profile with demo data
            profile.address_line_1 = '123 Business Street'
            profile.address_line_2 = 'Suite 456, Floor 3'
            profile.town = 'London'
            profile.post_code = 'SW1A 1AA'
            profile.email = 'demo@businessexample.com'
            profile.phone = '+44 20 7946 0958'
            profile.bank_name = 'Barclays Bank'
            profile.account_name = 'Demo Business Ltd'
            profile.account_number = '12345678'
            profile.sort_code = '20-00-00'
            profile.save()
            self.stdout.write(f'Updated user profile for {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Profile data ready for user {user.username}'))
