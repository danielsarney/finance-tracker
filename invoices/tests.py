from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
import json
from finance_tracker.factories import (
    UserFactory, ClientFactory, WorkLogFactory
)
from .models import Invoice, InvoiceLineItem
from .forms import InvoiceForm


class InvoiceModelTest(TestCase):
    """Test cases for the Invoice model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client_obj = ClientFactory(user=self.user)
        self.work_log = WorkLogFactory(
            user=self.user, 
            company_client=self.client_obj,
            status='PENDING'
        )
    
    def test_invoice_number_generation_logic(self):
        """Test the invoice number generation logic directly."""
        # Clear any existing invoices
        Invoice.objects.all().delete()
        
        # Test first invoice
        invoice1 = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        self.assertEqual(invoice1.invoice_number, "INV-005")
        
        # Test second invoice
        invoice2 = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        self.assertEqual(invoice2.invoice_number, "INV-006")
        
        # Test the generate_invoice_number method directly
        next_number = Invoice.generate_invoice_number()
        self.assertEqual(next_number, "INV-007")
    
    def test_invoice_creation(self):
        """Test creating a basic invoice."""
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        self.assertEqual(invoice.user, self.user)
        self.assertEqual(invoice.client, self.client_obj)
        self.assertEqual(invoice.sender_name, "Test User")
        self.assertEqual(invoice.bank_name, "Test Bank")
    
    def test_invoice_number_generation(self):
        """Test automatic invoice number generation."""
        # Clear any existing invoices
        Invoice.objects.all().delete()
        
        # Create first invoice
        invoice1 = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        # Create second invoice
        invoice2 = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        self.assertEqual(invoice1.invoice_number, "INV-005")
        self.assertEqual(invoice2.invoice_number, "INV-006")
    
    def test_invoice_with_line_items(self):
        """Test invoice with linked work logs."""
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        # Create line item
        line_item = InvoiceLineItem.objects.create(
            invoice=invoice,
            work_log=self.work_log
        )
        
        self.assertEqual(invoice.line_items.count(), 1)
        self.assertEqual(invoice.total_amount, self.work_log.total_amount)
    
    def test_invoice_status_properties(self):
        """Test invoice status properties."""
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        # Test unpaid invoice
        self.assertFalse(invoice.is_paid)
        
        # Test overdue invoice
        overdue_invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today() - timedelta(days=60),
            due_date=date.today() - timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        self.assertTrue(overdue_invoice.is_overdue)


class InvoiceFormTest(TestCase):
    """Test cases for the InvoiceForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client_obj = ClientFactory(user=self.user)
    
    def test_invoice_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30)
        }
        
        form = InvoiceForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invoice_form_invalid_dates(self):
        """Test form validation for invalid dates."""
        # Due date before issue date
        form_data = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() - timedelta(days=1)
        }
        
        form = InvoiceForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Due date must be after issue date', str(form.errors))
        
        # Issue date in future
        form_data = {
            'client': self.client_obj.id,
            'issue_date': date.today() + timedelta(days=1),
            'due_date': date.today() + timedelta(days=30)
        }
        
        form = InvoiceForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Issue date cannot be in the future', str(form.errors))
    
    def test_invoice_form_user_filtering(self):
        """Test that form only shows clients for the current user."""
        other_user = UserFactory()
        other_client = ClientFactory(user=other_user)
        
        form = InvoiceForm(user=self.user)
        self.assertIn(self.client_obj, form.fields['client'].queryset)
        self.assertNotIn(other_client, form.fields['client'].queryset)
    
    def test_invoice_form_default_dates(self):
        """Test form sets default dates correctly."""
        form = InvoiceForm(user=self.user)
        self.assertEqual(form.fields['issue_date'].initial, date.today())
        self.assertEqual(form.fields['due_date'].initial, date.today() + timedelta(days=30))


