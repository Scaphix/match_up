"""
Views for connection-related functionality (likes, matches, discovery)
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from dating.models import Profile
from .models import Like, Match
from .services import get_discoverable_profiles


class DiscoverView(LoginRequiredMixin, ListView):
    """
    Display profiles for discovery feed using service function.
    Shows profiles filtered by preferences and excludes already
    interacted profiles.
    """
    model = Profile
    template_name = 'connections/discover.html'
    context_object_name = 'profiles'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        """Check if user has a profile before allowing discovery"""
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile to discover other users.'
            )
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Get discoverable profiles using service function"""
        return get_discoverable_profiles(
            self.request.user,
            order_by='newest'
        )

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Discover'
        return context


class LikeProfileView(LoginRequiredMixin, View):
    """
    Like a profile - creates a Like record with action='like'.
    Automatically creates Match if mutual like exists (via signal).
    """

    def post(self, request, profile_id):
        try:
            # Ensure user has a profile
            if not hasattr(request.user, 'profile'):
                return JsonResponse({
                    'error': 'You must create a profile first.'
                }, status=400)

            target_profile = get_object_or_404(Profile, id=profile_id)

            # Prevent liking yourself
            if target_profile.user == request.user:
                return JsonResponse({
                    'error': 'Cannot like your own profile'
                }, status=400)

            # Check if already liked
            existing_like = Like.objects.filter(
                from_user=request.user,
                to_user=target_profile.user
            ).first()

            if existing_like:
                if existing_like.action == Like.LIKE:
                    return JsonResponse({
                        'success': True,
                        'message': 'Already liked!',
                        'is_match': self._check_match(
                            request.user, target_profile.user
                        )
                    })
                else:
                    # Update dislike to like
                    existing_like.action = Like.LIKE
                    existing_like.save()
            else:
                # Create new like
                Like.objects.create(
                    from_user=request.user,
                    to_user=target_profile.user,
                    action=Like.LIKE
                )

            # Check if match was created (signal should have created it)
            is_match = self._check_match(request.user, target_profile.user)

            match_msg = ' It\'s a match!' if is_match else ''
            return JsonResponse({
                'success': True,
                'message': f'Profile liked!{match_msg}',
                'is_match': is_match
            })

        except IntegrityError:
            return JsonResponse({
                'error': 'You have already interacted with this profile.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)

    def _check_match(self, user1, user2):
        """Check if a match exists between two users"""
        return Match.objects.filter(
            user1=user1, user2=user2, is_active=True
        ).exists() or Match.objects.filter(
            user1=user2, user2=user1, is_active=True
        ).exists()


class PassProfileView(LoginRequiredMixin, View):
    """
    Pass/dislike a profile - creates a Like record with action='dislike'.
    """

    def post(self, request, profile_id):
        try:
            # Ensure user has a profile
            if not hasattr(request.user, 'profile'):
                return JsonResponse({
                    'error': 'You must create a profile first.'
                }, status=400)

            target_profile = get_object_or_404(Profile, id=profile_id)

            # Prevent passing on yourself
            if target_profile.user == request.user:
                return JsonResponse({
                    'error': 'Cannot pass on your own profile'
                }, status=400)

            # Check if already passed
            existing_like = Like.objects.filter(
                from_user=request.user,
                to_user=target_profile.user
            ).first()

            if existing_like:
                if existing_like.action == Like.DISLIKE:
                    return JsonResponse({
                        'success': True,
                        'message': 'Already passed!'
                    })
                else:
                    # Update like to dislike
                    existing_like.action = Like.DISLIKE
                    existing_like.save()
            else:
                # Create new dislike/pass
                Like.objects.create(
                    from_user=request.user,
                    to_user=target_profile.user,
                    action=Like.DISLIKE
                )

            return JsonResponse({
                'success': True,
                'message': 'Profile passed!'
            })

        except IntegrityError:
            return JsonResponse({
                'error': 'You have already interacted with this profile.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class MatchesListView(LoginRequiredMixin, ListView):
    """
    View all active matches for current user.
    Shows profiles of users the current user has matched with.
    """
    model = Match
    template_name = 'connections/matches.html'
    context_object_name = 'matches'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        """Check if user has a profile"""
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile to view matches.'
            )
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Get all active matches for current user"""
        return Match.objects.filter(
            is_active=True
        ).filter(
            user1=self.request.user
        ) | Match.objects.filter(
            is_active=True
        ).filter(
            user2=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add match partner profiles to context"""
        context = super().get_context_data(**kwargs)
        matches = context['matches']

        # Get profiles for each match
        match_profiles = []
        for match in matches:
            other_user = match.get_other_user(self.request.user)
            try:
                profile = other_user.profile
                match_profiles.append({
                    'match': match,
                    'profile': profile
                })
            except Profile.DoesNotExist:
                continue

        context['match_profiles'] = match_profiles
        context['title'] = 'My Matches'
        return context


class LikedProfilesView(LoginRequiredMixin, ListView):
    """
    View all profiles the current user has liked (one-way likes).
    """
    model = Profile
    template_name = 'connections/liked_profiles.html'
    context_object_name = 'profiles'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        """Check if user has a profile"""
        if not hasattr(request.user, 'profile'):
            messages.info(
                request,
                'You must create a profile to view liked profiles.'
            )
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Get profiles user has liked"""
        liked_user_ids = Like.objects.filter(
            from_user=self.request.user,
            action=Like.LIKE
        ).values_list('to_user_id', flat=True)

        return Profile.objects.filter(
            user_id__in=liked_user_ids
        ).order_by('-createdAt')

    def get_context_data(self, **kwargs):
        """Add context"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profiles I Liked'
        return context
