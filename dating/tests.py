"""
Comprehensive test suite for dating app views.
Tests all views in dating/views.py.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Profile


class BaseViewTestCase(TestCase):
    """Base test case with common setUp data"""

    def setUp(self):
        """Create test users and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )


class HomeViewTests(TestCase):
    """Tests for Home template view"""

    def test_home_view_accessible(self):
        """Home page should be accessible to everyone"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_anonymous_user(self):
        """Home page should work for anonymous users"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/index.html')


class ProfileGetStartedTests(TestCase):
    """Tests for ProfileGetStarted view redirects"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_redirect_anonymous_to_signup(self):
        """Unauthenticated users should redirect to signup"""
        url = reverse('profile_getstarted')
        response = self.client.get(url)
        # Assumes allauth signup URL name
        self.assertRedirects(
            response, '/account/signup/', fetch_redirect_response=False
        )

    def test_redirect_no_profile_to_create(self):
        """Users without profile should redirect to profile creation"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_getstarted')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_redirect_with_profile_to_about(self):
        """Users with profile should redirect to profile about"""
        Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_getstarted')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_about'))


class ProfileCreateTests(BaseViewTestCase):
    """Tests for ProfileCreate view"""

    def test_get_create_requires_login(self):
        """Profile creation page requires authentication"""
        url = reverse('profile_create')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_create_authenticated(self):
        """Authenticated users can access profile creation form"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/profile_form.html')

    def test_post_create_profile_success(self):
        """POST with valid data should create profile and redirect"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        data = {
            'age': 25,
            'gender': 'M',
            'location': 'Test City',
            'bio': 'This is a test bio that is long enough for validation',
            'interests': 'Reading, Coding'
        }
        response = self.client.post(url, data)
        # Should redirect to profile detail
        self.assertEqual(response.status_code, 302)
        # Profile should be created
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        # Verify redirect URL contains the profile pk
        self.assertIn(str(profile.pk), response.url)

    def test_post_create_profile_validation_error_age_too_young(self):
        """Age below 18 should fail validation"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        data = {
            'age': 17,
            'gender': 'M',
            'location': 'Test City',
            'bio': 'This is a test bio that is long enough',
            'interests': 'Reading'
        }
        response = self.client.post(url, data)
        # Form re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_post_create_profile_validation_error_age_too_old(self):
        """Age above 99 should fail validation"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        data = {
            'age': 100,
            'gender': 'M',
            'location': 'Test City',
            'bio': 'This is a test bio that is long enough',
            'interests': 'Reading'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_post_create_profile_validation_error_bio_too_short(self):
        """Bio shorter than 10 characters should fail validation"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        data = {
            'age': 25,
            'gender': 'M',
            'location': 'Test City',
            'bio': 'Short',  # Too short
            'interests': 'Reading'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_post_create_profile_already_exists(self):
        """Creating a second profile should show error message"""
        # Create first profile
        Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_create')
        data = {
            'age': 30,
            'gender': 'F',
            'location': 'Another City',
            'bio': 'This is another test bio that is long enough',
            'interests': 'Dancing'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Form re-rendered
        # Should still have only one profile
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)

    def test_form_class_validation(self):
        """Test form validation directly"""
        from .views import ProfileCreate
        view = ProfileCreate()
        form_class = view.get_form_class()

        # Valid form
        valid_data = {
            'age': 25,
            'gender': 'M',
            'location': 'Test City',
            'bio': 'This is a test bio that is long enough',
            'interests': 'Reading, Coding',
        }
        form = form_class(data=valid_data)
        self.assertTrue(form.is_valid())


class ProfileUpdateTests(BaseViewTestCase):
    """Tests for ProfileUpdate view"""

    def setUp(self):
        super().setUp()
        self.profile = Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )

    def test_get_update_requires_login(self):
        """Profile update page requires authentication"""
        url = reverse('profile_update')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_update_authenticated(self):
        """Authenticated users can access profile update form"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_update')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/profile_form.html')

    def test_post_update_profile_success(self):
        """POST with valid data should update profile"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_update')
        data = {
            'age': 30,
            'gender': 'M',
            'location': 'Updated City',
            'bio': 'This is an updated test bio that is long enough',
            'interests': 'Updated Interests'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('profile_about'))
        # Profile should be updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.age, 30)
        self.assertEqual(self.profile.location, 'Updated City')
        # Check success message
        messages = list(response.wsgi_request._messages)
        msg_text = any('successfully updated' in str(m) for m in messages)
        self.assertTrue(msg_text)


class ProfileDeleteTests(BaseViewTestCase):
    """Tests for ProfileDelete view"""

    def setUp(self):
        super().setUp()
        self.profile = Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )

    def test_get_delete_requires_login(self):
        """Profile delete page requires authentication"""
        url = reverse('profile_delete')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_delete_requires_profile(self):
        """Users without profile should redirect to create"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('profile_delete')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_get_delete_authenticated_with_profile(self):
        """Authenticated users with profile can access delete page"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_delete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/profile_delete.html')

    def test_post_delete_profile_success(self):
        """POST should delete profile and redirect to home"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_delete')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('home'))
        # Profile should be deleted
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        # Check success message
        messages = list(response.wsgi_request._messages)
        msg_text = any('successfully deleted' in str(m) for m in messages)
        self.assertTrue(msg_text)


class ProfileDetailTests(BaseViewTestCase):
    """Tests for ProfileDetail view"""

    def setUp(self):
        super().setUp()
        self.profile = Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )

    def test_get_detail_requires_login(self):
        """Profile detail page requires authentication"""
        url = reverse('profile_detail', args=[self.profile.pk])
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_detail_authenticated(self):
        """Authenticated users can view profile detail"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_detail', args=[self.profile.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/profile_detail.html')
        self.assertEqual(response.context['profile'], self.profile)

    def test_get_detail_with_origin_parameter(self):
        """Profile detail should handle origin query parameter"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_detail', args=[self.profile.pk])
        url += '?origin=/connections/discover/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('next_url', response.context)
        expected_url = '/connections/discover/'
        self.assertEqual(response.context['next_url'], expected_url)

    def test_get_detail_with_invalid_origin_parameter(self):
        """Profile detail should default to discover if origin is invalid"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_detail', args=[self.profile.pk])
        url += '?origin=http://evil.com/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('next_url', response.context)
        # Should default to discover, not the evil URL
        expected_url = '/connections/discover/'
        self.assertEqual(response.context['next_url'], expected_url)

    def test_get_detail_nonexistent_profile(self):
        """Accessing non-existent profile should return 404"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProfileAboutTests(BaseViewTestCase):
    """Tests for ProfileAbout view"""

    def setUp(self):
        super().setUp()
        self.profile = Profile.objects.create(
            user=self.user,
            age=25,
            gender='M',
            location='Test City',
            bio='This is a test bio that is long enough',
            interests='Reading'
        )

    def test_get_about_requires_login(self):
        """Profile about page requires authentication"""
        url = reverse('profile_about')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_about_requires_profile(self):
        """Users without profile should redirect to create"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('profile_about')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_get_about_authenticated_with_profile(self):
        """Authenticated users with profile can view their profile"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/profile_detail.html')
        self.assertEqual(response.context['profile'], self.profile)


class AboutViewTests(TestCase):
    """Tests for AboutView template"""

    def test_about_view_accessible(self):
        """About page should be accessible to everyone"""
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/about.html')


class ContactViewTests(TestCase):
    """Tests for ContactView template"""

    def test_contact_view_accessible(self):
        """Contact page should be accessible to everyone"""
        url = reverse('contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dating/contact.html')
