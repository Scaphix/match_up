"""
Comprehensive test suite for connections app views.
Tests all views in connections/views.py.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

from dating.models import Profile
from .models import Like, Match


class BaseConnectionsTestCase(TestCase):
    """Base test case with common setUp data for connections"""

    def setUp(self):
        """Create test users, profiles, and client"""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )

        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=25,
            gender='M',
            location='City1',
            bio='This is user1 bio that is long enough for validation',
            interests='Reading'
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=27,
            gender='F',
            location='City2',
            bio='This is user2 bio that is long enough for validation',
            interests='Coding'
        )
        self.profile3 = Profile.objects.create(
            user=self.user3,
            age=30,
            gender='M',
            location='City3',
            bio='This is user3 bio that is long enough for validation',
            interests='Gaming'
        )


class DiscoverViewTests(BaseConnectionsTestCase):
    """Tests for DiscoverView"""

    def test_get_discover_requires_login(self):
        """Discover page requires authentication"""
        url = reverse('connections:discover')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_get_discover_requires_profile(self):
        """Users without profile should redirect to create"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_get_discover_with_profile(self):
        """Users with profile can access discover page"""
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connections/discover.html')

    def test_discover_excludes_own_profile(self):
        """Discover should not show user's own profile"""
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        profiles = response.context['profiles']
        self.assertNotIn(self.profile1, profiles)

    def test_discover_excludes_already_liked_profiles(self):
        """Discover should exclude profiles user has already liked"""
        # User1 likes User2
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.LIKE
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        profiles = response.context['profiles']
        self.assertNotIn(self.profile2, profiles)

    def test_discover_excludes_already_passed_profiles(self):
        """Discover should exclude profiles user has passed on"""
        # User1 passes User3
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user3,
            action=Like.DISLIKE
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        profiles = response.context['profiles']
        self.assertNotIn(self.profile3, profiles)

    def test_discover_pagination(self):
        """Discover should support pagination"""
        # Create more profiles to trigger pagination (assuming paginate_by = 3)
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i+4}',
                password='testpass123'
            )
            Profile.objects.create(
                user=user,
                age=25+i,
                gender='M',
                location=f'City{i+4}',
                bio='This is a test bio that is long enough for validation',
                interests='Reading'
            )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should have pagination with 3 profiles per page
        self.assertTrue(
            response.context['is_paginated'] or
            len(response.context['profiles']) <= 3
        )

    def test_discover_shows_available_profiles(self):
        """Discover should show profiles that haven't been interacted with"""
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:discover')
        response = self.client.get(url)
        profiles = response.context['profiles']
        # Should show user2 and user3 (not user1)
        self.assertIn(self.profile2, profiles)
        self.assertIn(self.profile3, profiles)


