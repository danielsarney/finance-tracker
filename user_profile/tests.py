from django.test import TestCase, Client
from django.urls import reverse
from .models import UserProfile
from finance_tracker.factories import UserFactory

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_user_profile_creation(self):
        """Test that a profile is automatically created when a user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str(self):
        """Test the string representation of UserProfile"""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.profile), expected)

class UserProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.profile = self.user.profile
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('user_profile:profile_view'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test that authenticated users can view their profile"""
        self.client.login(username=self.user.username, password='testpass123')
        response = self.client.get(reverse('user_profile:profile_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Business Profile')
    
    def test_profile_edit_requires_login(self):
        """Test that profile edit view requires authentication"""
        response = self.client.get(reverse('user_profile:profile_edit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_edit_authenticated(self):
        """Test that authenticated users can edit their profile"""
        self.client.login(username=self.user.username, password='testpass123')
        response = self.client.get(reverse('user_profile:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Business Profile')
    
    def test_profile_edit_form_submission(self):
        """Test that profile can be updated via form submission"""
        self.client.login(username=self.user.username, password='testpass123')
        
        # Test data for updating profile
        form_data = {
            'email': 'newemail@example.com',
            'phone': '+44 123 456 7890',
            'address_line_1': '123 New Street',
            'address_line_2': 'Suite 456',
            'town': 'New City',
            'post_code': 'AB12 3CD',
            'bank_name': 'New Bank',
            'account_name': 'New Account Name',
            'account_number': '98765432',
            'sort_code': '98-76-54',
        }
        
        response = self.client.post(reverse('user_profile:profile_edit'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        
        # Verify the data was updated
        self.assertEqual(self.profile.email, 'newemail@example.com')
        self.assertEqual(self.profile.phone, '+44 123 456 7890')
        self.assertEqual(self.profile.address_line_1, '123 New Street')
        self.assertEqual(self.profile.address_line_2, 'Suite 456')
        self.assertEqual(self.profile.town, 'New City')
        self.assertEqual(self.profile.post_code, 'AB12 3CD')
        self.assertEqual(self.profile.bank_name, 'New Bank')
        self.assertEqual(self.profile.account_name, 'New Account Name')
        self.assertEqual(self.profile.account_number, '98765432')
        self.assertEqual(self.profile.sort_code, '98-76-54')
