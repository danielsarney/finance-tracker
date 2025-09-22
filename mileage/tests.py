from django.test import TestCase, Client as TestClient
from django.urls import reverse
from decimal import Decimal
from datetime import date
from .models import MileageLog
from finance_tracker.factories import UserFactory, ClientFactory, MileageLogFactory, BatchMileageLogFactory


class MileageLogModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser')
        self.client_obj = ClientFactory(user=self.user, company_name='Test Client')

    def test_mileage_log_creation(self):
        """Test creating a mileage log."""
        log = MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 15),
            start_location='Home',
            end_location='Client Office',
            purpose='Client meeting',
            miles=Decimal('25.5'),
            client=self.client_obj
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.miles, Decimal('25.5'))
        self.assertEqual(log.client, self.client_obj)
        self.assertEqual(log.rate_per_mile, Decimal('0.45'))  # First 10k miles
        self.assertEqual(log.total_claim, Decimal('25.5') * Decimal('0.45'))

    def test_mileage_calculation_first_10k_miles(self):
        """Test calculation for first 10,000 miles."""
        log = MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 15),
            start_location='Home',
            end_location='Office',
            purpose='Work',
            miles=Decimal('50.0'),
            client=self.client_obj
        )
        
        self.assertEqual(log.rate_per_mile, Decimal('0.45'))
        self.assertEqual(log.total_claim, Decimal('22.50'))

    def test_mileage_calculation_over_10k_miles(self):
        """Test calculation when exceeding 10,000 miles."""
        # Create logs to reach 10,000 miles
        BatchMileageLogFactory.create_batch_for_user(
            self.user, 
            count=200,
            date=date(2024, 6, 15),
            start_location='Home',
            end_location='Office',
            purpose='Work',
            miles=Decimal('50.0'),
            client=self.client_obj
        )
        
        # Now add one more log - should use 25p rate
        log = MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 16),
            start_location='Home',
            end_location='Client',
            purpose='Client visit',
            miles=Decimal('30.0'),
            client=self.client_obj
        )
        
        self.assertEqual(log.rate_per_mile, Decimal('0.25'))
        self.assertEqual(log.total_claim, Decimal('7.50'))

    def test_mileage_calculation_mixed_rates(self):
        """Test calculation when a single journey spans both rate bands."""
        # Create logs to reach 9,500 miles
        BatchMileageLogFactory.create_batch_for_user(
            self.user,
            count=190,
            date=date(2024, 6, 15),
            start_location='Home',
            end_location='Office',
            purpose='Work',
            miles=Decimal('50.0'),
            client=self.client_obj
        )
        
        # Now add a 1,000 mile journey - should be mixed rates
        log = MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 16),
            start_location='Home',
            end_location='Distant Client',
            purpose='Client visit',
            miles=Decimal('1000.0'),
            client=self.client_obj
        )
        
        # 500 miles at 45p + 500 miles at 25p
        expected_claim = (Decimal('500') * Decimal('0.45')) + (Decimal('500') * Decimal('0.25'))
        self.assertEqual(log.total_claim, expected_claim)

    def test_tax_year_summary(self):
        """Test tax year summary calculation."""
        # Create logs in current tax year
        MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 15),  # After April 6th
            start_location='Home',
            end_location='Office',
            purpose='Work',
            miles=Decimal('100.0'),
            client=self.client_obj
        )
        
        summary = MileageLog.get_tax_year_summary(self.user, 2024)
        
        self.assertEqual(summary['total_miles'], Decimal('100.0'))
        self.assertEqual(summary['total_claim'], Decimal('45.00'))
        self.assertEqual(summary['miles_at_45p'], Decimal('100.0'))
        self.assertEqual(summary['miles_at_25p'], Decimal('0'))

    def test_string_representation(self):
        """Test string representation of mileage log."""
        log = MileageLogFactory(
            user=self.user,
            date=date(2024, 6, 15),
            start_location='Home',
            end_location='Office',
            purpose='Work',
            miles=Decimal('25.5'),
            client=self.client_obj
        )
        
        expected = "Home to Office - 25.5 miles (2024-06-15)"
        self.assertEqual(str(log), expected)


class MileageLogViewsTest(TestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser')
        self.client_obj = ClientFactory(user=self.user, company_name='Test Client')
        self.client = TestClient()
        self.client.login(username='testuser', password='testpass123')

    def test_mileage_list_view(self):
        """Test mileage list view."""
        response = self.client.get(reverse('mileage:mileage_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mileage Logs')

    def test_mileage_create_view(self):
        """Test mileage create view."""
        response = self.client.get(reverse('mileage:mileage_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log Mileage')

    def test_mileage_create_post(self):
        """Test creating mileage via POST."""
        data = {
            'date': '2024-06-15',
            'start_location': 'Home',
            'end_location': 'Office',
            'purpose': 'Work',
            'miles': '25.5',
            'client': self.client_obj.id,
            'start_address': '123 Home Street, London, SW1A 1AA',
            'end_address': '456 Office Road, Manchester, M1 1AA'
        }
        
        response = self.client.post(reverse('mileage:mileage_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Check that the mileage log was created
        self.assertEqual(MileageLog.objects.count(), 1)
        log = MileageLog.objects.first()
        self.assertEqual(log.miles, Decimal('25.5'))

    def test_mileage_summary_view(self):
        """Test mileage summary view."""
        response = self.client.get(reverse('mileage:mileage_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mileage Summary')

    def test_calculate_claim_api(self):
        """Test the calculate claim API endpoint."""
        response = self.client.get(reverse('mileage:calculate_claim'), {'miles': '50'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['miles'], 50)
        self.assertEqual(data['rate_per_mile'], 0.45)
        self.assertEqual(data['total_claim'], 22.50)

    def test_calculate_claim_api_invalid_miles(self):
        """Test the calculate claim API with invalid miles."""
        response = self.client.get(reverse('mileage:calculate_claim'), {'miles': 'invalid'})
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)