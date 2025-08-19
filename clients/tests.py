from django.test import TestCase, Client as TestClient
from django.urls import reverse
from .models import Client
from finance_tracker.factories import UserFactory, ClientFactory

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_client_creation(self):
        """Test that a client can be created with all required fields"""
        client = ClientFactory(user=self.user)
        
        self.assertIsNotNone(client.company_name)
        self.assertIsNotNone(client.contact_person)
        self.assertIsNotNone(client.email)
        self.assertIsNotNone(client.hourly_rate)
        self.assertEqual(client.user, self.user)
    
    def test_client_str_representation(self):
        """Test the string representation of Client"""
        client = ClientFactory(user=self.user)
        
        self.assertEqual(str(client), client.company_name)
    
    def test_client_full_address_property(self):
        """Test the full_address property returns formatted address"""
        client = ClientFactory(user=self.user, address_line_2='Suite 456')
        
        expected_address = f'{client.address_line_1}, {client.address_line_2}, {client.town}, {client.post_code}'
        self.assertEqual(client.full_address, expected_address)
    
    def test_client_full_address_without_line2(self):
        """Test full_address property when address_line_2 is empty"""
        client = ClientFactory(user=self.user, address_line_2='')
        
        expected_address = f'{client.address_line_1}, {client.town}, {client.post_code}'
        self.assertEqual(client.full_address, expected_address)
    
    def test_client_ordering(self):
        """Test that clients are ordered by company name"""
        # Create clients with specific names to test ordering
        Client.objects.create(
            user=self.user,
            company_name='Zebra Corp',
            contact_person='John Smith',
            email='john@zebra.com',
            address_line_1='123 Test Street',
            town='Test City',
            post_code='TE1 1ST',
            hourly_rate=45.00
        )
        
        Client.objects.create(
            user=self.user,
            company_name='Alpha Corp',
            contact_person='Jane Doe',
            email='jane@alpha.com',
            address_line_1='456 Test Street',
            town='Test City',
            post_code='TE1 1ST',
            hourly_rate=50.00
        )
        
        clients = Client.objects.all()
        self.assertEqual(clients[0].company_name, 'Alpha Corp')
        self.assertEqual(clients[1].company_name, 'Zebra Corp')

class ClientViewsTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create a test client using factory
        self.test_client = ClientFactory(user=self.user)
    
    def test_client_list_requires_login(self):
        """Test that client list view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('clients:client_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_client_list_authenticated(self):
        """Test that authenticated users can view client list"""
        response = self.client.get(reverse('clients:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_client.company_name)
        self.assertContains(response, 'Clients')
    
    def test_client_list_search_functionality(self):
        """Test client search functionality"""
        # Create another client for search testing
        another_client = ClientFactory(user=self.user)
        
        # Search by company name
        response = self.client.get(reverse('clients:client_list'), {'search': self.test_client.company_name})
        self.assertContains(response, self.test_client.company_name)
        self.assertNotContains(response, another_client.company_name)
        
        # Search by contact person
        response = self.client.get(reverse('clients:client_list'), {'search': another_client.contact_person})
        self.assertContains(response, another_client.company_name)
        self.assertNotContains(response, self.test_client.company_name)
    
    def test_client_create_requires_login(self):
        """Test that client create view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('clients:client_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_client_create_authenticated(self):
        """Test that authenticated users can create clients"""
        response = self.client.get(reverse('clients:client_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Client')
    
    def test_client_create_form_submission(self):
        """Test that client can be created via form submission"""
        form_data = {
            'company_name': 'New Company Ltd',
            'contact_person': 'New Person',
            'email': 'new@company.com',
            'phone': '+44 123 456 7890',
            'address_line_1': '789 New Street',
            'address_line_2': 'Floor 2',
            'town': 'New City',
            'post_code': 'NE1 1EW',
            'hourly_rate': 55.00,
        }
        
        response = self.client.post(reverse('clients:client_create'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify the client was created
        new_client = Client.objects.get(company_name='New Company Ltd')
        self.assertEqual(new_client.contact_person, 'New Person')
        self.assertEqual(new_client.email, 'new@company.com')
        self.assertEqual(new_client.hourly_rate, 55.00)
        self.assertEqual(new_client.user, self.user)
    
    def test_client_detail_requires_login(self):
        """Test that client detail view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('clients:client_detail', kwargs={'pk': self.test_client.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_client_detail_authenticated(self):
        """Test that authenticated users can view client details"""
        response = self.client.get(reverse('clients:client_detail', kwargs={'pk': self.test_client.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_client.company_name)
        self.assertContains(response, self.test_client.contact_person)
        self.assertContains(response, f'£{self.test_client.hourly_rate}/h')
    
    def test_client_detail_user_isolation(self):
        """Test that users can only see their own clients"""
        other_user = UserFactory()
        other_client = ClientFactory(user=other_user)
        
        response = self.client.get(reverse('clients:client_detail', kwargs={'pk': other_client.pk}))
        self.assertEqual(response.status_code, 404)  # Should not be accessible
    
    def test_client_update_requires_login(self):
        """Test that client update view requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('clients:client_update', kwargs={'pk': self.test_client.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_client_update_authenticated(self):
        """Test that authenticated users can edit clients"""
        response = self.client.get(reverse('clients:client_update', kwargs={'pk': self.test_client.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Edit Client: {self.test_client.company_name}')
    
    def test_client_update_form_submission(self):
        """Test that client can be updated via form submission"""
        form_data = {
            'company_name': 'Updated Company Ltd',
            'contact_person': 'Updated Person',
            'email': 'updated@company.com',
            'phone': '+44 987 654 3210',
            'address_line_1': '999 Updated Street',
            'town': 'Updated City',
            'post_code': 'UP1 1DA',
            'hourly_rate': 60.00,
        }
        
        response = self.client.post(reverse('clients:client_update', kwargs={'pk': self.test_client.pk}), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Refresh client from database
        self.test_client.refresh_from_db()
        
        # Verify the data was updated
        self.assertEqual(self.test_client.company_name, 'Updated Company Ltd')
        self.assertEqual(self.test_client.contact_person, 'Updated Person')
        self.assertEqual(self.test_client.email, 'updated@company.com')
        self.assertEqual(self.test_client.hourly_rate, 60.00)
    
    def test_client_update_user_isolation(self):
        """Test that users can only edit their own clients"""
        other_user = UserFactory()
        other_client = ClientFactory(user=other_user)
        
        response = self.client.get(reverse('clients:client_update', kwargs={'pk': other_client.pk}))
        self.assertEqual(response.status_code, 404)  # Should not be accessible