class LikeProfileViewTests(BaseConnectionsTestCase):
    """Tests for LikeProfileView"""

    def setUp(self):
        super().setUp()
        self.client.login(username='user1', password='testpass123')

    def test_like_requires_login(self):
        """Like endpoint requires authentication"""
        self.client.logout()
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_like_requires_profile(self):
        """User must have profile to like others"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_like_profile_success(self):
        """POST should create a Like record"""
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        # Like should be created
        self.assertTrue(
            Like.objects.filter(
                from_user=self.user1,
                to_user=self.user2,
                action=Like.LIKE
            ).exists()
        )

    def test_like_own_profile_error(self):
        """Users cannot like their own profile"""
        url = reverse('connections:like_profile', args=[self.profile1.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('own profile', data['error'].lower())

    def test_like_already_liked(self):
        """Liking an already liked profile should return success"""
        # Create existing like
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.LIKE
        )
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        # Should still be only one like
        self.assertEqual(
            Like.objects.filter(
                from_user=self.user1,
                to_user=self.user2,
                action=Like.LIKE
            ).count(),
            1
        )

    def test_like_updates_dislike_to_like(self):
        """Liking a previously passed profile should update to like"""
        # Create existing dislike
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.DISLIKE
        )
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Should update to like
        like = Like.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(like.action, Like.LIKE)

    def test_like_creates_match_when_mutual(self):
        """When both users like each other, a match should be created"""
        # User2 already likes User1
        Like.objects.create(
            from_user=self.user2,
            to_user=self.user1,
            action=Like.LIKE
        )
        url = reverse('connections:like_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['is_match'])
        # Match should be created (via signal)
        self.assertTrue(
            Match.objects.filter(
                user1=self.user1, user2=self.user2, is_active=True
            ).exists() or
            Match.objects.filter(
                user1=self.user2, user2=self.user1, is_active=True
            ).exists()
        )

    def test_like_nonexistent_profile(self):
        """Liking non-existent profile should return 404"""
        url = reverse('connections:like_profile', args=[99999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class PassProfileViewTests(BaseConnectionsTestCase):
    """Tests for PassProfileView"""

    def setUp(self):
        super().setUp()
        self.client.login(username='user1', password='testpass123')

    def test_pass_requires_login(self):
        """Pass endpoint requires authentication"""
        self.client.logout()
        url = reverse('connections:pass_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_pass_requires_profile(self):
        """User must have profile to pass on others"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('connections:pass_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_pass_profile_success(self):
        """POST should create a DISLIKE Like record"""
        url = reverse('connections:pass_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        # Dislike should be created
        self.assertTrue(
            Like.objects.filter(
                from_user=self.user1,
                to_user=self.user2,
                action=Like.DISLIKE
            ).exists()
        )

    def test_pass_own_profile_error(self):
        """Users cannot pass on their own profile"""
        url = reverse('connections:pass_profile', args=[self.profile1.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_pass_already_passed(self):
        """Passing an already passed profile should return success"""
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.DISLIKE
        )
        url = reverse('connections:pass_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_pass_updates_like_to_dislike(self):
        """Passing a previously liked profile should update the like"""
        # Create existing like
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.LIKE
        )
        url = reverse('connections:pass_profile', args=[self.profile2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Should update to dislike
        like = Like.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(like.action, Like.DISLIKE)

    def test_pass_nonexistent_profile(self):
        """Passing non-existent profile should return 404"""
        url = reverse('connections:pass_profile', args=[99999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class MatchesListViewTests(BaseConnectionsTestCase):
    """Tests for MatchesListView"""

    def test_matches_requires_login(self):
        """Matches page requires authentication"""
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_matches_requires_profile(self):
        """Users without profile should redirect to create"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_matches_with_profile_no_matches(self):
        """Users with profile but no matches should see empty state"""
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connections/matches.html')

    def test_matches_shows_mutual_matches(self):
        """Matches page should show mutual matches"""
        # Create mutual match
        match = Match.objects.create(
            user1=self.user1,
            user2=self.user2,
            is_active=True
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('match_profiles', response.context)
        # Should show the match
        match_profiles = response.context['match_profiles']
        self.assertEqual(len(match_profiles), 1)
        self.assertEqual(match_profiles[0]['match'], match)
        self.assertEqual(match_profiles[0]['profile'], self.profile2)

    def test_matches_excludes_inactive_matches(self):
        """Matches page should only show active matches"""
        # Create inactive match
        Match.objects.create(
            user1=self.user1,
            user2=self.user2,
            is_active=False
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        match_profiles = response.context['match_profiles']
        self.assertEqual(len(match_profiles), 0)

    def test_matches_shows_both_user1_and_user2_matches(self):
        """Matches should show matches where user is either user1 or user2"""
        # Create match with user1 as user1
        Match.objects.create(
            user1=self.user1,
            user2=self.user2,
            is_active=True
        )
        # Create match with user1 as user2
        Match.objects.create(
            user1=self.user3,
            user2=self.user1,
            is_active=True
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        match_profiles = response.context['match_profiles']
        self.assertEqual(len(match_profiles), 2)

    def test_matches_pagination(self):
        """Matches should support pagination"""
        # Create multiple matches
        for i in range(5):
            user = User.objects.create_user(
                username=f'matchuser{i}',
                password='testpass123'
            )
            Profile.objects.create(
                user=user,
                age=25,
                gender='M',
                location='City',
                bio='This is a test bio that is long enough',
                interests='Reading'
            )
            Match.objects.create(
                user1=self.user1,
                user2=user,
                is_active=True
            )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:matches')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should have pagination (assuming paginate_by = 3)
        self.assertTrue(
            response.context['is_paginated'] or
            len(response.context['match_profiles']) <= 3
        )


class LikedProfilesViewTests(BaseConnectionsTestCase):
    """Tests for LikedProfilesView"""

    def test_liked_profiles_requires_login(self):
        """Liked profiles page requires authentication"""
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        self.assertRedirects(response, '/account/login/?next=' + url)

    def test_liked_profiles_requires_profile(self):
        """Users without profile should redirect to create"""
        User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('profile_create'))

    def test_liked_profiles_with_no_likes(self):
        """Users with no likes should see empty state"""
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connections/liked_profiles.html')

    def test_liked_profiles_shows_liked_profiles(self):
        """Liked profiles page should show profiles user has liked"""
        # User1 likes User2 and User3
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.LIKE
        )
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user3,
            action=Like.LIKE
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        profiles = response.context['profiles']
        self.assertEqual(len(profiles), 2)
        self.assertIn(self.profile2, profiles)
        self.assertIn(self.profile3, profiles)

    def test_liked_profiles_excludes_passed_profiles(self):
        """Liked profiles should not show passed/disliked profiles"""
        # User1 likes User2, passes User3
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action=Like.LIKE
        )
        Like.objects.create(
            from_user=self.user1,
            to_user=self.user3,
            action=Like.DISLIKE
        )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        profiles = response.context['profiles']
        self.assertEqual(len(profiles), 1)
        self.assertIn(self.profile2, profiles)
        self.assertNotIn(self.profile3, profiles)

    def test_liked_profiles_pagination(self):
        """Liked profiles should support pagination"""
        # Create more profiles and likes
        for i in range(5):
            user = User.objects.create_user(
                username=f'likeduser{i}',
                password='testpass123'
            )
            Profile.objects.create(
                user=user,
                age=25,
                gender='M',
                location='City',
                bio='This is a test bio that is long enough',
                interests='Reading'
            )
            Like.objects.create(
                from_user=self.user1,
                to_user=user,
                action=Like.LIKE
            )
        self.client.login(username='user1', password='testpass123')
        url = reverse('connections:liked_profiles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should have pagination (assuming paginate_by = 3)
        self.assertTrue(
            response.context['is_paginated'] or
            len(response.context['profiles']) <= 3
        )
