"""
Service functions for connection-related operations
"""
from django.db.models import Q
from dating.models import Profile, Preference
from .models import Like


def get_discoverable_profiles(user, preferences=None, order_by='newest'):
    """
    Get profiles that are discoverable for a user based on their preferences
    and interaction history.

    Args:
        user: The User instance requesting discoverable profiles
        preferences: Optional Preference instance. If None, will try to get
                     from user.preference or use defaults
        order_by: 'newest' (default) or 'random' for ordering

    Returns:
        QuerySet of Profile objects that match the criteria
    """
    # Get or create preferences
    if preferences is None:
        try:
            preferences = user.preference
        except Preference.DoesNotExist:
            # Use default preferences if none exist
            preferences = None

    # Start with all profiles except current user
    queryset = Profile.objects.exclude(user=user)

    # Exclude profiles user has already liked
    liked_user_ids = Like.objects.filter(
        from_user=user,
        action=Like.LIKE
    ).values_list('to_user_id', flat=True)
    queryset = queryset.exclude(user_id__in=liked_user_ids)

    # Exclude profiles user has already passed/disliked
    disliked_user_ids = Like.objects.filter(
        from_user=user,
        action=Like.DISLIKE
    ).values_list('to_user_id', flat=True)
    queryset = queryset.exclude(user_id__in=disliked_user_ids)

    # Apply preference filters if preferences exist
    if preferences:
        # Filter by age range
        queryset = queryset.filter(
            age__gte=preferences.min_age,
            age__lte=preferences.max_age
        )

        # Filter by preferred genders
        preferred_genders = preferences.get_preferred_genders_list()
        if preferred_genders:
            # Build Q object for gender filtering
            gender_q = Q()
            for gender in preferred_genders:
                gender_q |= Q(gender=gender.strip())
            queryset = queryset.filter(gender_q)

    # Apply ordering
    if order_by == 'random':
        queryset = queryset.order_by('?')
    else:  # default to 'newest'
        queryset = queryset.order_by('-createdAt')

    return queryset