class InvoiceViewsTest(TestCase):
    """Test cases for invoice views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client_obj = ClientFactory(user=self.user)
        self.work_log = WorkLogFactory(
            user=self.user,
            company_client=self.client_obj,
            status='PENDING'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_invoice_list_view(self):
        """Test invoice list view."""
        # Create an invoice
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        response = self.client.get(reverse('invoices:invoice_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
    
    def test_invoice_create_view_get(self):
        """Test invoice create view GET request."""
        response = self.client.get(reverse('invoices:invoice_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Invoice')
    
    def test_invoice_create_view_post(self):
        """Test invoice create view POST request."""
        data = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': [self.work_log.id]
        }
        
        response = self.client.post(reverse('invoices:invoice_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check invoice was created
        invoice = Invoice.objects.first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.client, self.client_obj)
        
        # Check work log was updated
        self.work_log.refresh_from_db()
        self.assertEqual(self.work_log.status, 'INVOICED')
        self.assertEqual(self.work_log.invoice_number, invoice.invoice_number)
    
    def test_invoice_detail_view(self):
        """Test invoice detail view."""
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        response = self.client.get(reverse('invoices:invoice_detail', kwargs={'pk': invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
    
    def test_get_available_worklogs_view(self):
        """Test AJAX endpoint for getting available work logs."""
        response = self.client.get(
            reverse('invoices:get_available_worklogs', kwargs={'client_id': self.client_obj.id})
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['work_logs']), 1)
        self.assertEqual(data['work_logs'][0]['id'], self.work_log.id)
    
    def test_invoice_download_pdf_view(self):
        """Test PDF download view."""
        invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        response = self.client.get(reverse('invoices:invoice_download_pdf', kwargs={'pk': invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])


class InvoiceLineItemTest(TestCase):
    """Test cases for InvoiceLineItem model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client_obj = ClientFactory(user=self.user)
        self.work_log = WorkLogFactory(
            user=self.user,
            company_client=self.client_obj,
            status='PENDING'
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="Test User",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="test@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
    
    def test_invoice_line_item_creation(self):
        """Test creating invoice line item."""
        line_item = InvoiceLineItem.objects.create(
            invoice=self.invoice,
            work_log=self.work_log
        )
        
        self.assertEqual(line_item.invoice, self.invoice)
        self.assertEqual(line_item.work_log, self.work_log)
        self.assertEqual(str(line_item), f"{self.invoice.invoice_number} - {self.work_log}")
    
    def test_invoice_total_amount_calculation(self):
        """Test invoice total amount calculation with multiple line items."""
        # Create additional work log
        work_log2 = WorkLogFactory(
            user=self.user,
            company_client=self.client_obj,
            status='PENDING',
            hours_worked=Decimal('4.0'),
            hourly_rate=Decimal('50.00')
        )
        
        # Create line items
        InvoiceLineItem.objects.create(invoice=self.invoice, work_log=self.work_log)
        InvoiceLineItem.objects.create(invoice=self.invoice, work_log=work_log2)
        
        expected_total = self.work_log.total_amount + work_log2.total_amount
        self.assertEqual(self.invoice.total_amount, expected_total)


class InvoiceIntegrationTest(TestCase):
    """Integration tests for the complete invoice workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.client_obj = ClientFactory(user=self.user)
        self.work_logs = WorkLogFactory.create_batch(
            3, user=self.user, company_client=self.client_obj, status='PENDING'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_complete_invoice_workflow(self):
        """Test the complete invoice creation workflow."""
        # 1. Create invoice
        data = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': [wl.id for wl in self.work_logs]
        }
        
        response = self.client.post(reverse('invoices:invoice_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify invoice was created
        invoice = Invoice.objects.first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.line_items.count(), 3)
        
        # 3. Verify work logs were updated
        for work_log in self.work_logs:
            work_log.refresh_from_db()
            self.assertEqual(work_log.status, 'INVOICED')
            self.assertEqual(work_log.invoice_number, invoice.invoice_number)
            self.assertEqual(work_log.invoice_date, invoice.issue_date)
        
        # 4. Verify invoice details are locked
        self.assertIsNotNone(invoice.sender_name)
        self.assertIsNotNone(invoice.bank_name)
        
        # 5. Test PDF download
        pdf_response = self.client.get(
            reverse('invoices:invoice_download_pdf', kwargs={'pk': invoice.pk})
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
    
    def test_invoice_with_no_work_logs(self):
        """Test invoice creation with no work logs selected."""
        data = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': []
        }
        
        response = self.client.post(reverse('invoices:invoice_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Invoice should be deleted if no work logs selected
        self.assertEqual(Invoice.objects.count(), 0)
    
    def test_invoice_number_sequence(self):
        """Test invoice number sequence across multiple invoices."""
        # Clear any existing invoices to start fresh
        Invoice.objects.all().delete()
        
        # Create first invoice
        data1 = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': [self.work_logs[0].id]
        }
        
        response1 = self.client.post(reverse('invoices:invoice_create'), data1)
        self.assertEqual(response1.status_code, 302)
        
        invoice1 = Invoice.objects.first()
        self.assertEqual(invoice1.invoice_number, "INV-005")
        
        # Create second invoice
        data2 = {
            'client': self.client_obj.id,
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': [self.work_logs[1].id]
        }
        
        response2 = self.client.post(reverse('invoices:invoice_create'), data2)
        self.assertEqual(response2.status_code, 302)
        
        # Get the second invoice by ordering by ID (more reliable than .last())
        all_invoices = list(Invoice.objects.order_by('id'))
        invoice2 = all_invoices[1]  # Get the second invoice by index
        self.assertEqual(invoice2.invoice_number, "INV-006")


class InvoicePermissionTest(TestCase):
    """Test cases for invoice permissions and access control."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.client1 = ClientFactory(user=self.user1)
        self.client2 = ClientFactory(user=self.user2)
        self.work_log1 = WorkLogFactory(user=self.user1, company_client=self.client1)
        self.work_log2 = WorkLogFactory(user=self.user2, company_client=self.client2)
        
        self.client = Client()
    
    def test_user_cannot_access_other_user_invoice(self):
        """Test that users cannot access invoices from other users."""
        # Create invoice for user1
        invoice = Invoice.objects.create(
            user=self.user1,
            client=self.client1,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            sender_name="User1",
            sender_address_line_1="123 Test St",
            sender_town="Test City",
            sender_post_code="TE1 1ST",
            sender_phone="01234567890",
            sender_email="user1@example.com",
            bank_name="Test Bank",
            account_name="Test Account",
            account_number="12345678",
            sort_code="12-34-56"
        )
        
        # Try to access as user2
        self.client.force_login(self.user2)
        response = self.client.get(reverse('invoices:invoice_detail', kwargs={'pk': invoice.pk}))
        self.assertEqual(response.status_code, 404)
    
    def test_user_cannot_create_invoice_for_other_user_client(self):
        """Test that users cannot create invoices for other users' clients."""
        self.client.force_login(self.user1)
        
        data = {
            'client': self.client2.id,  # Client belongs to user2
            'issue_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'work_logs': [self.work_log1.id]
        }
        
        response = self.client.post(reverse('invoices:invoice_create'), data)
        self.assertEqual(response.status_code, 200)  # Form validation error
        self.assertFalse(Invoice.objects.filter(user=self.user1).exists())
