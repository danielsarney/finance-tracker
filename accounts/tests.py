from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from finance_tracker.factories import UserFactory


class CustomUserCreationFormTest(TestCase):
    """Test cases for CustomUserCreationForm."""

    def setUp(self):
        self.factory_user = UserFactory.build()
        self.valid_data = {
            "email": self.factory_user.email,
            "first_name": self.factory_user.first_name,
            "last_name": self.factory_user.last_name,
            "password1": "testpass123",
            "password2": "testpass123",
        }

    def test_form_valid_data(self):
        """Test form with valid data."""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        required_fields = ["email", "first_name", "last_name", "password1", "password2"]

        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            form = CustomUserCreationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_password_mismatch(self):
        """Test form validation when passwords don't match."""
        data = self.valid_data.copy()
        data["password2"] = "differentpassword"
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_duplicate_email(self):
        """Test form validation with duplicate email."""
        # Create a user with the same email first using factory
        UserFactory(email=self.valid_data["email"])

        form = CustomUserCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_save_creates_user(self):
        """Test that form.save() creates a User instance."""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(
            user.username, self.valid_data["email"]
        )  # Username should be set to email
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.last_name, self.valid_data["last_name"])

    def test_form_no_username_field(self):
        """Test that username field is not in the form."""
        form = CustomUserCreationForm()
        self.assertNotIn("username", form.fields)

    def test_form_widget_attributes(self):
        """Test that form fields have correct widget attributes."""
        form = CustomUserCreationForm()

        # Check email field
        self.assertIn("class", form.fields["email"].widget.attrs)
        self.assertEqual(form.fields["email"].widget.attrs["class"], "form-control")

        # Check password fields
        self.assertIn("class", form.fields["password1"].widget.attrs)
        self.assertEqual(form.fields["password1"].widget.attrs["class"], "form-control")

    def test_form_with_factory_generated_data(self):
        """Test form with factory-generated user data."""
        # Use factory to generate realistic test data
        factory_user = UserFactory.build()  # Build but don't save

        test_data = {
            "email": factory_user.email,
            "first_name": factory_user.first_name,
            "last_name": factory_user.last_name,
            "password1": "testpass123",
            "password2": "testpass123",
        }

        form = CustomUserCreationForm(data=test_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.email, factory_user.email)
        self.assertEqual(user.first_name, factory_user.first_name)
        self.assertEqual(user.last_name, factory_user.last_name)


class CustomAuthenticationFormTest(TestCase):
    """Test cases for CustomAuthenticationForm."""

    def setUp(self):
        # Use factory to create a test user
        self.user = UserFactory()
        self.user.set_password("testpass123")
        self.user.save()

        self.valid_data = {"email": self.user.email, "password": "testpass123"}

    def test_form_valid_data(self):
        """Test form with valid data."""
        form = CustomAuthenticationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.user, self.user)

    def test_form_missing_fields(self):
        """Test form validation with missing fields."""
        # Missing email
        data = {"password": "testpass123"}
        form = CustomAuthenticationForm(data=data)
        self.assertFalse(form.is_valid())

        # Missing password
        data = {"email": self.user.email}
        form = CustomAuthenticationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_email(self):
        """Test form validation with invalid email."""
        data = {"email": "nonexistent@example.com", "password": "testpass123"}
        form = CustomAuthenticationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_invalid_password(self):
        """Test form validation with invalid password."""
        data = {"email": self.user.email, "password": "wrongpassword"}
        form = CustomAuthenticationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_widget_attributes(self):
        """Test that form fields have correct widget attributes."""
        form = CustomAuthenticationForm()

        # Check email field
        self.assertIn("class", form.fields["email"].widget.attrs)
        self.assertEqual(form.fields["email"].widget.attrs["class"], "form-control")

        # Check password field
        self.assertIn("class", form.fields["password"].widget.attrs)
        self.assertEqual(form.fields["password"].widget.attrs["class"], "form-control")

    def test_form_with_multiple_users(self):
        """Test form with multiple factory-created users."""
        # Create multiple users with factories
        users = UserFactory.create_batch(3)

        for user in users:
            user.set_password("testpass123")
            user.save()

            data = {"email": user.email, "password": "testpass123"}

            form = CustomAuthenticationForm(data=data)
            self.assertTrue(form.is_valid())
            self.assertEqual(form.user, user)


class AccountsViewsTest(TestCase):
    """Test cases for accounts views."""

    def setUp(self):
        self.client = Client()
        # Use factory to create a test user
        self.user = UserFactory()
        self.user.set_password("testpass123")
        self.user.save()

    def test_register_view_get(self):
        """Test register view GET request."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)


    def test_register_view_post_invalid(self):
        """Test register view POST request with invalid data."""
        data = {
            "email": "invalid-email",
            "first_name": "",
            "last_name": "",
            "password1": "pass",
            "password2": "different",
        }

        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertTemplateUsed(response, "accounts/register.html")

        # Check that form errors are displayed
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())


    def test_login_view_get(self):
        """Test login view GET request."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], CustomAuthenticationForm)


    def test_login_view_post_invalid(self):
        """Test login view POST request with invalid credentials."""
        data = {"email": self.user.email, "password": "wrongpassword"}

        response = self.client.post(reverse("accounts:login"), data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertTemplateUsed(response, "accounts/login.html")

        # Check that form errors are displayed
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())

    def test_logout_view(self):
        """Test logout view."""
        # First login the user
        self.client.login(username=self.user.username, password="testpass123")

        # Then logout
        response = self.client.get(reverse("accounts:logout"))

        # Should redirect to login page
        self.assertRedirects(response, reverse("accounts:login"))

        # Check that user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view_requires_login(self):
        """Test that logout view requires login."""
        response = self.client.get(reverse("accounts:logout"))
        # Should redirect to login page since user is not authenticated
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={reverse('accounts:logout')}"
        )



class AccountsURLsTest(TestCase):
    """Test cases for accounts URLs."""

    def test_register_url(self):
        """Test register URL pattern."""
        url = reverse("accounts:register")
        self.assertEqual(url, "/accounts/register/")

        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "register")
        self.assertEqual(resolver.app_name, "accounts")

    def test_login_url(self):
        """Test login URL pattern."""
        url = reverse("accounts:login")
        self.assertEqual(url, "/accounts/login/")

        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "user_login")
        self.assertEqual(resolver.app_name, "accounts")

    def test_logout_url(self):
        """Test logout URL pattern."""
        url = reverse("accounts:logout")
        self.assertEqual(url, "/accounts/logout/")

        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "user_logout")
        self.assertEqual(resolver.app_name, "accounts")


class AccountsAppConfigTest(TestCase):
    """Test cases for accounts app configuration."""

    def test_app_config(self):
        """Test that the accounts app is properly configured."""
        from django.apps import apps

        app_config = apps.get_app_config("accounts")
        self.assertEqual(app_config.name, "accounts")
        self.assertEqual(app_config.label, "accounts")


class AccountsIntegrationTest(TestCase):
    """Integration tests for accounts functionality using factories."""

    def setUp(self):
        self.client = Client()

